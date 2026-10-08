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


    def test_variant_state_survives_plan_switch(self):
        # 切换方案会重建当前 creative_plan；已生成的版本缓存/输出记录必须保留。
        try:
            from ad_studio.app import App
        except ModuleNotFoundError as exc:
            if exc.name != 'tkinter':
                raise
            import sys, types
            fake_tk = types.ModuleType('tkinter')
            fake_tk.Tk = object
            fake_tk.ttk = types.ModuleType('tkinter.ttk')
            fake_tk.filedialog = types.ModuleType('tkinter.filedialog')
            fake_tk.messagebox = types.ModuleType('tkinter.messagebox')
            sys.modules['tkinter'] = fake_tk
            sys.modules['tkinter.ttk'] = fake_tk.ttk
            sys.modules['tkinter.filedialog'] = fake_tk.filedialog
            sys.modules['tkinter.messagebox'] = fake_tk.messagebox
            from ad_studio.app import App
        with tempfile.TemporaryDirectory() as td:
            app = App.__new__(App)
            app.project = new_project("https://item.jd.com/123.html", 2, "真人口播")
            app.project.creative_plan = {
                "creative_variants": [
                    {"_variant_index": 1, "video_form": "方案A"},
                    {"_variant_index": 2, "video_form": "方案B"},
                ],
                "variant_count": 2,
                "variant_shot_cache": {
                    "1": [{"id": "shot-01", "index": 1, "title": "A镜头", "visual": "A", "script": "A"}],
                    "2": [{"id": "shot-01", "index": 1, "title": "B镜头", "visual": "B", "script": "B"}],
                },
                "variant_outputs": {"1": {"path": "/tmp/a-final.mp4", "status": "已输出"}},
                "variant_footage_gap_tasks": {"1": {"tasks": [{"task_id": "A"}]}},
            }
            app.active_variant_index = 1
            app.level = type("V", (), {"get": lambda self: 2})()
            app.form = type("V", (), {"get": lambda self: "AI自动选择"})()
            app.task_type = type("V", (), {"get": lambda self: "电商短视频"})()
            app.lib = type("L", (), {"reusable": lambda self, kind: []})()
            app._activate_plan({
                "_variant_index": 2,
                "_variant_label": "方案2｜B",
                "video_form": "AI自动选择",
                "shots": [],
            }, type("Info", (), {"name": "测试商品"})())
            self.assertEqual(app.project.creative_plan["variant_outputs"]["1"]["path"], "/tmp/a-final.mp4")
            self.assertIn("2", app.project.creative_plan["variant_shot_cache"])
            self.assertIn("1", app.project.creative_plan["variant_footage_gap_tasks"])

    def test_variant_runtime_state_isolated_for_hybrid_gap_tasks(self):
        # GitHub Linux runner不一定安装Tk；测试只需要App的无GUI状态方法。
        try:
            from ad_studio.app import App
        except ModuleNotFoundError as exc:
            if exc.name != 'tkinter':
                raise
            import sys
            import types
            fake_tk = types.ModuleType('tkinter')
            fake_tk.Tk = object
            fake_tk.ttk = types.ModuleType('tkinter.ttk')
            fake_tk.filedialog = types.ModuleType('tkinter.filedialog')
            fake_tk.messagebox = types.ModuleType('tkinter.messagebox')
            sys.modules['tkinter'] = fake_tk
            sys.modules['tkinter.ttk'] = fake_tk.ttk
            sys.modules['tkinter.filedialog'] = fake_tk.filedialog
            sys.modules['tkinter.messagebox'] = fake_tk.messagebox
            from ad_studio.app import App
        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td))
            p = new_project("https://item.jd.com/123.html", 2, "真人口播")
            p.creative_plan = {
                "variant_footage_gap_tasks": {},
                "variant_hybrid_reviewed_shots": {},
            }
            app = App.__new__(App)
            app.project = p
            app.active_variant_index = 1
            p.creative_plan["footage_gap_tasks"] = {
                "tasks": [{
                    "task_id": "A-GAP-1",
                    "variant_index": 1,
                    "recommended_resolution": "AI补镜头",
                    "generated_path": "/tmp/a.mp4",
                    "review_status": "已通过",
                }]
            }
            p.creative_plan["hybrid_reviewed_shots"] = [{"task_id": "A-GAP-1", "variant_index": 1}]
            app._cache_active_variant()

            app.active_variant_index = 2
            p.creative_plan["footage_gap_tasks"] = {"tasks": [{
                "task_id": "B-GAP-1",
                "variant_index": 2,
                "recommended_resolution": "AI补镜头",
            }]}
            p.creative_plan["hybrid_reviewed_shots"] = [{"task_id": "B-GAP-1", "variant_index": 2}]
            app._cache_active_variant()

            # 模拟切换回方案1：必须恢复 A，不能看到 B。
            app.active_variant_index = 1
            app._restore_active_variant_runtime()
            self.assertEqual(
                [x["task_id"] for x in p.creative_plan["footage_gap_tasks"]["tasks"]],
                ["A-GAP-1"],
            )
            self.assertEqual(
                [x["task_id"] for x in p.creative_plan["hybrid_reviewed_shots"]],
                ["A-GAP-1"],
            )

            app.active_variant_index = 2
            app._restore_active_variant_runtime()
            self.assertEqual(
                [x["task_id"] for x in p.creative_plan["footage_gap_tasks"]["tasks"]],
                ["B-GAP-1"],
            )
            self.assertEqual(
                [x["task_id"] for x in p.creative_plan["hybrid_reviewed_shots"]],
                ["B-GAP-1"],
            )

    def test_variant_render_paths_are_physically_isolated(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            p = new_project("https://item.jd.com/123.html", 2, "真人口播")
            p.creative_plan["variant_index"] = 1
            a = store.render_path(p, p.shots[0])
            p.creative_plan["variant_index"] = 2
            b = store.render_path(p, p.shots[0])
            self.assertNotEqual(a, b)
            self.assertIn("variant-1", str(a))
            self.assertIn("variant-2", str(b))
            self.assertNotEqual(store._variant_index(p), 1)

            # 后处理路径同样不能复用另一个方案的目录。
            self.assertIn("variant-2", str(root / "postprocessed" / p.id / "variant-2" / p.shots[0].id))
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