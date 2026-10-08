import json
import tempfile
import unittest
from pathlib import Path

from ad_studio.model_router import FUNCTIONS, ModelProfile, ModelRouter, audit_ad_variant_set, build_creative_test_plan, audit_creative_factual_consistency, audit_storyboard_fact_consistency, audit_visual_fact_consistency


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


class CreativeVariantAuditTest(unittest.TestCase):
    def test_non_platform_creative_audit_requires_single_mechanism_for_clean_test(self):
        plans = [
            {"hook": "先痛点", "strategy": "痛点后解决", "selling_points": ["省时间"], "video_form": "演示", "proof": "前后对比", "cta": "了解更多", "script": "A"},
            {"hook": "先结果", "strategy": "结果后解释", "selling_points": ["省时间"], "video_form": "演示", "proof": "前后对比", "cta": "了解更多", "script": "B"},
            {"hook": "先结果", "strategy": "结果后解释", "selling_points": ["省钱"], "video_form": "演示", "proof": "前后对比", "cta": "了解更多", "script": "C"},
        ]
        audit = audit_ad_variant_set(plans, "广告投放视频")
        self.assertTrue(audit["enabled"])
        self.assertEqual(audit["mechanism_score"], 100)
        self.assertEqual(audit["test_design_score"], 75)
        self.assertIn("核心机制字段", audit["method"])

    def test_creative_audit_does_not_invent_platform_or_performance_data(self):
        plans = [
            {"hook": "A", "strategy": "A", "script": "同一商品"},
            {"hook": "A", "strategy": "A", "script": "另一版"},
        ]
        audit = audit_ad_variant_set(plans, "广告投放视频")
        self.assertEqual(audit["mechanism_score"], 0)
        self.assertEqual(audit["test_design_score"], 0)
        self.assertNotIn("platform", audit)
        self.assertNotIn("ctr", audit)
        self.assertNotIn("roas", audit)

    def test_non_ad_task_does_not_enable_ab_audit(self):
        audit = audit_ad_variant_set([{"hook": "A"}, {"hook": "B"}], "电商短视频")
        self.assertFalse(audit["enabled"])
        self.assertEqual(audit["test_design_score"], 0)


    def test_creative_test_plan_is_prelaunch_only_and_exposes_real_observation_targets(self):
        plans=[{"variant_test_axis":{"id":"hook","name":"钩子角度"},"hook":"先痛点","strategy":"痛点后解决","selling_points":["省时间"],"video_form":"演示","proof":"前后对比","cta":"了解更多"},{"variant_test_axis":{"id":"hook","name":"钩子角度"},"hook":"先结果","strategy":"痛点后解决","selling_points":["省时间"],"video_form":"演示","proof":"前后对比","cta":"了解更多"}]
        tp=build_creative_test_plan(plans,audit_ad_variant_set(plans,"广告投放视频"))
        self.assertTrue(tp["enabled"]); self.assertEqual(tp["variants"][0]["primary_test_axis"]["id"],"hook")
        self.assertIn("验证",tp["variants"][0]["test_purpose"]); self.assertEqual(tp["variants"][0]["result_status"],"待真实投放数据")
        self.assertNotIn("ctr",tp); self.assertNotIn("roas",tp); self.assertIn("真实反馈"," ".join(tp["variants"][0]["observation_targets"]))

    def test_creative_test_plan_flags_multi_mechanism_contamination(self):
        plans=[{"variant_test_axis":{"id":"hook","name":"钩子角度"},"hook":"A","strategy":"S1","selling_points":["P1"]},{"variant_test_axis":{"id":"hook","name":"钩子角度"},"hook":"B","strategy":"S2","selling_points":["P1"]}]
        tp=build_creative_test_plan(plans,audit_ad_variant_set(plans,"广告投放视频"))
        self.assertTrue(any("同时变化" in x for x in tp["next_round_recommendations"]))


    def test_creative_fact_audit_flags_unsupported_claims_forbidden_terms_and_absolute_words(self):
        product={"product_name":"测试商品","selling_points":["轻便","易收纳"]}
        variants=[{"selling_points":["轻便","全网第一"],"script":"这是全网第一，内部测试禁词"}]
        audit=audit_creative_factual_consistency(product,variants,["禁词"])
        item=audit["variants"][0]
        self.assertIn("全网第一",item["unsupported_selling_points"])
        self.assertIn("禁词",item["forbidden_term_hits"])
        self.assertIn("第一",item["absolute_or_high_risk_claims"])

    def test_creative_fact_audit_does_not_invent_missing_product_facts(self):
        audit=audit_creative_factual_consistency({},[{"selling_points":["神奇功能"]}],[])
        self.assertEqual(audit["variants"][0]["product_fact_status"],"缺少商品资料，无法完成事实核验")


    def test_storyboard_fact_audit_marks_visual_claims_as_review_and_matches_supported_facts(self):
        product={"selling_points":["轻便","易收纳"]}
        variants=[{"shots":[{"description":"展示轻便结构","product_focus":"商品主体","subtitle":"轻便"}]}]
        audit=audit_storyboard_fact_consistency(product,variants)
        shot=audit["variants"][0]["shots"][0]
        self.assertIn("轻便",shot["covered_facts"])
        self.assertEqual(shot["fact_status"],"有商品资料对应")
        self.assertEqual(shot["obscured"],"待视觉复核")
        self.assertEqual(shot["appearance_fidelity"],"待视觉复核")
        self.assertEqual(shot["function_fidelity"],"待视觉复核")

    def test_visual_fact_audit_maps_real_footage_analysis_risks_to_variant_plan(self):
        analysis={"clips":[{"source":"a.mp4","usable":True,"visual_tags":["product_visible","blocked"],"selling_points":["轻便"],"reason":"商品被手部部分遮挡"}]}
        plans={"1":[{"source":"a.mp4","start":0,"duration":2}]}
        audit=audit_visual_fact_consistency({"selling_points":["轻便"]},analysis,plans)
        shot=audit["variants"][0]["shots"][0]
        self.assertEqual(shot["risk_status"],"需复核")
        self.assertIn("商品可能被遮挡",shot["risks"])
        self.assertIn("轻便",shot["covered_selling_points"])

if __name__ == "__main__":
    unittest.main()