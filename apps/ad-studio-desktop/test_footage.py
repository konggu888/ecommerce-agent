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
