import tempfile
import unittest
from pathlib import Path

from ad_studio.subtitles import analyze_subtitle_density, plan_subtitle_timing, write_srt


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
