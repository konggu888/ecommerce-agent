# A109 legacy audio compatibility
# Older shot files may already contain baked-in per-shot BGM; use clean source clips before global mixing.
import unittest
from unittest import mock
from pathlib import Path
from ad_studio import music_sync


class BeatDetectionTests(unittest.TestCase):
    def test_detects_regular_synthetic_clicks(self):
        rate=11025; samples=[0]*(rate*4)
        for t in (0.5,1.0,1.5,2.0,2.5,3.0):
            start=int(t*rate); samples[start:start+80]=[18000]*80
        result=music_sync.detect_beats(samples,rate)
        self.assertGreaterEqual(len(result["beats"]),4)
        self.assertGreaterEqual(result["confidence"],0.45)
        self.assertAlmostEqual(result["bpm"],120.0,delta=12.0)

    def test_silence_has_no_confident_beats(self):
        result=music_sync.detect_beats([0]*22050,11025)
        self.assertEqual(result["beats"],[]); self.assertEqual(result["confidence"],0.0)

    def test_low_confidence_preserves_original_timing(self):
        durations=[2.0,2.0,2.0]
        plan=music_sync.plan_beat_aligned_durations(durations,[2.1,4.1],0.2)
        self.assertEqual(plan["durations"],durations); self.assertFalse(plan["changed"])

    def test_safe_beat_snap_changes_real_shot_durations(self):
        plan=music_sync.plan_beat_aligned_durations([2.0,2.0,2.0],[2.1,4.1],0.95)
        self.assertTrue(plan["changed"])
        self.assertAlmostEqual(plan["durations"][0],2.1,places=6)
        self.assertAlmostEqual(plan["durations"][1],2.0,places=6)
        self.assertAlmostEqual(plan["durations"][2],1.9,places=6)

    def test_over_adjustment_and_too_short_shot_fall_back(self):
        self.assertFalse(music_sync.plan_beat_aligned_durations([2.0,2.0],[2.24],0.95,max_shot_delta=0.1)["changed"])
        self.assertFalse(music_sync.plan_beat_aligned_durations([0.9,0.9],[0.1],0.95,min_duration=0.8)["changed"])

    def test_content_protection_estimates_dialogue_text_and_product_hold(self):
        result = music_sync.derive_content_minimum_durations([
            {"dialogue": "这款产品操作简单，适合日常使用"},
            {"objective": "商品细节展示", "editing_intent": {"role": "product_detail"}},
            {"on_screen_text": ["立即咨询，了解更多"]},
        ], [5.0, 3.0, 3.0])
        self.assertGreater(result["minimum_durations"][0], 3.0)
        self.assertEqual(result["minimum_durations"][1], 2.0)
        self.assertGreater(result["minimum_durations"][2], 2.0)
        self.assertIn("非视觉识别", result["shots"][0]["basis"])

    def test_beat_snap_preserves_dialogue_and_product_holds(self):
        protection = music_sync.derive_content_minimum_durations([
            {"objective": "商品细节展示", "editing_intent": {"role": "product_detail"}}, {}, {}
        ], [2.0, 2.0, 2.0])
        plan = music_sync.plan_beat_aligned_durations(
            [2.0, 2.0, 2.0], [1.9, 4.1], 0.95,
            minimum_durations=protection["minimum_durations"])
        self.assertTrue(plan["changed"])
        self.assertAlmostEqual(plan["durations"][0], 2.0, places=6)
        self.assertAlmostEqual(plan["durations"][1], 2.1, places=6)
        self.assertAlmostEqual(plan["durations"][2], 1.9, places=6)
        self.assertIn(1, plan["reverted_boundaries"])

    def test_underlength_dialogue_prevents_music_retiming(self):
        protection = music_sync.derive_content_minimum_durations([
            {"dialogue": "这段口播包含较多必须听清楚的商品说明信息"}, {}, {}
        ], [2.0, 2.0, 2.0])
        plan = music_sync.plan_beat_aligned_durations(
            [2.0, 2.0, 2.0], [2.1, 4.1], 0.95,
            minimum_durations=protection["minimum_durations"])
        self.assertTrue(plan["changed"])
        self.assertGreaterEqual(plan["durations"][0], 2.0)
        self.assertAlmostEqual(sum(plan["durations"]), 6.0, places=6)
        self.assertIn("reverted_boundaries", plan)

    def test_local_beat_planning_keeps_safe_unrelated_boundary(self):
        plan = music_sync.plan_beat_aligned_durations(
            [2.0, 2.0, 2.0, 2.0], [2.2, 4.1, 6.1], 0.95,
            minimum_durations=[0.8, 2.2, 0.8, 0.8])
        self.assertTrue(plan["changed"])
        self.assertAlmostEqual(plan["durations"][0], 2.0, places=6)
        self.assertAlmostEqual(plan["durations"][1], 2.0, places=6)
        self.assertAlmostEqual(plan["durations"][2], 2.1, places=6)
        self.assertAlmostEqual(plan["durations"][3], 1.9, places=6)
        self.assertIn(3, plan["adjusted_boundaries"])
        self.assertTrue(plan["reverted_boundaries"])
        self.assertIn("局部", plan["reason"])

    def test_multiple_protected_neighbors_revert_only_conflicting_boundaries(self):
        plan = music_sync.plan_beat_aligned_durations(
            [2.0, 2.0, 2.0, 2.0, 2.0], [2.2, 4.0, 6.1, 8.1], 0.95,
            minimum_durations=[2.2, 2.2, 2.2, 0.8, 0.8])
        self.assertEqual(plan["durations"][0], 2.0)
        self.assertEqual(plan["durations"][1], 2.0)
        self.assertAlmostEqual(plan["durations"][2], 2.1, places=6)
        self.assertTrue(plan["changed"])
        self.assertTrue(plan["reverted_boundaries"])
        self.assertAlmostEqual(sum(plan["durations"]), 10.0, places=6)

    def test_low_confidence_and_crossfade_still_fall_back(self):
        original = [2.0, 2.0, 2.0]
        low = music_sync.plan_beat_aligned_durations(original, [2.1, 4.1], 0.2)
        crossfade = music_sync.plan_beat_aligned_durations(original, [2.1, 4.1], 0.95, allow_retime=False)
        self.assertEqual(low["durations"], original)
        self.assertEqual(crossfade["durations"], original)
        self.assertFalse(low["changed"])
        self.assertFalse(crossfade["changed"])

    def test_crossfade_boundary_plan_falls_back_without_retiming(self):
        plan=music_sync.plan_beat_aligned_durations(
            [2.0,2.0,2.0],[2.1,4.1],0.95,allow_retime=False
        )
        self.assertFalse(plan["changed"])
        self.assertEqual(plan["durations"],[2.0,2.0,2.0])
        self.assertIn("交叉溶解",plan["reason"])

    def test_invalid_duration_and_extreme_speed_are_rejected(self):
        self.assertFalse(music_sync.plan_beat_aligned_durations([2.0,float("nan")],[2.0],0.95)["changed"])
        with self.assertRaises(ValueError): music_sync.retime_clip(Path("in.mp4"),Path("out.mp4"),1.5)

    def test_retime_command_keeps_audio_synced(self):
        with mock.patch.object(music_sync,"_has_audio",return_value=True), mock.patch.object(music_sync.subprocess,"run") as run:
            music_sync.retime_clip(Path("in.mp4"),Path("out.mp4"),1.1)
        command=run.call_args.args[0]
        self.assertIn("setpts=0.90909091*PTS",command)
        self.assertIn("atempo=1.100000",command)
        self.assertEqual(command[-1],"out.mp4")

    def test_global_bgm_uses_one_continuous_track_after_assembly(self):
        with mock.patch.object(music_sync,"_has_audio",return_value=True), \
             mock.patch.object(Path,"is_file",return_value=True), \
             mock.patch.object(music_sync.subprocess,"run") as run:
            music_sync.mix_global_bgm(Path("assembled.mp4"),Path("music.mp3"),Path("mixed.mp4"),0.2)
        command=run.call_args.args[0]
        self.assertIn("-stream_loop",command)
        self.assertIn("amix=inputs=2:duration=first",command[command.index("-filter_complex")+1])
        self.assertEqual(command[-1],"mixed.mp4")


if __name__=="__main__": unittest.main()
