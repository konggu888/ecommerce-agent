import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ad_studio.models import Project, Shot
from ad_studio.production import ProductionStore


def make_project(task_type):
    shots = [
        Shot(id=f"shot-{i:02d}", index=i, title=f"{task_type}-镜头{i}", visual="商品主体清晰", script="用户确认卖点")
        for i in range(1, 4)
    ]
    return Project(
        id=f"project-{task_type}", product_name="验收商品", platform="抖音", form=task_type,
        level=2, actor_id=None, scene_id=None, shots=shots,
        product_info={"name":"验收商品","selling_points":["用户确认卖点"],"specs":{"容量":"500ml"},"forbidden_terms":["全网最低"]},
        creative_plan={"variant_index":1, "workflow_task_type":task_type},
    )


class A33FullUserFlowTests(unittest.TestCase):
    TASKS = ("电商短视频", "商品主图视频", "广告投放视频")

    def _prepare_completed_shots(self, root, project):
        for shot in project.shots:
            path = root / f"{shot.id}.mp4"
            path.write_bytes(b"test-video")
            shot.video_path = str(path)
            shot.status = "已生成"
            shot.clip_source = "filmed" if project.form != "广告投放视频" else "ai_generated"
            shot.storyboard_review = "不需要"

    def _finalize(self, store, project, root):
        def fake_concat(_inputs, target):
            Path(target).parent.mkdir(parents=True, exist_ok=True)
            Path(target).write_bytes(b"final-video")
        probe = type("Completed", (), {"stdout": json.dumps({
            "streams":[{"codec_type":"video","width":1080,"height":1920}],
            "format":{"duration":"6.0"}
        })})()
        with patch("ad_studio.production.concat", side_effect=fake_concat), patch(
            "ad_studio.production.shutil.which", return_value="/usr/bin/ffprobe"
        ), patch("ad_studio.production.subprocess.run", return_value=probe):
            built = store.build_final(project, "9:16", variant_index=1)
        self.assertTrue(built.exists())
        manifest = json.loads(built.with_suffix(".json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["delivery_status"], "可交付")
        self.assertEqual(manifest["shot_count"], 3)
        return built, manifest

    def test_a33_normal_path_runs_for_all_three_workflows(self):
        for task_type in self.TASKS:
            with self.subTest(task_type=task_type), tempfile.TemporaryDirectory() as td:
                root = Path(td); store = ProductionStore(root); project = make_project(task_type)
                self._prepare_completed_shots(root, project)
                gate = store.final_render_gate(project)
                self.assertTrue(gate["allowed"])
                inputs = store.final_render_inputs(project)
                self.assertEqual([x["index"] for x in inputs], [1, 2, 3])
                output, manifest = self._finalize(store, project, root)
                self.assertTrue(output.exists())
                self.assertEqual(manifest["variant_index"], 1)

    def test_a33_exception_path_blocks_incomplete_workflow_for_all_three(self):
        for task_type in self.TASKS:
            with self.subTest(task_type=task_type), tempfile.TemporaryDirectory() as td:
                root = Path(td); store = ProductionStore(root); project = make_project(task_type)
                self._prepare_completed_shots(root, project)
                project.shots[-1].video_path = None
                with self.assertRaises(RuntimeError) as cm:
                    store.build_final(project, "9:16", variant_index=1)
                self.assertIn("没有成片", str(cm.exception))

    def test_a33_safety_intercept_blocks_each_workflow(self):
        for task_type in self.TASKS:
            with self.subTest(task_type=task_type), tempfile.TemporaryDirectory() as td:
                root = Path(td); store = ProductionStore(root); project = make_project(task_type)
                self._prepare_completed_shots(root, project)
                project.creative_plan["creative_fact_audit"] = {"variants":[
                    {"variant_index":1,"forbidden_term_hits":["全网最低"]}
                ]}
                gate = store.final_render_gate(project)
                self.assertFalse(gate["allowed"])
                self.assertIn("命中用户禁用词", gate["reasons"][0])
                with self.assertRaises(RuntimeError):
                    store.build_final(project, "9:16", variant_index=1)

    def test_a33_repair_recheck_and_delivery_complete_for_all_three(self):
        for task_type in self.TASKS:
            with self.subTest(task_type=task_type), tempfile.TemporaryDirectory() as td:
                root = Path(td); store = ProductionStore(root); project = make_project(task_type)
                self._prepare_completed_shots(root, project)
                project.creative_plan["creative_fact_audit"] = {"variants":[
                    {"variant_index":1,"absolute_or_high_risk_claims":["最高"]}
                ]}
                self.assertFalse(store.final_render_gate(project)["allowed"])
                project.creative_plan["creative_fact_audit"] = {}
                gate = store.final_render_gate(project)
                self.assertTrue(gate["allowed"])
                output, manifest = self._finalize(store, project, root)
                history = store.final_output_history(project)
                self.assertEqual(history[0]["delivery_status"], "可交付")
                self.assertEqual(history[0]["output_path"], str(output))
                self.assertTrue(manifest["media_check"]["valid"])


if __name__ == "__main__":
    unittest.main()
