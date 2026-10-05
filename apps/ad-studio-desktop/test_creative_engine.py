import unittest

from ad_studio.creative_engine import CreativeEngine, CreativePlanError, validate_plan


def sample_plan():
    return {
        "product_summary": "一款面向通勤人群的便携商品",
        "product_type": "日用商品",
        "selling_points": ["便携", "易使用"],
        "target_audience": ["年轻通勤人群"],
        "pain_points": ["携带麻烦"],
        "usage_scenes": ["通勤"],
        "positioning": "解决日常携带不便",
        "ad_level": "轻广告",
        "video_form": "真人+产品",
        "duration_seconds": 30,
        "strategy": "先痛点后演示",
        "hook": "出门还在为携带麻烦发愁？",
        "script": "从痛点进入产品演示，再给出行动提示。",
        "shots": [{
            "index": 1,
            "objective": "建立痛点",
            "visual": "通勤场景",
            "dialogue": "为什么每天都这么麻烦？",
            "duration_seconds": 4,
            "actor_requirements": ["年轻"],
            "scene_requirements": ["通勤"],
            "product_asset_requirements": [],
            "on_screen_text": ["痛点"],
            "cta_role": "",
            "generation_prompt": "真实通勤短视频"
        }]
    }


class CreativeEngineTests(unittest.TestCase):
    def test_validate_structured_plan(self):
        plan = validate_plan(sample_plan())
        self.assertEqual(plan.video_form, "真人+产品")
        self.assertEqual(len(plan.shots), 1)

    def test_engine_uses_llm_output(self):
        seen = {}
        class FakeLLM:
            def create_plan(self, product, constraints):
                seen["product"] = product["name"]
                seen["platform"] = constraints["platform"]
                return sample_plan()

        plan = CreativeEngine(FakeLLM()).plan(
            {"name": "测试商品"},
            {"platform": "抖音"}
        )
        self.assertEqual(seen["product"], "测试商品")
        self.assertEqual(seen["platform"], "抖音")
        self.assertEqual(plan.selling_points, ["便携", "易使用"])

    def test_missing_fields_fail(self):
        with self.assertRaises(CreativePlanError):
            validate_plan({"product_summary": "x"})


if __name__ == "__main__":
    unittest.main()
