import json
import tempfile
import unittest
from pathlib import Path

from ad_studio.model_router import FUNCTIONS, ModelProfile, ModelRouter


class FakeRouter(ModelRouter):
    def __init__(self, config_path):
        self.calls = []
        super().__init__(config_path)

    def complete_json(self, profile, prompt):
        self.calls.append((profile.id, prompt))
        if "当前阶段：product_understanding" in prompt:
            return {"product_summary": "测试商品", "product_type": "测试", "positioning": "测试定位", "usage_scenes": ["家庭"]}
        if "当前阶段：selling_points" in prompt:
            return {"selling_points": ["卖点A"]}
        if "当前阶段：audience_pain" in prompt:
            return {"target_audience": ["人群A"], "pain_points": ["痛点A"]}
        if "当前阶段：ad_strategy" in prompt:
            return {"strategy": "测试策略", "hook": "测试开头"}
        if "当前阶段：ad_intensity" in prompt:
            return {"ad_level": "标准广告"}
        if "当前阶段：video_form" in prompt:
            return {"video_form": "真人+产品", "duration_seconds": 30}
        if "当前阶段：script" in prompt:
            return {"script": "测试剧本"}
        if "当前阶段：storyboard" in prompt:
            return {"shots": [{
                "index": 1, "objective": "开场", "visual": "展示商品",
                "dialogue": "这是测试", "duration_seconds": 3,
                "actor_requirements": [], "scene_requirements": [],
                "product_asset_requirements": ["商品主体"],
                "on_screen_text": ["测试"], "cta_role": "",
                "generation_prompt": "测试镜头"
            }]}
        if "当前阶段：asset_selection" in prompt:
            return {"asset_selection": [{
                "shot_index": 1, "asset_type": "product",
                "requirements": ["商品主体"], "preferred_asset_ids": []
            }]}
        raise AssertionError("unexpected stage")


class ModelRouterRoutingTest(unittest.TestCase):
    def test_all_nine_functions_use_their_selected_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "model-config.json"
            data = {
                "default_model": "m0",
                "models": [
                    {"id": f"m{i}", "name": f"模型{i}", "provider": "local_openai",
                     "base_url": "http://127.0.0.1:11434/v1", "model": f"model-{i}",
                     "api_key": "", "enabled": True}
                    for i in range(9)
                ],
                "routes": {function: f"m{i}" for i, function in enumerate(FUNCTIONS)},
            }
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            router = FakeRouter(path)
            plan = router.create_plan({"name": "测试商品"}, {"platform": "抖音"})

            self.assertEqual([model_id for model_id, _ in router.calls],
                             [f"m{i}" for i in range(9)])
            self.assertEqual(plan["ad_level"], "标准广告")
            self.assertEqual(plan["video_form"], "真人+产品")
            self.assertEqual(len(plan["shots"]), 1)
            self.assertIn("creative_stages", plan)


if __name__ == "__main__":
    unittest.main()
