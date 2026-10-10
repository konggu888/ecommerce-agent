import unittest

from ad_studio.short_drama import (
    ShortDramaPlanError, build_short_drama_prompt, generate_short_drama,
    short_drama_production_rows, validate_short_drama,
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
