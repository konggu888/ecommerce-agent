"""用户拍摄素材剪辑（footage）单元测试。

覆盖：素材扫描/探测、本地裁剪命令、剪辑方案校验、
plan_footage（FakeRouter 路由验证）、render_footage_shot（本地裁剪出片）。
不依赖真实 FFmpeg：探测与裁剪均通过 mock 注入。
"""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ad_studio.models import Project, Shot
from ad_studio.production import ProductionStore
from ad_studio.model_router import FUNCTIONS, ModelRouter
from ad_studio.footage import (
    FootageClip,
    FootageError,
    probe_clip,
    scan_footage,
    trim_clip,
    validate_footage_plan,
    archive_analyzed_waste,
    normalize_footage_analysis,
    rank_footage_analysis,
    audit_footage_coverage,
    audit_final_footage_plan,
    classify_footage_gaps,
    build_footage_gap_tasks,
)

from ad_studio import footage as footage_module


def fake_completed(stdout: str = "", stderr: str = "", returncode: int = 0):
    return subprocess.CompletedProcess(
        args=[], returncode=returncode, stdout=stdout, stderr=stderr
    )


class ProbeClipTests(unittest.TestCase):
    def test_ffprobe_missing_raises(self):
        with mock.patch.object(footage_module, "which", return_value=None):
            with self.assertRaises(FootageError):
                probe_clip(Path("clip.mp4"))

    def test_returns_duration_resolution_fps(self):
        payload = json.dumps({
            "format": {"duration": "12.5"},
            "streams": [{"width": 1080, "height": 1920, "r_frame_rate": "30000/1001"}],
        })
        with mock.patch.object(footage_module, "which", return_value="/usr/bin/ffprobe"), \
             mock.patch.object(footage_module.subprocess, "run",
                               return_value=fake_completed(stdout=payload)):
            info = probe_clip(Path("clip.mp4"))
        self.assertEqual(info["duration"], 12.5)
        self.assertEqual((info["width"], info["height"]), (1080, 1920))
        self.assertAlmostEqual(info["fps"], 30000 / 1001, places=3)

    def test_ffprobe_failure_raises(self):
        with mock.patch.object(footage_module, "which", return_value="/usr/bin/ffprobe"), \
             mock.patch.object(footage_module.subprocess, "run",
                               return_value=fake_completed(stderr="boom", returncode=1)):
            with self.assertRaises(FootageError):
                probe_clip(Path("bad.mp4"))


class ScanFootageTests(unittest.TestCase):
    def test_missing_folder_raises(self):
        with self.assertRaises(FootageError):
            scan_footage(Path("/no/such/folder-xyz"))

    def test_lists_sorted_video_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "b.mp4").write_bytes(b"x")
            (folder / "a.MOV").write_bytes(b"x")
            (folder / "note.txt").write_text("not video", encoding="utf-8")

            def fake_probe(path):
                return {"duration": 3.0, "width": 640, "height": 480, "fps": 30.0}

            with mock.patch.object(footage_module, "probe_clip", side_effect=fake_probe):
                clips = scan_footage(folder)
        self.assertEqual([c.name for c in clips], ["a.MOV", "b.mp4"])
        self.assertEqual(clips[0].duration, 3.0)
        self.assertEqual(clips[0].width, 640)

    def test_unparsable_file_gets_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "bad.mp4").write_bytes(b"x")
            with mock.patch.object(footage_module, "probe_clip",
                                   side_effect=FootageError("解析失败")):
                clips = scan_footage(folder)
        self.assertEqual(len(clips), 1)
        self.assertEqual(clips[0].duration, 0.0)
        self.assertIn("解析失败", clips[0].note)



class NormalizeFootageAnalysisTests(unittest.TestCase):
    def test_ranks_usable_materials_and_penalizes_duplicate(self):
        raw = {"clips": [
            {"source": "repeat.mp4", "score": 95, "usable": True, "duplicate_group": "正面", "duplicate_confidence": 0.9, "best_take": False, "speech_quality": "filler", "visual_tags": ["product_visible"]},
            {"source": "best.mp4", "score": 88, "usable": True, "duplicate_group": "正面", "duplicate_confidence": 0.9, "best_take": True, "speech_quality": "clear", "visual_tags": ["product_visible", "detail"]},
            {"source": "bad.mp4", "score": 99, "usable": False},
        ]}
        result = rank_footage_analysis(raw)
        self.assertEqual(result["clips"][1]["material_rank"], 1)
        self.assertEqual(result["clips"][0]["material_rank"], 2)
        self.assertEqual(result["clips"][2]["material_rank"], 0)
        self.assertGreater(result["clips"][1]["selection_score"], result["clips"][0]["selection_score"])


    def test_marks_best_take_in_duplicate_group(self):
        raw = {"clips": [
            {"source": "a.mp4", "score": 72, "duplicate_group": "展示正面", "take_rank": 2},
            {"source": "b.mp4", "score": 91, "duplicate_group": "展示正面", "take_rank": 1},
        ]}
        result = normalize_footage_analysis(raw)
        self.assertTrue(result["clips"][1]["best_take"])
        self.assertFalse(result["clips"][0]["best_take"])

    def test_explicit_best_take_is_preserved(self):
        raw = {"clips": [
            {"source": "a.mp4", "score": 99, "duplicate_group": "开箱", "best_take": False},
            {"source": "b.mp4", "score": 60, "duplicate_group": "开箱", "best_take": True},
        ]}
        result = normalize_footage_analysis(raw)
        self.assertTrue(result["clips"][1]["best_take"])
        self.assertFalse(result["clips"][0]["best_take"])

    def test_normalizes_duplicate_confidence(self):
        result = normalize_footage_analysis({"clips": [{"source": "a.mp4", "duplicate_confidence": 8}]})
        self.assertEqual(result["clips"][0]["duplicate_confidence"], 1.0)

    def test_coverage_maps_selling_points_across_ranked_pool(self):
        analysis = {"clips": [
            {"source": "rank1.mp4", "score": 98, "usable": True, "material_rank": 1, "selection_score": 98, "selling_points": ["外观"], "visual_tags": ["product_visible"]},
            {"source": "rank2.mp4", "score": 78, "usable": True, "material_rank": 2, "selection_score": 78, "selling_points": ["续航"], "visual_tags": ["demo"]},
        ]}
        result = audit_footage_coverage(analysis, {"selling_points": ["外观", "续航"], "shots": []})
        points = {x["name"]: x for x in result["selling_points"]}
        self.assertEqual(points["外观"]["best_source"], "rank1.mp4")
        self.assertEqual(points["续航"]["best_source"], "rank2.mp4")
        self.assertEqual(result["coverage_score"], 100.0)



    def test_classify_footage_gaps_prefers_reshoot_for_product_evidence(self):
        coverage={"missing_key_shots":[{"need":"商品细节特写","reason":"没有可验证的商品细节"}],"missing_selling_points":["防水"]}
        result=classify_footage_gaps(coverage, {}, generation_connected=False)
        self.assertEqual(result["key_shot_gaps"][0]["action"],"待补拍")
        self.assertEqual(result["selling_point_gaps"][0]["action"],"待补拍")

    def test_build_footage_gap_tasks_creates_actionable_reshoot_tasks(self):
        coverage={"coverage_score":50}
        gaps={
            "generation_connected":False,
            "key_shot_gaps":[{"need":"商品细节","reason":"缺少细节证据","action":"待补拍","why":"需要真实商品证据"}],
            "selling_point_gaps":[{"name":"防水","why":"没有实拍证据","action":"待补拍"}],
        }
        result=build_footage_gap_tasks(coverage,gaps,{})
        self.assertEqual(result["task_count"],2)
        self.assertEqual(result["tasks"][0]["type"],"待补拍")
        self.assertIn("商品细节",result["tasks"][0]["need"])
        self.assertIn("防水",result["tasks"][1]["related_selling_point"])
        self.assertTrue(result["tasks"][0]["acceptance"])

    def test_build_footage_gap_tasks_supports_generation_only_when_flagged(self):
        coverage={"coverage_score":80}
        gaps={
            "generation_connected":True,
            "key_shot_gaps":[{"need":"氛围镜头","reason":"缺少辅助画面","action":"待生成","why":"生成链已接通"}],
        }
        result=build_footage_gap_tasks(coverage,gaps,{})
        self.assertEqual(result["tasks"][0]["type"],"待生成")

    def test_classify_footage_gaps_keeps_raw_missing_selling_points(self):
        coverage={"missing_selling_points":["防水","静音"]}
        result=classify_footage_gaps(coverage, {}, generation_connected=False)
        self.assertEqual([x["name"] for x in result["selling_point_gaps"]], ["防水","静音"])
        self.assertEqual(result["gap_count"], 2)

    def test_final_plan_audit_marks_uncovered_selling_point(self):
        analysis={"clips":[
            {"source":"a.mp4","material_rank":1,"selection_score":100,"duplicate_group":"g1","best_take":True},
            {"source":"b.mp4","material_rank":2,"selection_score":90,"duplicate_group":"g1","best_take":False},
        ]}
        coverage={"opening_candidate":"a.mp4","selling_points":[
            {"name":"续航","covered":True,"best_source":"a.mp4"},
            {"name":"静音","covered":True,"best_source":"b.mp4"},
        ]}
        result=audit_final_footage_plan(
            [{"source":"a.mp4","objective":"展示续航"}], analysis, coverage
        )
        self.assertTrue(result["opening_used"])
        self.assertEqual(result["missing_selling_points"],["静音"])
        self.assertEqual(result["plan"][0]["material_rank"],1)

    def test_coverage_detects_missing_required_shot_and_opening(self):
        analysis = {"clips": [{"source": "detail.mp4", "score": 90, "usable": True, "material_rank": 1, "selection_score": 90, "selling_points": ["材质"], "visual_tags": ["product_visible", "detail"]}]}
        result = audit_footage_coverage(analysis, {"selling_points": ["材质"], "shots": [{"objective": "真人使用场景"}, {"objective": "商品特写"}]})
        self.assertEqual(result["opening_candidate"], "detail.mp4")
        self.assertEqual(result["coverage_score"], 100.0)
        self.assertTrue(any(x["need"] == "真人/场景" for x in result["missing_key_shots"]))


class ArchiveWasteTests(unittest.TestCase):
    def test_archives_ai_rejected_and_unparsable_but_keeps_good(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/'素材'; src.mkdir(); archive=root/'05_废片库'
            bad=src/'bad.mp4'; bad.write_bytes(b'bad')
            rejected=src/'reject.mp4'; rejected.write_bytes(b'reject')
            good=src/'good.mp4'; good.write_bytes(b'good')
            clips=[
                FootageClip('bad.mp4',str(bad),0,0,0,0,'解析失败'),
                FootageClip('reject.mp4',str(rejected),5,1080,1920,30),
                FootageClip('good.mp4',str(good),5,1080,1920,30),
            ]
            analysis={'clips':[{'source':'reject.mp4','usable':False,'score':12,'reason':'严重遮挡','visual_tags':['blocked']}, {'source':'good.mp4','usable':True,'score':88}]}
            kept,records=archive_analyzed_waste(clips,analysis,archive,'p1')
            self.assertEqual([x.name for x in kept],['good.mp4'])
            self.assertFalse(bad.exists()); self.assertFalse(rejected.exists()); self.assertTrue(good.exists())
            self.assertEqual(sum(1 for x in records if x['archived']),2)
            self.assertTrue((archive/'p1'/'archive-manifest.json').exists())


class TrimClipTests(unittest.TestCase):
    def test_missing_source_raises(self):
        with self.assertRaises(FootageError):
            trim_clip(Path("/no/such.mp4"), Path("/tmp/out.mp4"))

    def test_builds_ffmpeg_command_and_returns_out(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.mp4"
            src.write_bytes(b"x")
            out = Path(tmp) / "out" / "v1.mp4"
            captured = {}

            def fake_run(cmd, **kwargs):
                captured["cmd"] = cmd
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(b"video")
                return fake_completed()

            with mock.patch.object(footage_module, "which", return_value="/usr/bin/ffmpeg"), \
                 mock.patch.object(footage_module, "best_h264_encoder", return_value="libx264"), \
                 mock.patch.object(footage_module.subprocess, "run", side_effect=fake_run):
                result = trim_clip(src, out, start=1.5, duration=3.0)
                self.assertEqual(result, out)
                self.assertTrue(out.exists())
        cmd = captured["cmd"]
        self.assertIn("-ss", cmd)
        self.assertIn("1.500", cmd)
        self.assertIn("-t", cmd)
        self.assertIn("3.000", cmd)
        self.assertIn("-c:v", cmd)
        self.assertIn("libx264", cmd)
        self.assertIn("-an", cmd)

    def test_without_duration_omits_t(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.mp4"
            src.write_bytes(b"x")
            out = Path(tmp) / "out.mp4"
            captured = {}

            def fake_run(cmd, **kwargs):
                captured["cmd"] = cmd
                return fake_completed()

            with mock.patch.object(footage_module, "which", return_value="/usr/bin/ffmpeg"), \
                 mock.patch.object(footage_module, "best_h264_encoder", return_value="libx264"), \
                 mock.patch.object(footage_module.subprocess, "run", side_effect=fake_run):
                trim_clip(src, out, start=0.0)
        self.assertNotIn("-t", captured["cmd"])


def sample_clips():
    return [
        FootageClip(name="a.mp4", path="/x/a.mp4", duration=10.0,
                    width=1080, height=1920, fps=30.0),
        FootageClip(name="b.mp4", path="/x/b.mp4", duration=5.0,
                    width=720, height=1280, fps=30.0),
    ]


class ValidateFootagePlanTests(unittest.TestCase):
    def test_empty_plan_raises(self):
        with self.assertRaises(FootageError):
            validate_footage_plan([], sample_clips())

    def test_valid_plan_passes(self):
        raw = [{"index": 1, "source": "a.mp4", "start": 0.5, "duration": 3.0,
                "visual": "开场"}]
        items, warnings = validate_footage_plan(raw, sample_clips())
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["source"], "a.mp4")
        self.assertEqual(items[0]["start"], 0.5)
        self.assertEqual(items[0]["duration"], 3.0)
        self.assertEqual(warnings, [])

    def test_missing_source_raises(self):
        raw = [{"index": 1, "source": "nope.mp4", "start": 0, "duration": 3}]
        with self.assertRaises(FootageError):
            validate_footage_plan(raw, sample_clips())

    def test_truncates_overlong_duration_with_warning(self):
        raw = [{"index": 1, "source": "a.mp4", "start": 8.0, "duration": 5.0}]
        items, warnings = validate_footage_plan(raw, sample_clips())
        self.assertEqual(items[0]["duration"], 2.0)
        self.assertEqual(len(warnings), 1)

    def test_start_beyond_end_raises(self):
        raw = [{"index": 1, "source": "a.mp4", "start": 10.5, "duration": 1.0}]
        with self.assertRaises(FootageError):
            validate_footage_plan(raw, sample_clips())

    def test_non_dict_shot_raises(self):
        with self.assertRaises(FootageError):
            validate_footage_plan(["oops"], sample_clips())

    def test_zero_duration_clip_rejected(self):
        clips = [FootageClip(name="z.mp4", path="/x/z.mp4", duration=0.0,
                             width=0, height=0, fps=0.0)]
        raw = [{"index": 1, "source": "z.mp4", "start": 0, "duration": 2}]
        with self.assertRaises(FootageError):
            validate_footage_plan(raw, clips)

    def test_default_duration_uses_remaining(self):
        raw = [{"index": 1, "source": "a.mp4", "start": 2.0, "duration": 0}]
        items, _ = validate_footage_plan(raw, sample_clips())
        self.assertGreater(items[0]["duration"], 0)

    def test_ranges_skip_filler_and_compute_total_duration(self):
        raw = [{"index": 1, "source": "a.mp4", "start": 0, "duration": 9,
                "ranges": [[0.5, 2.0], [5.0, 6.5], [6.4, 7.0]]}]
        items, warnings = validate_footage_plan(raw, sample_clips())
        self.assertEqual(items[0]["ranges"], [[0.5, 2.0], [5.0, 7.0]])
        self.assertAlmostEqual(items[0]["duration"], 3.5)
        self.assertEqual(warnings, [])

    def test_clamps_visual_params(self):
        raw = [{"index": 1, "source": "a.mp4", "start": 0, "duration": 2,
                "focus_x": 2.0, "focus_y": -1.0, "speed": 9.9, "bgm_volume": 1.0}]
        items, _ = validate_footage_plan(raw, sample_clips())
        self.assertEqual(items[0]["focus_x"], 1.0)
        self.assertEqual(items[0]["focus_y"], 0.0)
        self.assertEqual(items[0]["speed"], 1.5)
        self.assertEqual(items[0]["bgm_volume"], 0.35)


class FakeRouter(ModelRouter):
    """继承 ModelRouter 覆盖 complete_json，不发起真实网络请求。"""

    def __init__(self, config_path):
        self.calls = []
        super().__init__(config_path)

    def complete_json(self, profile, prompt, function=""):
        self.calls.append((profile.id, function, prompt))
        return {"footage_plan": [{
            "index": 1, "source": "a.mp4", "start": 0.2, "duration": 3.0,
            "objective": "开场", "visual": "展示商品", "script": "大家好",
            "composition": "主体清晰居中", "focus_x": 0.5, "focus_y": 0.5,
            "subtitle_position": "底部安全区", "subtitle_style": "白字黑边",
            "pacing": "标准", "speed": 1.0, "bgm_intensity": "低",
            "bgm_volume": 0.16, "transition": "硬切",
        }]}


class PlanFootageTests(unittest.TestCase):
    def make_router(self):
        tmp = tempfile.mkdtemp(prefix="footage-router-")
        path = Path(tmp) / "model-config.json"
        data = {
            "default_model": "m0",
            "models": [
                {"id": f"m{i}", "name": f"模型{i}", "provider": "local_openai",
                 "base_url": "http://127.0.0.1:11434/v1", "model": f"model-{i}",
                 "api_key": "", "enabled": True}
                for i in range(10)
            ],
            "routes": {function: f"m{i}" for i, function in enumerate(FUNCTIONS)},
        }
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return FakeRouter(path)

    def test_routes_to_director_and_returns_plan(self):
        router = self.make_router()
        plan = router.plan_footage(
            {"name": "测试商品", "summary": "xxx"},
            {"product_summary": "测试", "selling_points": ["A"], "shots": []},
            [{"name": "a.mp4", "duration": 10.0, "width": 1080,
              "height": 1920, "fps": 30.0}],
            {"platform": "抖音"},
        )
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0]["source"], "a.mp4")
        self.assertEqual(router.calls[-1][:2], ("m9", "素材剪辑导演"))
        self.assertIn("a.mp4", router.calls[-1][2])
        self.assertIn("footage_clips", router.calls[-1][2])

    def test_invalid_result_raises(self):
        router = self.make_router()
        router.complete_json = lambda *a, **k: {"foo": 1}
        with self.assertRaises(RuntimeError):
            router.plan_footage({}, {}, [], {})


class RenderFootageShotTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="prod-footage-"))
        self.store = ProductionStore(self.root)

    def project(self, **shot_kwargs):
        shot = Shot(id="s1", index=1, title="镜头1", visual="展示", script="文案",
                    **shot_kwargs)
        project = Project(id="p1", product_name="测试", platform="抖音", form="真人",
                          level=1, actor_id=None, scene_id=None, shots=[shot])
        return project, shot

    def test_missing_source_file_raises(self):
        project, shot = self.project(clip_source="filmed",
                                     source_file="/no/such.mp4",
                                     source_start=0.0, source_duration=3.0)
        with self.assertRaises(FootageError):
            self.store.render_footage_shot(project, shot)

    def test_trim_and_mark_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "clip.mp4"
            src.write_bytes(b"x")
            project, shot = self.project(clip_source="filmed",
                                         source_file=str(src),
                                         source_start=1.0, source_duration=3.0)
            captured = {}

            def fake_trim(source, out, start, duration):
                captured.update(source=source, out=out, start=start, duration=duration)
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(b"video")
                return out

            with mock.patch.object(footage_module, "trim_clip", side_effect=fake_trim):
                result = self.store.render_footage_shot(project, shot)
        self.assertEqual(captured["start"], 1.0)
        self.assertEqual(captured["duration"], 3.0)
        self.assertEqual(result, self.store.render_path(project, shot))
        self.assertEqual(shot.video_path, str(result))
        self.assertEqual(shot.status, "已生成")
        self.assertEqual(shot.provider, "本地素材剪辑")

    def test_trim_failure_marks_failed_and_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "clip.mp4"
            src.write_bytes(b"x")
            project, shot = self.project(clip_source="filmed",
                                         source_file=str(src),
                                         source_start=0.0, source_duration=2.0)

            def boom(*a, **k):
                raise RuntimeError("ffmpeg 失败")

            with mock.patch.object(footage_module, "trim_clip", side_effect=boom):
                with self.assertRaises(RuntimeError):
                    self.store.render_footage_shot(project, shot)
        self.assertEqual(shot.status, "素材裁剪失败")

    def test_render_shot_routes_filmed_to_footage(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "clip.mp4"
            src.write_bytes(b"x")
            project, shot = self.project(clip_source="filmed",
                                         source_file=str(src),
                                         source_start=0.0, source_duration=2.0)
            with mock.patch.object(self.store, "render_footage_shot",
                                   return_value=Path("out.mp4")) as fake:
                result = self.store.render_shot(project, shot)
        fake.assert_called_once_with(project, shot)
        self.assertEqual(result, Path("out.mp4"))


if __name__ == "__main__":
    unittest.main()


def test_archive_analyzed_waste_protects_currently_referenced_source(tmp_path):
    source = tmp_path / 'keep.mp4'
    source.write_bytes(b'video')
    clip = FootageClip(name='keep.mp4', path=str(source), duration=3.0, width=720, height=1280, fps=30.0)
    kept, records = archive_analyzed_waste([clip], {'clips': [{'source': 'keep.mp4', 'usable': False, 'reason': '画面抖动'}]}, tmp_path / '05_废片库', 'project-1', protected_paths={str(source)})
    assert kept == [clip]
    assert source.exists()
    assert records[0]['protected'] is True
    assert records[0]['archived'] is False


def test_append_footage_reanalysis_history_keeps_previous_snapshot(tmp_path):
    from ad_studio.footage import append_footage_reanalysis_history
    p = append_footage_reanalysis_history(tmp_path / 'project', {'coverage': 72, 'plan': ['old']})
    assert p.exists()
    assert 'old' in p.read_text(encoding='utf-8')
    assert p.parent.name == 'footage-reanalysis-history'


def test_history_report_method_does_not_require_ai(tmp_path):
    from ad_studio.footage import append_footage_reanalysis_history
    p = append_footage_reanalysis_history(tmp_path / 'project', {'footage_plan': [{'source': 'a.mp4'}]})
    assert p.exists()
