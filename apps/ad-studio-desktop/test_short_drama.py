import unittest

from ad_studio.short_drama import (
    ShortDramaPlanError, build_short_drama_prompt, generate_short_drama,
    audit_short_drama, build_episode_continuity_ledger, short_drama_production_rows, validate_short_drama,
    generate_next_short_drama_episode,
)


def sample_plan():
    return {
        "drama_business_mode": "product_placement",
        "genre": "都市轻喜剧",
        "genre_reasoning": "目标人群熟悉通勤生活",
        "logline": "一场出门前的混乱让主角发现商品的实际用途",
        "premise": "日常问题引发连续误会",
        "world": "现代城市公寓与通勤路上",
        "characters": [{"name": "小林", "role": "主角", "goal": "准时出门",
                        "relationship": "同事", "arc": "从慌乱到从容"}],
        "plot_beats": ["意外开场", "误会升级", "商品自然解决问题", "轻松收尾"],
        "conflict_and_reversal": "主角以为问题无法解决，后来发现关键在准备方式",
        "ending": "主角从容赴约",
        "full_script": "场景一：主角匆忙寻找物品……",
        "storyboard": [{
            "index": 1, "scene": "公寓玄关", "location": "现代公寓",
            "characters": ["小林"], "action": "主角翻找物品并看向时钟",
            "dialogue": "怎么又找不到了？", "product_integration": "暂不出现",
            "asset_needs": ["演员：年轻上班族", "场景：公寓玄关"],
            "actor_requirements": ["年轻上班族"], "scene_requirements": ["公寓玄关"],
            "product_asset_requirements": [],
            "shot_type": "中景推近", "duration_seconds": 4,
            "generation_prompt": "自然光，生活化表演"
        }],
        "product_truths": ["仅使用已确认商品信息"],
        "risk_notes": ["商品具体参数待确认"],
        "alternative_directions": [
            {"title": "反转喜剧", "mechanism": "误会反转", "conversion_path": "演示后引导了解"},
            {"title": "温情日常", "mechanism": "关系变化", "conversion_path": "情境共鸣后介绍"}
        ]
    }


class ShortDramaTests(unittest.TestCase):
    def test_validates_story_first_plan(self):
        plan = validate_short_drama(sample_plan())
        self.assertEqual(plan["storyboard"][0]["duration_seconds"], 4)
        self.assertEqual(plan["genre"], "都市轻喜剧")

    def test_rejects_missing_storyboard(self):
        plan = sample_plan()
        plan["storyboard"] = []
        with self.assertRaises(ShortDramaPlanError):
            validate_short_drama(plan)

    def test_prompt_preserves_product_and_existing_plan_as_context(self):
        prompt = build_short_drama_prompt(
            {"name": "测试商品", "description": "便携"},
            {"platform": "抖音"},
            {"script": "已有广告脚本"}
        )
        self.assertIn("测试商品", prompt)
        self.assertIn("已有广告脚本", prompt)
        self.assertIn("不是把常规广告脚本扩写成几个镜头", prompt)
        self.assertIn("constraints.drama_business_mode", prompt)
        general_prompt = build_short_drama_prompt({}, {"drama_business_mode": "general"})
        self.assertIn("允许完全不带商品", general_prompt)

    def test_builds_existing_production_contract(self):
        rows = short_drama_production_rows(sample_plan(), "测试商品")
        self.assertEqual(rows[0]["duration_seconds"], 4)
        self.assertEqual(rows[0]["asset_resolution"]["actor_tags"], ["年轻上班族"])
        self.assertEqual(rows[0]["asset_resolution"]["scene_tags"], ["公寓玄关"])
        self.assertEqual(rows[0]["asset_resolution"]["product_tags"], [])
        self.assertEqual(rows[0]["director_mode"], "short_drama")

    def test_audit_flags_ad_claim_and_unknown_character(self):
        plan = sample_plan()
        plan["full_script"] = "本产品保证有效，绝对安全。"
        plan["storyboard"][0]["characters"] = ["未定义人物"]
        report = audit_short_drama(plan, {"description": "普通日用品"})
        codes = {item["code"] for item in report["issues"]}
        self.assertIn("AD_CLAIM_REVIEW", codes)
        self.assertIn("UNKNOWN_CHARACTER", codes)
        self.assertEqual(report["status"], "需人工复核")
        self.assertTrue(report["passed"])

    def test_audit_flags_scene_location_conflict(self):
        plan = sample_plan()
        second = dict(plan["storyboard"][0])
        second["index"] = 2
        second["location"] = "另一个完全不同的地点"
        second["scene"] = plan["storyboard"][0]["scene"]
        plan["storyboard"].append(second)
        report = audit_short_drama(plan, {"description": "便携商品"})
        self.assertIn("SCENE_CONTINUITY", {item["code"] for item in report["issues"]})
        self.assertEqual(report["total_duration_seconds"], 8)

    def test_accepts_and_flattens_continuous_multi_episode_plan(self):
        plan = sample_plan()
        first_shot = dict(plan["storyboard"][0])
        second_shot = dict(plan["storyboard"][0])
        second_shot["index"] = 1
        second_shot["scene"] = "办公室"
        plan["format_mode"] = "continuous_series"
        plan["episode_count"] = 2
        plan["series_bible"] = {"series_arc": "从误会到和解", "continuity_rules": ["主角外观保持一致"]}
        plan["episodes"] = [
            {"episode_number": 1, "title": "误会", "logline": "冲突发生", "full_script": "第一集剧本",
             "plot_beats": ["开场", "冲突", "悬念"], "ending_hook": "主角发现线索", "continuity_state": {"opening_state": "小林准备出门", "character_state_changes": ["小林发现线索"], "unresolved_threads": ["线索来自谁"], "ending_state": "小林拿到一张匿名便条", "next_episode_requirements": ["第二集必须解释便条来源"]}, "storyboard": [first_shot]},
            {"episode_number": 2, "title": "反转", "logline": "线索揭晓", "full_script": "第二集剧本",
             "plot_beats": ["承接", "反转", "收束"], "ending_hook": "阶段结局", "continuity_state": {"opening_state": "小林持有上一集的匿名便条", "character_state_changes": ["小林开始信任同事"], "unresolved_threads": [], "ending_state": "便条来源得到解释", "next_episode_requirements": []}, "storyboard": [second_shot]},
        ]
        plan["storyboard"] = []
        validated = validate_short_drama(plan)
        self.assertEqual([x["episode_number"] for x in validated["storyboard"]], [1, 2])
        rows = short_drama_production_rows(validated, "测试商品")
        self.assertEqual([x["episode_number"] for x in rows], [1, 2])
        self.assertEqual([x["index"] for x in rows], [1, 2])
        self.assertEqual([x["episode_shot_index"] for x in rows], [1, 1])
        self.assertTrue(rows[1]["title"].startswith("第2集"))
        self.assertEqual([x["episode_number"] for x in validated["continuity_ledger"]], [1, 2])
        self.assertIn("匿名便条", validated["continuity_ledger"][0]["ending_state"])
        self.assertIn("解释便条来源", validated["continuity_ledger"][0]["next_episode_requirements"][0])

    def test_general_mode_can_generate_without_product(self):
        seen = {}
        class FakeRouter:
            def resolve_route(self, function): return "profile"
            def complete_json(self, profile, prompt, function=None):
                plan = sample_plan()
                plan["drama_business_mode"] = "general"
                plan["storyboard"][0]["product_integration"] = "本镜不出现商品"
                return plan
        result = generate_short_drama(FakeRouter(), {}, {"drama_business_mode": "general"})
        self.assertEqual(result["drama_business_mode"], "general")

    def test_rejects_unknown_drama_business_mode(self):
        plan = sample_plan()
        plan["drama_business_mode"] = "random_mode"
        with self.assertRaises(ShortDramaPlanError):
            validate_short_drama(plan)

    def test_builds_continuity_ledger_in_episode_order(self):
        plan = sample_plan()
        plan["episodes"] = [
            {"episode_number": 1, "continuity_state": {"opening_state": "A", "character_state_changes": ["B"], "unresolved_threads": ["C"], "ending_state": "D", "next_episode_requirements": ["E"]}},
            {"episode_number": 2, "continuity_state": {"opening_state": "D", "character_state_changes": [], "unresolved_threads": [], "ending_state": "F", "next_episode_requirements": []}},
        ]
        ledger = build_episode_continuity_ledger(plan)
        self.assertEqual([row["episode_number"] for row in ledger], [1, 2])
        self.assertEqual(ledger[1]["opening_state"], "D")

    def test_rejects_multi_episode_plan_without_continuity_state(self):
        plan = sample_plan()
        plan["format_mode"] = "continuous_series"
        plan["episode_count"] = 2
        plan["episodes"] = [{"episode_number": 1, "storyboard": [dict(plan["storyboard"][0])]}, {"episode_number": 2, "storyboard": [dict(plan["storyboard"][0])]}]
        with self.assertRaisesRegex(ShortDramaPlanError, "continuity_state"):
            validate_short_drama(plan)

    def test_rejects_missing_episode_in_series(self):
        plan = sample_plan()
        plan["format_mode"] = "continuous_series"
        plan["episode_count"] = 2
        plan["episodes"] = [{"episode_number": 1, "storyboard": [dict(plan["storyboard"][0])]}]
        with self.assertRaises(ShortDramaPlanError):
            validate_short_drama(plan)

    def test_uses_dedicated_route_and_records_function(self):
        seen = {}
        class FakeRouter:
            def resolve_route(self, function):
                seen["route"] = function
                return "profile"
            def complete_json(self, profile, prompt, function=None):
                seen["function"] = function
                return sample_plan()
        result = generate_short_drama(FakeRouter(), {"name": "商品"}, {"drama_business_mode": "product_placement"})
        self.assertEqual(seen["route"], "AI短剧编导")
        self.assertEqual(seen["function"], "AI短剧编导")
        self.assertEqual(len(result["storyboard"]), 1)


    def test_next_episode_uses_handoff_context_and_preserves_previous_episode(self):
        plan = sample_plan()
        plan["format_mode"] = "continuous_series"
        plan["episode_count"] = 1
        plan["episodes"] = [{
            "episode_number": 1, "title": "匿名便条", "logline": "小林发现线索",
            "plot_beats": ["开场", "发现线索", "悬念"], "ending_hook": "匿名便条",
            "full_script": "第一集完整剧本",
            "continuity_state": {"opening_state": "小林准备出门", "character_state_changes": ["小林发现便条"],
                "unresolved_threads": ["便条是谁留下的"], "ending_state": "小林拿着匿名便条",
                "next_episode_requirements": ["解释便条来源，便条不能消失"]},
            "storyboard": [dict(plan["storyboard"][0])],
        }]
        plan["storyboard"][0]["episode_number"] = 1
        seen = {}
        class FakeRouter:
            def resolve_route(self, function): return "short-drama-profile"
            def complete_json(self, profile, prompt, function=None):
                seen["prompt"] = prompt
                return {"episode_number": 2, "title": "便条的来历", "logline": "小林追查便条",
                    "plot_beats": ["承接便条", "追查来源", "揭开部分真相"], "ending_hook": "新线索",
                    "full_script": "第二集完整剧本",
                    "continuity_state": {"opening_state": "小林仍拿着第一集的匿名便条",
                        "character_state_changes": ["小林开始信任同事"], "unresolved_threads": ["新线索指向旧档案"],
                        "ending_state": "便条来源得到部分解释", "next_episode_requirements": ["继续追查旧档案"]},
                    "storyboard": [dict(plan["storyboard"][0])]}
        updated = generate_next_short_drama_episode(FakeRouter(), plan, {})
        self.assertIn("便条是谁留下的", seen["prompt"])
        self.assertIn("小林拿着匿名便条", seen["prompt"])
        self.assertEqual(updated["episode_count"], 2)
        self.assertEqual([e["episode_number"] for e in updated["episodes"]], [1, 2])
        self.assertEqual(updated["episodes"][0]["full_script"], "第一集完整剧本")
        self.assertEqual(updated["storyboard"][-1]["episode_number"], 2)
        self.assertEqual(updated["continuity_ledger"][1]["opening_state"], "小林仍拿着第一集的匿名便条")

    def test_next_episode_rejects_wrong_episode_number(self):
        plan = sample_plan()
        plan["format_mode"] = "continuous_series"
        plan["episode_count"] = 1
        plan["episodes"] = [{"episode_number": 1, "title": "第一集", "logline": "开场",
            "plot_beats": ["开场", "冲突", "悬念"], "ending_hook": "钩子", "full_script": "剧本",
            "continuity_state": {"opening_state": "开场", "character_state_changes": [], "unresolved_threads": [],
                "ending_state": "结尾", "next_episode_requirements": ["承接"]},
            "storyboard": [dict(plan["storyboard"][0])]}]
        class FakeRouter:
            def resolve_route(self, function): return "profile"
            def complete_json(self, profile, prompt, function=None): return {"episode_number": 3}
        with self.assertRaisesRegex(ShortDramaPlanError, "要求第2集"):
            generate_next_short_drama_episode(FakeRouter(), plan, {})


    def test_product_short_drama_ad_requires_fidelity_constraints_and_explains_genre(self):
        plan = sample_plan()
        plan["drama_business_mode"] = "product_short_drama_ad"
        plan["product_analysis"] = {"product_type": "便携收纳用品", "target_audience": "通勤人群", "selling_points": ["便携"], "usage_scenarios": ["通勤"], "unknown_facts": ["材质待确认"]}
        plan["genre_decision"] = {"selected_genre": "古代轻喜剧", "reasoning": "用古代出行收纳难题演绎便携价值", "world_style": "架空古代市集", "story_product_role": "主角解决出行收纳问题的真实用品"}
        plan["product_fact_lock"] = {"confirmed_facts": ["便携"], "unknown_or_unverified": ["材质待确认"], "appearance_structure_function_constraints": ["保持参考图外观与结构", "只展示已确认的真实用途"], "reference_assets_required": ["商品正面/侧面参考图"], "do_not_change": ["不得改色改款", "不得添加不存在的功能"]}
        plan["storyboard"][0]["product_fidelity_constraints"] = ["商品外观和结构必须与参考素材一致", "不得添加未确认功能"]
        plan["storyboard"][0]["visual_verification"] = "not_checked"
        validated = validate_short_drama(plan)
        self.assertEqual(validated["genre_decision"]["selected_genre"], "古代轻喜剧")
        report = audit_short_drama(validated, {"name": "便携收纳用品", "description": "便携"})
        self.assertIn("PRODUCT_VISUAL_NOT_VERIFIED", {item["code"] for item in report["issues"]})

    def test_product_short_drama_ad_rejects_missing_fidelity_lock(self):
        plan = sample_plan()
        plan["drama_business_mode"] = "product_short_drama_ad"
        plan["product_analysis"] = {"product_type": "用品"}
        plan["genre_decision"] = {"selected_genre": "古代", "reasoning": "故事适配"}
        plan["product_fact_lock"] = {"confirmed_facts": [], "unknown_or_unverified": []}
        with self.assertRaisesRegex(ShortDramaPlanError, "商品外观/结构/功能真实性约束"):
            validate_short_drama(plan)

    def test_product_short_drama_ad_requires_product_material(self):
        class FakeRouter:
            def resolve_route(self, function): return "profile"
            def complete_json(self, profile, prompt, function=None):
                plan = sample_plan()
                plan["drama_business_mode"] = "product_short_drama_ad"
                plan["product_analysis"] = {"product_type": "用品"}
                plan["genre_decision"] = {"selected_genre": "古代", "reasoning": "适配"}
                plan["product_fact_lock"] = {"confirmed_facts": [], "unknown_or_unverified": []}
                plan["storyboard"][0]["product_fidelity_constraints"] = ["保持真实外观"]
                return plan
        with self.assertRaisesRegex(ShortDramaPlanError, "必须提供商品资料"):
            generate_short_drama(FakeRouter(), {}, {"drama_business_mode": "product_short_drama_ad"})

if __name__ == "__main__":
    unittest.main()
