import tempfile
import unittest
from pathlib import Path

from ad_studio.subtitles import analyze_subtitle_density, parse_srt_cues, plan_subtitle_timing, write_srt


class AdaptiveSubtitleTimingTests(unittest.TestCase):
    def test_short_caption_spans_actual_clip_duration(self):
        plan = plan_subtitle_timing("产品很好用。", duration=5.2)
        self.assertEqual(plan["segment_count"], 1)
        self.assertAlmostEqual(plan["segments"][0]["start"], 0)
        self.assertAlmostEqual(plan["segments"][0]["end"], 5.2)

    def test_long_caption_is_split_and_timed_across_clip(self):
        text = "先看细节，再看功能；最后展示实际使用效果！"
        plan = plan_subtitle_timing(text, duration=4.0, max_chars=10)
        self.assertGreater(plan["segment_count"], 1)
        self.assertAlmostEqual(plan["segments"][0]["start"], 0)
        self.assertAlmostEqual(plan["segments"][-1]["end"], 4.0)
        self.assertEqual("".join(row["text"] for row in plan["segments"]).replace(" ", ""), text)

    def test_short_shot_reduces_caption_switching_and_reports_density(self):
        text = "这是一个信息量很大但是只有很短时间展示的超长商品功能介绍字幕内容"
        report = analyze_subtitle_density(text, duration=1.0, max_chars=6)
        self.assertLessEqual(report["segment_count"], 1)
        self.assertGreater(report["effective_max_chars"], 6)
        self.assertTrue(report["warnings"])

    def test_high_density_warning_does_not_rewrite_caption_words(self):
        text = "十秒内容塞进一秒"
        plan = plan_subtitle_timing(text, duration=0.5)
        self.assertEqual("".join(row["text"] for row in plan["segments"]), text)
        self.assertTrue(any("字/秒" in warning for warning in plan["warnings"]))

    def test_write_srt_writes_multiple_timestamped_cues(self):
        with tempfile.TemporaryDirectory() as folder:
            path = write_srt("第一段内容，第二段内容。第三段内容！", Path(folder) / "captions.srt", duration=3, max_chars=7)
            content = path.read_text(encoding="utf-8")
        self.assertIn("00:00:00,000 --> 00:00:01,000", content)
        self.assertIn("00:00:02,000 --> 00:00:03,000", content)
        self.assertIn("第二段", content)


if __name__ == "__main__":
    unittest.main()


class ParseSrtCueWindowTests(unittest.TestCase):
    def test_parses_single_and_multiple_real_cue_windows(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "real.srt"
            path.write_text("1\n00:00:00,000 --> 00:00:01,000\n第一条\n\n2\n00:00:01,000 --> 00:00:03,000\n第二条\n", encoding="utf-8")
            result = parse_srt_cues(path, duration=3.0)
        self.assertEqual(result["cue_count"], 2)
        self.assertEqual(result["cues"][0]["start"], 0.0)
        self.assertEqual(result["cues"][1]["duration"], 2.0)

    def test_accepts_dot_timestamp_fraction(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "decimal.srt"
            path.write_text("1\n00:00:00.000 --> 00:00:02.000\n字幕\n", encoding="utf-8")
            self.assertEqual(parse_srt_cues(path, duration=2.0)["cue_count"], 1)

    def test_rejects_out_of_range_and_mismatched_timeline(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "late.srt"
            path.write_text("1\n00:00:01,000 --> 00:00:04,000\n字幕\n", encoding="utf-8")
            with self.assertRaises(ValueError): parse_srt_cues(path, duration=3.0)

    def test_rejects_malformed_empty_and_missing_srt(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "broken.srt"
            path.write_text("not a valid cue", encoding="utf-8")
            with self.assertRaises(ValueError): parse_srt_cues(path, duration=2.0)
            path.write_text("", encoding="utf-8")
            with self.assertRaises(ValueError): parse_srt_cues(path, duration=2.0)
            with self.assertRaises(ValueError): parse_srt_cues(Path(folder) / "missing.srt", duration=2.0)


if __name__ == "__main__":
    unittest.main()
