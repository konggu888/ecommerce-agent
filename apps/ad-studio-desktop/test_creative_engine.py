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

    # A missing speed is distinct from an explicit speed and must use pacing defaults.
    def test_pacing_sets_executable_default_speed(self):
        cases = (("慢", 0.85), ("标准", 1.0), ("快", 1.15), ("极快", 1.3))
        for pacing, expected_speed in cases:
            with self.subTest(pacing=pacing):
                raw = sample_plan()
                raw["shots"][0]["pacing"] = pacing
                shot = validate_plan(raw).shots[0]
                self.assertEqual(shot.pacing, pacing)
                self.assertEqual(shot.speed, expected_speed)

    def test_explicit_speed_overrides_pacing_default(self):
        raw = sample_plan()
        raw["shots"][0]["pacing"] = "快"
        raw["shots"][0]["speed"] = 0.9
        shot = validate_plan(raw).shots[0]
        self.assertEqual(shot.pacing, "快")
        self.assertEqual(shot.speed, 0.9)

    def test_unknown_pacing_falls_back_to_standard(self):
        raw = sample_plan()
        raw["shots"][0]["pacing"] = "极其神速"
        raw["shots"][0].pop("speed", None)
        shot = validate_plan(raw).shots[0]
        self.assertEqual(shot.pacing, "标准")
        self.assertEqual(shot.speed, 1.0)

    def test_role_defaults_drive_duration_speed_and_transition(self):
        cases = [
            ({"objective": "开场钩子：反常识问题"}, "hook", 2, 1.15, "硬切"),
            ({"objective": "商品细节展示", "visual": "商品特写与材质"}, "product_detail", 4, 0.85, "交叉溶解"),
            ({"objective": "功能演示", "visual": "逐步展示使用方法"}, "demonstration", 5, 1.0, "硬切"),
            ({"objective": "实测对比证明"}, "proof", 4, 0.85, "交叉溶解"),
        ]
        for fields, role, duration, speed, transition in cases:
            with self.subTest(role=role):
                raw = sample_plan()
                shot = raw["shots"][0]
                shot.update(fields)
                for key in ("duration_seconds", "pacing", "speed", "transition"):
                    shot.pop(key, None)
                resolved = validate_plan(raw).shots[0]
                self.assertEqual(resolved.editing_intent["role"], role)
                self.assertEqual(resolved.duration_seconds, duration)
                self.assertEqual(resolved.speed, speed)
                self.assertEqual(resolved.transition, transition)
                self.assertEqual(resolved.editing_intent["duration_source"], "role_default")
                self.assertTrue(resolved.editing_intent["rationale"])

    def test_last_cta_defaults_to_fade_out(self):
        raw = sample_plan()
        shot = raw["shots"][0]
        shot.update({"objective": "结束购买提醒", "cta_role": "下单转化"})
        for key in ("duration_seconds", "pacing", "speed", "transition"):
            shot.pop(key, None)
        resolved = validate_plan(raw).shots[0]
        self.assertEqual(resolved.editing_intent["role"], "cta")
        self.assertEqual(resolved.transition, "淡出")
        self.assertEqual(resolved.editing_intent["transition_source"], "role_default")

    def test_explicit_editing_decisions_override_role_defaults(self):
        raw = sample_plan()
        shot = raw["shots"][0]
        shot.update({"objective": "商品细节特写", "duration_seconds": 7, "pacing": "快", "speed": 1.2, "transition": "硬切"})
        resolved = validate_plan(raw).shots[0]
        self.assertEqual(resolved.duration_seconds, 7)
        self.assertEqual(resolved.speed, 1.2)
        self.assertEqual(resolved.transition, "硬切")
        self.assertEqual(resolved.editing_intent["duration_source"], "explicit")
        self.assertEqual(resolved.editing_intent["speed_source"], "explicit")
        self.assertEqual(resolved.editing_intent["transition_source"], "explicit")

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
