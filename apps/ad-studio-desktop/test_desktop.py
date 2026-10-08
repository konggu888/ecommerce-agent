import tempfile
import unittest
from pathlib import Path

from ad_studio.engine import detect_platform, estimate_cost, new_project, mark_regenerate
from ad_studio.library import LocalLibrary
from ad_studio.production import ProductionStore


class DesktopCoreTests(unittest.TestCase):
    def test_platform_detection(self):
        self.assertEqual(detect_platform("https://item.jd.com/123.html"), "京东")
        self.assertEqual(detect_platform("https://detail.tmall.com/item.htm?id=123"), "淘宝")
        self.assertEqual(detect_platform("https://mobile.yangkeduo.com/goods.html"), "拼多多")

    def test_budget_policy(self):
        c = estimate_cost(5)
        self.assertTrue(c["超预算"])
        self.assertEqual(c["总计"], 3.6)
        self.assertEqual(estimate_cost(6)["总计"], 4.32)

    def test_cost_breakdown_is_auditable_and_configurable(self):
        c = estimate_cost(5, {"cloud_video_per_shot": 1.0})
        self.assertEqual(c["云端"], 5.0)
        self.assertEqual(c["总计"], 5.0)
        video = next(x for x in c["明细"] if x["项目"] == "云端视频生成")
        self.assertEqual(video["数量"], 5)
        self.assertEqual(video["单价"], 1.0)
        self.assertEqual(video["小计"], 5.0)
        self.assertTrue(c["计价说明"])

    def test_only_selected_shot_changes_version(self):
        p = new_project("https://item.jd.com/123.html", 2, "真人口播")
        old = [s.version for s in p.shots]
        mark_regenerate(p, 2)
        self.assertEqual(p.shots[2].version, old[2] + 1)
        self.assertEqual([s.version for i, s in enumerate(p.shots) if i != 2], [old[i] for i in range(len(old)) if i != 2])

    def test_asset_persists_and_reuses(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            src = root / "actor.txt"
            src.write_text("actor", encoding="utf-8")
            lib = LocalLibrary(root / "library")
            a = lib.add_file(src, "测试演员", "演员")
            again = lib.reusable("演员")
            self.assertEqual(len(again), 1)
            self.assertEqual(again[0].id, a.id)

    def test_default_assets_have_stable_ids(self):
        with tempfile.TemporaryDirectory() as td:
            lib = LocalLibrary(Path(td) / 'library')
            lib.ensure_defaults()
            ids = {a.id for a in lib.all()}
            self.assertIn('actor-linchuan', ids)
            self.assertIn('scene-home', ids)
            lib.ensure_defaults()
            self.assertEqual(len(ids), len(lib.all()))

    def test_project_save_load(self):
        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td))
            p = new_project("https://item.jd.com/123.html", 2, "真人口播")
            p.cost_estimate = estimate_cost(len(p.shots))
            store.save(p)
            restored = store.load(p.id)
            self.assertIsNotNone(restored)
            self.assertEqual(restored.id, p.id)
            self.assertEqual(len(restored.shots), len(p.shots))
            self.assertEqual(restored.cost_estimate["总计"], 3.6)

    def test_reviewed_hybrid_task_persists_into_project(self):
        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td))
            p = new_project("https://item.jd.com/123.html", 2, "真人口播")
            task = {
                "task_id": "GAP-PERSIST-1",
                "generated_path": str(Path(td) / "support.mp4"),
                "review_status": "已通过",
                "estimated_cost_rmb": 0.72,
                "provider": "测试Provider",
                "target_shot_index": 2,
            }
            Path(task["generated_path"]).write_bytes(b"fake-video")
            accepted = store.accept_hybrid_generated_task(p, task)
            self.assertIsNotNone(accepted)
            self.assertTrue(task["accepted_into_storyboard"])
            self.assertEqual(len(p.shots), 6)
            self.assertTrue(any(s.id == task["accepted_shot_id"] for s in p.shots))
            restored = store.load(p.id)
            self.assertEqual(len(restored.shots), 6)
            self.assertTrue(any(s.id == task["accepted_shot_id"] for s in restored.shots))


    def test_final_render_inputs_are_ordered_and_pending_hybrid_is_excluded(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            p = new_project("https://item.jd.com/123.html", 2, "真人口播")
            for shot in p.shots:
                path = root / f"{shot.id}.mp4"
                path.write_bytes(b"video")
                shot.video_path = str(path)
            p.shots[1].storyboard_review = "待复核"
            inputs = store.final_render_inputs(p)
            self.assertEqual([x["index"] for x in inputs], [1, 3, 4, 5])
            self.assertEqual(inputs[0]["index"], 1)
            p.shots[1].storyboard_review = "已通过"
            inputs = store.final_render_inputs(p)
            self.assertEqual([x["index"] for x in inputs], [1, 2, 3, 4, 5])


if __name__ == "__main__":
    unittest.main()
