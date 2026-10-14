import unittest
from pathlib import Path
from unittest import mock

from ad_studio import ffmpeg


class FinalTransitionTests(unittest.TestCase):
    def test_crossfade_builds_video_and_audio_overlap_filters(self):
        with mock.patch.object(ffmpeg, "which", side_effect=lambda name: "/usr/bin/" + name), \
             mock.patch.object(ffmpeg, "_probe_clip", side_effect=[(3.0, True), (4.0, False), (2.0, True)]), \
             mock.patch.object(ffmpeg, "best_h264_encoder", return_value="libx264"), \
             mock.patch.object(ffmpeg.subprocess, "run") as run:
            ffmpeg.concat_with_transitions(
                [Path("a.mp4"), Path("b.mp4"), Path("c.mp4")],
                Path("final.mp4"), ["硬切", "交叉溶解", "硬切"], aspect="9:16",
            )
        command = run.call_args.args[0]
        graph = command[command.index("-filter_complex") + 1]
        self.assertIn("xfade=transition=fade:duration=0.350000:offset=2.650000", graph)
        self.assertIn("acrossfade=d=0.350000", graph)
        self.assertIn("xfade=transition=fade:duration=0.001000", graph)
        self.assertIn("anullsrc=channel_layout=stereo:sample_rate=48000", graph)
        self.assertIn("crop=1080:1920", graph)
        self.assertEqual(command[-1], "final.mp4")

    def test_crossfade_rejects_mismatched_transition_count(self):
        with mock.patch.object(ffmpeg, "which", return_value="/usr/bin/ffmpeg"):
            with self.assertRaisesRegex(ValueError, "数量不一致"):
                ffmpeg.concat_with_transitions([Path("a.mp4"), Path("b.mp4")], Path("final.mp4"), ["硬切"])

    def test_final_builder_uses_crossfade_only_when_requested(self):
        source = Path(__file__).with_name("ad_studio") / "production.py"
        text = source.read_text(encoding="utf-8")
        self.assertIn("if any(value == '交叉溶解' for value in shot_transitions[1:]):", text)
        self.assertIn("concat_with_transitions(shot_paths, concat_path, shot_transitions, aspect=aspect)", text)


if __name__ == "__main__":
    unittest.main()
