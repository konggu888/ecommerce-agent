import unittest

from ad_studio.short_drama import (
    ShortDramaPlanError, build_short_drama_prompt, generate_short_drama,
    audit_short_drama, short_drama_production_rows, validate_short_drama,
)


def sample_plan():
    return {
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
             "plot_beats": ["开场", "冲突", "悬念"], "ending_hook": "主角发现线索", "storyboard": [first_shot]},
            {"episode_number": 2, "title": "反转", "logline": "线索揭晓", "full_script": "第二集剧本",
             "plot_beats": ["承接", "反转", "收束"], "ending_hook": "阶段结局", "storyboard": [second_shot]},
        ]
        plan["storyboard"] = []
        validated = validate_short_drama(plan)
        self.assertEqual([x["episode_number"] for x in validated["storyboard"]], [1, 2])
        rows = short_drama_production_rows(validated, "测试商品")
        self.assertEqual([x["episode_number"] for x in rows], [1, 2])
        self.assertTrue(rows[1]["title"].startswith("第2集"))

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
        result = generate_short_drama(FakeRouter(), {"name": "商品"}, {})
        self.assertEqual(seen["route"], "AI短剧编导")
        self.assertEqual(seen["function"], "AI短剧编导")
        self.assertEqual(len(result["storyboard"]), 1)


if __name__ == "__main__":
    unittest.main()
