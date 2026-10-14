import unittest
from pathlib import Path
from unittest import mock

from ad_studio import postprocess


class FocusCropFilterTests(unittest.TestCase):
    def test_process_shot_uses_ai_focal_point_to_position_crop_window(self):
        with mock.patch.object(postprocess, "ffmpeg_path", return_value="ffmpeg"), \
             mock.patch.object(postprocess, "best_h264_encoder", return_value="libx264"), \
             mock.patch.object(postprocess, "_run") as run:
            postprocess.process_shot(
                Path("input.mp4"), Path("out.mp4"),
                aspect="9:16", focus_x=0.8, focus_y=0.2,
            )

        command = run.call_args.args[0]
        video_filter = command[command.index("-vf") + 1]
        self.assertIn("crop=1080:1920:x='max(0,min(iw-1080,iw*0.800000-1080/2))':y='max(0,min(ih-1920,ih*0.200000-1920/2))'", video_filter)

    def test_focus_coordinates_are_clamped(self):
        self.assertEqual(postprocess._normalized_focus(-1), 0.0)
        self.assertEqual(postprocess._normalized_focus(2), 1.0)

    def test_non_finite_or_invalid_focus_falls_back_to_center(self):
        for value in (float("nan"), float("inf"), float("-inf"), "not-a-number", None):
            with self.subTest(value=value):
                self.assertEqual(postprocess._normalized_focus(value), 0.5)

    def test_default_focus_keeps_center_crop(self):
        value = postprocess._focus_crop_filter(1080, 1920, 0.5, 0.5)
        self.assertIn("iw*0.500000-1080/2", value)
        self.assertIn("ih*0.500000-1920/2", value)

    def test_off_center_focus_moves_crop_toward_focal_point(self):
        value = postprocess._focus_crop_filter(1080, 1920, 0.8, 0.2)
        self.assertIn("iw*0.800000-1080/2", value)
        self.assertIn("ih*0.200000-1920/2", value)
        self.assertIn("max(0,min(iw-1080,", value)
        self.assertIn("max(0,min(ih-1920,", value)

    def test_fade_out_happens_at_end_after_speed_change(self):
        with mock.patch.object(postprocess, "ffmpeg_path", return_value="ffmpeg"), \
             mock.patch.object(postprocess, "best_h264_encoder", return_value="libx264"), \
             mock.patch.object(postprocess, "probe_duration", return_value=4.0), \
             mock.patch.object(postprocess, "_run") as run:
            postprocess.process_shot(
                Path("input.mp4"), Path("out.mp4"),
                aspect="9:16", speed=2.0, transition="淡出",
            )

        command = run.call_args.args[0]
        video_filter = command[command.index("-vf") + 1]
        # Four input seconds at 2x speed yields a two-second output;
        # the 250ms fade therefore starts at 1.750s, not at time zero.
        self.assertIn("setpts=0.5*PTS", video_filter)
        self.assertIn("fade=t=out:st=1.750:d=0.250", video_filter)

    def test_short_clip_fade_out_does_not_exceed_clip_duration(self):
        with mock.patch.object(postprocess, "ffmpeg_path", return_value="ffmpeg"), \
             mock.patch.object(postprocess, "best_h264_encoder", return_value="libx264"), \
             mock.patch.object(postprocess, "probe_duration", return_value=0.1), \
             mock.patch.object(postprocess, "_run") as run:
            postprocess.process_shot(
                Path("input.mp4"), Path("out.mp4"),
                aspect="9:16", transition="淡出",
            )

        command = run.call_args.args[0]
        video_filter = command[command.index("-vf") + 1]
        self.assertIn("fade=t=out:st=0.000:d=0.100", video_filter)


if __name__ == "__main__":
    unittest.main()
