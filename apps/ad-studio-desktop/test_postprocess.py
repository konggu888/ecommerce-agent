import unittest
from pathlib import Path
from unittest import mock

from ad_studio import postprocess


class FocusCropFilterTests(unittest.TestCase):
    def test_process_shot_uses_ai_focus_coordinates_in_crop_filter(self):
        with mock.patch.object(postprocess, "ffmpeg_path", return_value="ffmpeg"), \
             mock.patch.object(postprocess, "best_h264_encoder", return_value="libx264"), \
             mock.patch.object(postprocess, "_run") as run:
            postprocess.process_shot(
                Path("input.mp4"), Path("out.mp4"),
                aspect="9:16", focus_x=0.8, focus_y=0.2,
            )

        command = run.call_args.args[0]
        video_filter = command[command.index("-vf") + 1]
        self.assertIn("crop=1080:1920:x=(iw-1080)*0.800000:y=(ih-1920)*0.200000", video_filter)

    def test_focus_coordinates_are_clamped(self):
        self.assertEqual(postprocess._normalized_focus(-1), 0.0)
        self.assertEqual(postprocess._normalized_focus(2), 1.0)

    def test_non_finite_or_invalid_focus_falls_back_to_center(self):
        for value in (float("nan"), float("inf"), float("-inf"), "not-a-number", None):
            with self.subTest(value=value):
                self.assertEqual(postprocess._normalized_focus(value), 0.5)

    def test_default_focus_keeps_center_crop(self):
        value = postprocess._focus_crop_filter(1080, 1920, 0.5, 0.5)
        self.assertIn("x=(iw-1080)*0.500000:y=(ih-1920)*0.500000", value)


if __name__ == "__main__":
    unittest.main()
