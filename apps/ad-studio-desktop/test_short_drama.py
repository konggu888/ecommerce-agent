import unittest
import json

from ad_studio.short_drama import (
    ShortDramaPlanError, build_short_drama_prompt, generate_short_drama, analyze_episode_continuity_impact, product_visual_correction_suggestion,
    audit_short_drama, build_episode_continuity_ledger, short_drama_production_rows, validate_short_drama,
    generate_next_short_drama_episode, record_product_visual_verification, compare_product_visual_shot,
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
                        "motivation": "不想再次让同事失望", "fear_or_secret": "害怕被认为不可靠",
                        "relationship": "同事", "relationship_dynamics": "同事依赖其准时交接，但此前已有一次迟到",
                        "decision_pressure": "距离约定时间只剩十分钟", "arc": "从慌乱回避转向主动建立准备习惯"}],
        "plot_beats": ["意外开场", "误会升级", "商品自然解决问题", "轻松收尾"],
        "conflict_and_reversal": "主角以为问题无法解决，后来发现关键在准备方式",
        "causal_chain": [
            {"step": 1, "event": "主角发现钥匙不在固定位置", "caused_by": "开场初始条件：前一晚匆忙回家后随手放置物品",
             "character_choice": "先翻找玄关而不回想昨晚的行动", "consequence": "时间被消耗且没有找到钥匙",
             "state_change": "剩余出门时间缩短，主角压力增加", "script_evidence": "主角发现钥匙不在固定位置", "storyboard_indices": [1]},
            {"step": 2, "event": "主角沿回家路线回忆并检查收纳处", "caused_by": "第一步翻找失败，时间压力迫使其改变策略",
             "character_choice": "停止盲目翻找，按昨晚行动顺序排查", "consequence": "发现自己临时更换过放置位置",
             "state_change": "人物从慌乱转为有依据地行动，并获得新线索", "script_evidence": "主角沿回家路线回忆并检查收纳处", "storyboard_indices": [1]},
            {"step": 3, "event": "主角找到钥匙并决定建立固定归位习惯", "caused_by": "第二步发现临时放置是反复丢失的原因",
             "character_choice": "主动设置固定收纳点", "consequence": "及时出门并减少同类问题再次发生",
             "state_change": "主角获得掌控感，同事对其可靠性的担忧缓解", "script_evidence": "主角找到钥匙并决定建立固定归位习惯", "storyboard_indices": [1]}
        ],
        "story_engine": {
            "protagonist_goal": "准时出门并带齐必需物品",
            "opposing_force": "重要物品失踪且出门时间逼近",
            "stakes": "错过约定并失去同事信任",
            "escalation_steps": ["发现物品不在原处", "回想路线仍找不到", "发现误判来自临时更换收纳位置"],
            "turning_point": "主角意识到问题源于每次随手放置",
            "setup_and_payoff": "开场出现的空置收纳位在结尾成为固定归位点",
            "emotional_payoff": "从慌乱转为掌控感"
        },
        "hook_design": {
            "opening_question": "主角能否在出门前找到关键物品？",
            "retention_devices": ["不断逼近的时间", "物品去向线索逐步揭开"],
            "payoff": "开场疑问得到明确解决并展示新的习惯"
        },
        "ending": "主角从容赴约",
        "full_script": "主角发现钥匙不在固定位置。主角沿回家路线回忆并检查收纳处。主角找到钥匙并决定建立固定归位习惯。",
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
            {"title": "反转喜剧", "mechanism": "误会反转", "conflict_source": "物品丢失导致误会",
             "protagonist_choice": "承认自己放错物品还是责怪他人", "reversal_mechanism": "早期线索揭示物品一直在身边",
             "product_role": "作为整理工具帮助定位", "audience_hook": "限时寻找造成紧张感", "conversion_path": "演示后引导了解"},
            {"title": "温情日常", "mechanism": "关系变化", "conflict_source": "家人之间长期缺乏沟通",
             "protagonist_choice": "主动沟通还是继续回避", "reversal_mechanism": "旧物触发记忆并改变双方理解",
             "product_role": "作为共同整理回忆的道具", "audience_hook": "关系修复引发情感共鸣", "conversion_path": "情境共鸣后介绍"}
        ]
    }


class ShortDramaTests(unittest.TestCase):
    def test_audit_warns_when_causal_event_is_not_shown_in_referenced_shot(self):
        plan = sample_plan()
        plan["causal_chain"][0]["event"] = "主角突然打开红色保险箱"
        report = audit_short_drama(plan)
        self.assertIn("CAUSAL_EVENT_NOT_SHOWN", {item["code"] for item in report["issues"]})

    def test_audit_warns_when_turning_point_is_not_in_shots(self):
        plan = sample_plan()
        plan["story_engine"]["turning_point"] = "主角发现邻居一直在跟踪自己"
        report = audit_short_drama(plan)
        self.assertIn("TURNING_POINT_NOT_STORYBOARDED", {item["code"] for item in report["issues"]})

    def test_audit_warns_when_setup_payoff_is_not_in_shots(self):
        plan = sample_plan()
        plan["story_engine"]["setup_and_payoff"] = "开场墙上的地图最终揭示密室入口"
        report = audit_short_drama(plan)
        self.assertIn("SETUP_PAYOFF_NOT_STORYBOARDED", {item["code"] for item in report["issues"]})

    def test_audit_warns_when_relationship_change_is_not_specified(self):
        plan = sample_plan()
        plan["characters"].append({
            "name": "小王", "role": "同事", "goal": "得到帮助",
            "motivation": "希望合作顺利", "fear_or_secret": "担心被忽视",
            "relationship": "同事", "relationship_dynamics": "彼此依赖但沟通不足",
            "decision_pressure": "交接时间临近", "arc": "从怀疑转向合作"
        })
        report = audit_short_drama(plan)
        self.assertIn("RELATIONSHIP_CHANGE_UNSPECIFIED", {item["code"] for item in report["issues"]})

    def test_audit_warns_when_relationship_change_is_not_shown_in_referenced_shot(self):
        plan = sample_plan()
        plan["characters"].append({
            "name": "小王", "role": "同事", "goal": "得到帮助",
            "motivation": "希望合作顺利", "fear_or_secret": "担心被忽视",
            "relationship": "同事", "relationship_dynamics": "彼此依赖但沟通不足",
            "decision_pressure": "交接时间临近", "arc": "从怀疑转向合作"
        })
        plan["causal_chain"][0]["relationship_change"] = "小王开始信任小林"
        report = audit_short_drama(plan)
        self.assertIn("RELATIONSHIP_CHANGE_NOT_SHOWN", {item["code"] for item in report["issues"]})

    def test_audit_warns_when_state_continuity_is_not_defined(self):
        plan = sample_plan()
        plan["causal_chain"][0].pop("state_continuity", None)
        report = audit_short_drama(plan)
        self.assertIn("STATE_CONTINUITY_UNSPECIFIED", {item["code"] for item in report["issues"]})

    def test_audit_warns_when_state_continuity_references_unknown_character(self):
        plan = sample_plan()
        plan["causal_chain"][0]["state_continuity"] = {
            "affected_characters": ["不存在的人物"],
            "required_follow_through": "无后续影响",
            "storyboard_indices": [],
        }
        report = audit_short_drama(plan)
        self.assertIn("STATE_CONTINUITY_UNKNOWN_CHARACTER", {item["code"] for item in report["issues"]})

    def test_audit_warns_when_follow_through_is_not_shown_in_later_shot(self):
        plan = sample_plan()
        plan["storyboard"].append({
            "index": 3, "scene": "办公室", "location": "办公室", "characters": ["小林"],
            "action": "小林继续寻找钥匙", "dialogue": "", "product_integration": "本镜不出现商品",
            "shot_type": "中景", "duration_seconds": 4, "generation_prompt": "小林继续寻找钥匙",
        })
        plan["causal_chain"][0]["state_continuity"] = {
            "affected_characters": ["小林"],
            "required_follow_through": "小林把钥匙交给同事",
            "storyboard_indices": [3],
        }
        report = audit_short_drama(plan)
        self.assertIn("STATE_CONTINUITY_NOT_SHOWN", {item["code"] for item in report["issues"]})

    def test_audit_accepts_explicit_no_downstream_state_effect(self):
        plan = sample_plan()
        for step in plan["causal_chain"]:
            step["state_continuity"] = {
                "affected_characters": ["小林"],
                "required_follow_through": "无后续影响",
                "storyboard_indices": [],
            }
        report = audit_short_drama(plan)
        codes = {item["code"] for item in report["issues"]}
        self.assertNotIn("STATE_CONTINUITY_UNSPECIFIED", codes)
        self.assertNotIn("STATE_CONTINUITY_SHOTS_MISSING", codes)

    def test_prompt_requires_story_event_references_and_shootable_turning_point(self):
        prompt = build_short_drama_prompt({"name": "商品"}, {"drama_business_mode": "product_placement"})
        self.assertIn("narrative_function", prompt)
        self.assertIn("story_event_reference", prompt)
        self.assertIn("relationship_change", prompt)
        self.assertIn("state_continuity", prompt)
        self.assertIn("required_follow_through", prompt)
        self.assertIn("knowledge_origin", prompt)
        self.assertIn("knowledge_source_storyboard_indices", prompt)
        self.assertIn("前置线索", prompt)

    def test_audit_warns_when_action_basis_names_character_not_in_shot(self):
        plan = sample_plan()
        plan["storyboard"][0]["character_action_basis"] = [{
            "character_name": "小林", "goal_or_motivation": "准时出门",
            "known_information": "钥匙不在固定位置", "knowledge_source": "主角发现钥匙不在固定位置",
            "decision_pressure": "时间紧迫", "choice_rationale": "先翻找玄关"
        }, {
            "character_name": "小王", "goal_or_motivation": "帮忙",
            "known_information": "钥匙不在固定位置", "knowledge_source": "主角发现钥匙不在固定位置",
            "decision_pressure": "时间紧迫", "choice_rationale": "查看门口"
        }]
        report = audit_short_drama(plan)
        self.assertIn("CHARACTER_ACTION_BASIS_NOT_IN_SHOT", {item["code"] for item in report["issues"]})
        self.assertIn("CHARACTER_ACTION_BASIS_UNKNOWN_CHARACTER", {item["code"] for item in report["issues"]})

    def test_audit_warns_when_character_uses_information_revealed_later(self):
        plan = sample_plan()
        plan["storyboard"][0]["action"] = "主角发现钥匙不在固定位置"
        second = dict(plan["storyboard"][0])
        second["action"] = "小林依据尚未发生的信息作出决定"
        second["character_action_basis"] = [{
            "character_name": "小林", "goal_or_motivation": "准时出门",
            "known_information": "钥匙不在固定位置",
            "knowledge_source": "主角发现钥匙不在固定位置",
            "knowledge_origin": "storyboard", "knowledge_source_storyboard_indices": [3],
            "decision_pressure": "时间紧迫", "choice_rationale": "依据线索行动"
        }]
        third = dict(plan["storyboard"][0])
        third["action"] = "主角发现钥匙不在固定位置"
        plan["storyboard"].extend([second, third])
        report = audit_short_drama(plan)
        self.assertIn("CHARACTER_KNOWLEDGE_REVEALED_LATER", {item["code"] for item in report["issues"]})

    def test_audit_accepts_knowledge_revealed_in_an_earlier_shot(self):
        plan = sample_plan()
        plan["storyboard"][0]["action"] = "主角发现钥匙不在固定位置"
        second = dict(plan["storyboard"][0])
        second["action"] = "小林按已发现的线索检查收纳处"
        second["character_action_basis"] = [{
            "character_name": "小林", "goal_or_motivation": "准时出门",
            "known_information": "钥匙不在固定位置",
            "knowledge_source": "主角发现钥匙不在固定位置",
            "knowledge_origin": "storyboard", "knowledge_source_storyboard_indices": [1],
            "decision_pressure": "时间紧迫", "choice_rationale": "依据线索行动"
        }]
        plan["storyboard"].append(second)
        report = audit_short_drama(plan)
        codes = {item["code"] for item in report["issues"]}
        self.assertNotIn("CHARACTER_KNOWLEDGE_REVEALED_LATER", codes)
        self.assertNotIn("CHARACTER_KNOWLEDGE_SOURCE_SHOTS_MISSING", codes)
        self.assertNotIn("CHARACTER_KNOWLEDGE_SOURCE_NOT_IN_SOURCE_SHOT", codes)

    def test_audit_accepts_preexisting_knowledge_without_storyboard_source(self):
        plan = sample_plan()
        plan["storyboard"][0]["character_action_basis"] = [{
            "character_name": "小林", "goal_or_motivation": "准时出门",
            "known_information": "熟悉自家玄关布局",
            "knowledge_source": "主角发现钥匙不在固定位置",
            "knowledge_origin": "preexisting", "knowledge_source_storyboard_indices": [],
            "decision_pressure": "时间紧迫", "choice_rationale": "先检查熟悉的位置"
        }]
        report = audit_short_drama(plan)
        codes = {item["code"] for item in report["issues"]}
        self.assertNotIn("CHARACTER_KNOWLEDGE_TIMELINE_UNSPECIFIED", codes)
        self.assertNotIn("CHARACTER_KNOWLEDGE_PREEXISTING_HAS_SHOTS", codes)

    def test_audit_warns_when_action_basis_omits_character_from_character_list(self):
        plan = sample_plan()
        plan["storyboard"][0]["character_action_basis"] = [{
            "character_name": "小王", "goal_or_motivation": "帮忙",
            "known_information": "钥匙不在固定位置", "knowledge_source": "主角发现钥匙不在固定位置",
            "decision_pressure": "时间紧迫", "choice_rationale": "查看门口"
        }]
        report = audit_short_drama(plan)
        codes = {item["code"] for item in report["issues"]}
        self.assertIn("CHARACTER_ACTION_BASIS_NOT_IN_SHOT", codes)
        self.assertIn("CHARACTER_ACTION_BASIS_UNKNOWN_CHARACTER", codes)

    def test_audit_warns_when_character_action_has_no_basis(self):
        plan = sample_plan()
        report = audit_short_drama(plan)
        self.assertIn("CHARACTER_ACTION_BASIS_MISSING", {item["code"] for item in report["issues"]})

    def test_audit_warns_when_character_knowledge_source_is_not_script_evidence(self):
        plan = sample_plan()
        plan["storyboard"][0]["character_action_basis"] = [{
            "character_name": "小林",
            "goal_or_motivation": "准时出门",
            "known_information": "钥匙被邻居拿走",
            "knowledge_source": "邻居亲口承认偷走钥匙",
            "decision_pressure": "马上迟到",
            "choice_rationale": "直接去邻居家质问"
        }]
        report = audit_short_drama(plan)
        self.assertIn("CHARACTER_KNOWLEDGE_SOURCE_UNTRACEABLE", {item["code"] for item in report["issues"]})

    def test_audit_warns_when_causal_character_choice_is_not_in_referenced_shot(self):
        plan = sample_plan()
        plan["causal_chain"][0]["character_choice"] = "主角打电话向物业申请调取监控"
        report = audit_short_drama(plan)
        self.assertIn("CHARACTER_CHOICE_NOT_SHOWN", {item["code"] for item in report["issues"]})

    def test_audit_warns_for_incomplete_character_action_basis(self):
        plan = sample_plan()
        plan["storyboard"][0]["character_action_basis"] = [{"character_name": "小林", "goal_or_motivation": "准时出门"}]
        report = audit_short_drama(plan)
        self.assertIn("CHARACTER_ACTION_BASIS_INCOMPLETE", {item["code"] for item in report["issues"]})

    def test_a83_accepts_commitment_with_visible_later_fulfillment(self):
        plan = sample_plan()
        plan["storyboard"][0]["action"] = "小林当面答应小王：我会在今晚归还钥匙。"
        plan["storyboard"][0]["dialogue"] = "我会在今晚归还钥匙。"
        later = dict(plan["storyboard"][0])
        later["action"] = "小林把钥匙交还给小王，并说：我答应过今晚归还。"
        later["dialogue"] = "我答应过今晚归还。"
        plan["storyboard"].append(later)
        plan["narrative_obligations"] = [{
            "kind": "commitment", "character_name": "小林",
            "obligation": "小林承诺今晚归还钥匙",
            "origin_storyboard_index": 1, "origin_evidence": "我会在今晚归还钥匙",
            "expected_follow_through": "小林把钥匙交还给小王",
            "follow_through_storyboard_indices": [2], "status": "resolved",
            "resolution_rationale": "第2镜展示了归还动作"
        }]
        codes = {item["code"] for item in audit_short_drama(plan)["issues"]}
        self.assertNotIn("NARRATIVE_OBLIGATION_ORIGIN_NOT_SHOWN", codes)
        self.assertNotIn("NARRATIVE_OBLIGATION_FOLLOW_THROUGH_NOT_SHOWN", codes)
        self.assertNotIn("NARRATIVE_OBLIGATION_FOLLOW_SHOTS_NOT_LATER", codes)

    def test_a83_warns_when_promise_is_not_followed_through(self):
        plan = sample_plan()
        plan["storyboard"][0]["action"] = "小林当面答应小王：我会在今晚归还钥匙。"
        later = dict(plan["storyboard"][0])
        later["action"] = "小林匆忙走进电梯，没有提到钥匙。"
        plan["storyboard"].append(later)
        plan["narrative_obligations"] = [{
            "kind": "commitment", "character_name": "小林",
            "obligation": "小林承诺今晚归还钥匙",
            "origin_storyboard_index": 1, "origin_evidence": "我会在今晚归还钥匙",
            "expected_follow_through": "小林把钥匙交还给小王",
            "follow_through_storyboard_indices": [2], "status": "resolved"
        }]
        codes = {item["code"] for item in audit_short_drama(plan)["issues"]}
        self.assertIn("NARRATIVE_OBLIGATION_FOLLOW_THROUGH_NOT_SHOWN", codes)

    def test_a83_warns_on_invalid_or_nonchronological_obligation_references(self):
        plan = sample_plan()
        plan["storyboard"][0]["action"] = "小林误以为小王拿走钥匙，并开始质问小王。"
        plan["narrative_obligations"] = [
            {
                "kind": "misunderstanding", "character_name": "小林",
                "obligation": "小林误以为小王拿走钥匙",
                "origin_storyboard_index": 99, "origin_evidence": "误以为小王拿走钥匙",
                "expected_follow_through": "小林发现钥匙其实在自己的包里",
                "follow_through_storyboard_indices": [1], "status": "open"
            },
            {
                "kind": "misunderstanding", "character_name": "小林",
                "obligation": "同镜引用作为后续镜头",
                "origin_storyboard_index": 1, "origin_evidence": "主角翻找物品",
                "expected_follow_through": "小林发现钥匙其实在自己的包里",
                "follow_through_storyboard_indices": [1], "status": "open"
            }
        ]
        codes = {item["code"] for item in audit_short_drama(plan)["issues"]}
        self.assertIn("NARRATIVE_OBLIGATION_ORIGIN_INVALID", codes)
        self.assertIn("NARRATIVE_OBLIGATION_FOLLOW_SHOTS_NOT_LATER", codes)

    def test_a83_warns_when_obligation_references_unknown_character(self):
        plan = sample_plan()
        plan["narrative_obligations"] = [{
            "kind": "action_consequence", "character_name": "不存在的人物",
            "obligation": "行动造成钥匙遗失", "origin_storyboard_index": 1,
            "origin_evidence": "主角翻找物品", "expected_follow_through": "主角继续寻找钥匙",
            "follow_through_storyboard_indices": [1], "status": "open"
        }]
        codes = {item["code"] for item in audit_short_drama(plan)["issues"]}
        self.assertIn("NARRATIVE_OBLIGATION_UNKNOWN_CHARACTER", codes)
        self.assertIn("NARRATIVE_OBLIGATION_FOLLOW_SHOTS_NOT_LATER", codes)

    def _a84_multiepisode_plan(self):
        plan = sample_plan()
        first = dict(plan["storyboard"][0])
        first["episode_number"] = 1
        first["action"] = "小林答应继续追查匿名便条来源。"
        second = dict(plan["storyboard"][0])
        second["episode_number"] = 2
        second["action"] = "小林继续追查匿名便条来源，并打开旧档案。"
        state1 = {
            "opening_state": "小林收到匿名便条",
            "character_state_changes": ["小林决定追查"],
            "unresolved_threads": ["小林答应继续追查匿名便条来源"],
            "ending_state": "小林答应继续追查匿名便条来源",
            "next_episode_requirements": ["小林答应继续追查匿名便条来源"],
        }
        state2 = {
            "opening_state": "小林答应继续追查匿名便条来源",
            "character_state_changes": ["小林打开旧档案"],
            "unresolved_threads": ["便条来源仍未查明"],
            "ending_state": "小林打开旧档案",
            "next_episode_requirements": [],
        }
        plan.update({
            "format_mode": "continuous_series", "episode_count": 2,
            "episodes": [
                {"episode_number": 1, "title": "便条", "full_script": "小林收到便条并答应追查。",
                 "plot_beats": ["收到便条"], "ending_hook": "决定追查", "continuity_state": state1,
                 "storyboard": [dict(first)]},
                {"episode_number": 2, "title": "旧档案", "full_script": "小林继续追查并打开旧档案。",
                 "plot_beats": ["追查"], "ending_hook": "打开旧档案", "continuity_state": state2,
                 "storyboard": [dict(second)]},
            ],
            "storyboard": [first, second],
            "narrative_obligations": [{
                "kind": "commitment", "character_name": "小林",
                "obligation": "小林答应继续追查匿名便条来源",
                "origin_storyboard_index": 1, "origin_evidence": "答应继续追查匿名便条来源",
                "expected_follow_through": "小林继续追查匿名便条来源",
                "follow_through_storyboard_indices": [2], "status": "open",
                "cross_episode_required": True,
            }],
        })
        return plan

    def test_a84_accepts_open_obligation_carried_across_episode_boundary(self):
        plan = self._a84_multiepisode_plan()
        codes = {item["code"] for item in audit_short_drama(plan)["issues"]}
        self.assertNotIn("NARRATIVE_OBLIGATION_CROSS_EPISODE_TARGET_MISSING", codes)
        self.assertNotIn("NARRATIVE_OBLIGATION_CROSS_EPISODE_FOLLOW_THROUGH_MISSING", codes)
        self.assertNotIn("NARRATIVE_OBLIGATION_NOT_IN_EPISODE_HANDOFF", codes)
        self.assertNotIn("NARRATIVE_OBLIGATION_NOT_CARRIED_FORWARD", codes)

    def test_a84_warns_when_open_obligation_is_not_carried_to_next_episode(self):
        plan = self._a84_multiepisode_plan()
        plan["episodes"][0]["continuity_state"]["unresolved_threads"] = []
        plan["episodes"][0]["continuity_state"]["next_episode_requirements"] = []
        plan["episodes"][0]["continuity_state"]["ending_state"] = "小林回家休息"
        plan["episodes"][1]["continuity_state"]["opening_state"] = "小林开始新的一天"
        plan["episodes"][1]["continuity_state"]["unresolved_threads"] = []
        codes = {item["code"] for item in audit_short_drama(plan)["issues"]}
        self.assertIn("NARRATIVE_OBLIGATION_NOT_IN_EPISODE_HANDOFF", codes)
        self.assertIn("NARRATIVE_OBLIGATION_NOT_CARRIED_FORWARD", codes)

    def test_a84_warns_when_cross_episode_flag_is_not_boolean(self):
        plan = self._a84_multiepisode_plan()
        plan["narrative_obligations"][0]["cross_episode_required"] = "true"
        codes = {item["code"] for item in audit_short_drama(plan)["issues"]}
        self.assertIn("NARRATIVE_OBLIGATION_CROSS_EPISODE_FLAG_INVALID", codes)

    def test_a84_requires_later_episode_shot_for_cross_episode_obligation(self):
        plan = self._a84_multiepisode_plan()
        plan["narrative_obligations"][0]["follow_through_storyboard_indices"] = [1]
        codes = {item["code"] for item in audit_short_drama(plan)["issues"]}
        self.assertIn("NARRATIVE_OBLIGATION_CROSS_EPISODE_FOLLOW_THROUGH_MISSING", codes)

    def _a85_multiepisode_state_plan(self):
        plan = self._a84_multiepisode_plan()
        plan["episodes"][0]["full_script"] = "小林收到便条并答应追查。小林决定信任小王，并把秘密告诉小王。"
        plan["episodes"][1]["full_script"] = "小林继续追查并打开旧档案。小林仍信任小王，并记得便条上的秘密。"
        plan["episodes"][0]["continuity_state"]["character_state_ledger"] = [{
            "character_name": "小林", "dimension": "relationship:小林-小王信任",
            "state_description": "小林信任小王", "status": "established", "must_persist": True,
            "evidence": "小林决定信任小王", "storyboard_indices": [1],
        }]
        plan["episodes"][1]["continuity_state"]["character_state_ledger"] = [{
            "character_name": "小林", "dimension": "relationship:小林-小王信任",
            "state_description": "小林信任小王", "status": "persisting", "must_persist": True,
            "evidence": "小林仍信任小王", "storyboard_indices": [1],
        }]
        return plan

    def test_a85_accepts_persisting_character_relationship_state(self):
        plan = self._a85_multiepisode_state_plan()
        codes = {item["code"] for item in audit_short_drama(plan)["issues"]}
        self.assertNotIn("CHARACTER_STATE_NOT_CARRIED_FORWARD", codes)
        self.assertNotIn("CHARACTER_STATE_CHANGED_WITHOUT_DECLARATION", codes)
        self.assertNotIn("CHARACTER_STATE_CHANGE_UNJUSTIFIED", codes)

    def test_a85_warns_when_persistent_state_disappears_in_next_episode(self):
        plan = self._a85_multiepisode_state_plan()
        plan["episodes"][1]["continuity_state"]["character_state_ledger"] = []
        codes = {item["code"] for item in audit_short_drama(plan)["issues"]}
        self.assertIn("CHARACTER_STATE_NOT_CARRIED_FORWARD", codes)

    def test_a85_warns_when_relationship_resets_without_declared_change(self):
        plan = self._a85_multiepisode_state_plan()
        record = plan["episodes"][1]["continuity_state"]["character_state_ledger"][0]
        record["state_description"] = "小林不再信任小王"
        record["status"] = "persisting"
        codes = {item["code"] for item in audit_short_drama(plan)["issues"]}
        self.assertIn("CHARACTER_STATE_CHANGED_WITHOUT_DECLARATION", codes)

    def test_a85_requires_transition_evidence_for_declared_state_change(self):
        plan = self._a85_multiepisode_state_plan()
        record = plan["episodes"][1]["continuity_state"]["character_state_ledger"][0]
        record["state_description"] = "小林不再信任小王"
        record["status"] = "changed"
        record.pop("transition_evidence", None)
        codes = {item["code"] for item in audit_short_drama(plan)["issues"]}
        self.assertIn("CHARACTER_STATE_CHANGE_UNJUSTIFIED", codes)

    def test_a85_rejects_non_boolean_persistence_flag_and_untraceable_evidence(self):
        plan = self._a85_multiepisode_state_plan()
        record = plan["episodes"][0]["continuity_state"]["character_state_ledger"][0]
        record["must_persist"] = "yes"
        record["evidence"] = "这一句在剧本中不存在"
        codes = {item["code"] for item in audit_short_drama(plan)["issues"]}
        self.assertIn("CHARACTER_STATE_PERSIST_FLAG_INVALID", codes)
        self.assertIn("CHARACTER_STATE_EVIDENCE_UNTRACEABLE", codes)

    def _a86_changed_state_plan(self):
        plan = self._a85_multiepisode_state_plan()
        episode = plan["episodes"][1]
        episode["full_script"] = "小林看到小王藏起关键证据，因此不再信任小王。小林当面质问小王。此后小林拒绝与小王分享调查资料。"
        shots = episode["storyboard"]
        shots[0]["action"] = "小林看到小王藏起关键证据。"
        change_shot = dict(shots[0])
        change_shot["action"] = "小林意识到小王隐瞒事实，不再信任小王。"
        reaction_shot = dict(shots[0])
        reaction_shot["action"] = "小林当面质问小王为什么藏起关键证据。"
        consequence_shot = dict(shots[0])
        consequence_shot["action"] = "小林拒绝与小王分享调查资料。"
        episode["storyboard"] = [shots[0], change_shot, reaction_shot, consequence_shot]
        record = episode["continuity_state"]["character_state_ledger"][0]
        record.update({
            "state_description": "小林不再信任小王", "status": "changed",
            "transition_evidence": "小林看到小王藏起关键证据，因此不再信任小王",
            "trigger_event": "小林看到小王藏起关键证据", "trigger_storyboard_indices": [1],
            "change_storyboard_indices": [2],
            "reaction_evidence": "小林当面质问小王为什么藏起关键证据", "reaction_storyboard_indices": [3],
            "downstream_consequence_evidence": "小林拒绝与小王分享调查资料", "downstream_storyboard_indices": [4],
            "evidence": "小林意识到小王隐瞒事实，不再信任小王", "storyboard_indices": [2],
        })
        return plan

    def test_a86_accepts_ordered_character_state_causal_chain(self):
        codes = {item["code"] for item in audit_short_drama(self._a86_changed_state_plan())["issues"]}
        for code in ("CHARACTER_STATE_TRIGGER_MISSING", "CHARACTER_STATE_TRIGGER_NOT_BEFORE_CHANGE",
                     "CHARACTER_STATE_REACTION_MISSING", "CHARACTER_STATE_REACTION_NOT_LATER",
                     "CHARACTER_STATE_CONSEQUENCE_MISSING", "CHARACTER_STATE_CONSEQUENCE_NOT_LATER"):
            self.assertNotIn(code, codes)

    def test_a86_warns_when_changed_state_has_no_trigger(self):
        plan = self._a86_changed_state_plan()
        record = plan["episodes"][1]["continuity_state"]["character_state_ledger"][0]
        record.pop("trigger_event")
        record["trigger_storyboard_indices"] = []
        codes = {item["code"] for item in audit_short_drama(plan)["issues"]}
        self.assertIn("CHARACTER_STATE_TRIGGER_MISSING", codes)

    def test_a86_warns_when_trigger_follows_state_change(self):
        plan = self._a86_changed_state_plan()
        record = plan["episodes"][1]["continuity_state"]["character_state_ledger"][0]
        record["trigger_storyboard_indices"] = [3]
        record["change_storyboard_indices"] = [2]
        codes = {item["code"] for item in audit_short_drama(plan)["issues"]}
        self.assertIn("CHARACTER_STATE_TRIGGER_NOT_BEFORE_CHANGE", codes)

    def test_a86_warns_when_reaction_or_consequence_is_missing_or_out_of_order(self):
        plan = self._a86_changed_state_plan()
        record = plan["episodes"][1]["continuity_state"]["character_state_ledger"][0]
        record["reaction_evidence"] = "这句反应在剧本和分镜里不存在"
        record["reaction_storyboard_indices"] = [2]
        record["downstream_storyboard_indices"] = [2]
        codes = {item["code"] for item in audit_short_drama(plan)["issues"]}
        self.assertIn("CHARACTER_STATE_REACTION_MISSING", codes)
        self.assertIn("CHARACTER_STATE_CONSEQUENCE_NOT_LATER", codes)

    def test_a87_accepts_observable_performance_for_changed_state(self):
        plan = self._a86_changed_state_plan()
        record = plan["episodes"][1]["continuity_state"]["character_state_ledger"][0]
        plan["episodes"][1]["storyboard"][2]["action"] = "小林皱眉后退一步，抬手挡住小王，问他为什么藏起证据。"
        record["observable_manifestation"] = "小林皱眉后退一步，抬手挡住小王，问他为什么藏起证据"
        record["observable_storyboard_indices"] = [3]
        codes = {item["code"] for item in audit_short_drama(plan)["issues"]}
        self.assertNotIn("CHARACTER_STATE_MANIFESTATION_MISSING", codes)
        self.assertNotIn("CHARACTER_STATE_MANIFESTATION_NOT_SHOWN", codes)
        self.assertNotIn("CHARACTER_STATE_MANIFESTATION_TOO_ABSTRACT", codes)

    def test_a87_warns_when_state_change_has_only_abstract_emotion_label(self):
        plan = self._a86_changed_state_plan()
        record = plan["episodes"][1]["continuity_state"]["character_state_ledger"][0]
        record["observable_manifestation"] = "小林感到怀疑，态度改变"
        record["observable_storyboard_indices"] = [2]
        codes = {item["code"] for item in audit_short_drama(plan)["issues"]}
        self.assertIn("CHARACTER_STATE_MANIFESTATION_TOO_ABSTRACT", codes)

    def test_a87_warns_when_observable_manifestation_is_not_in_referenced_shot(self):
        plan = self._a86_changed_state_plan()
        record = plan["episodes"][1]["continuity_state"]["character_state_ledger"][0]
        record["observable_manifestation"] = "小林转身离开并锁上门"
        record["observable_storyboard_indices"] = [3]
        codes = {item["code"] for item in audit_short_drama(plan)["issues"]}
        self.assertIn("CHARACTER_STATE_MANIFESTATION_NOT_SHOWN", codes)

    def test_a86_prompt_requires_causal_closure_for_changed_states(self):
        prompt = build_short_drama_prompt({}, {"drama_business_mode": "general"})
        for field in ("trigger_event", "trigger_storyboard_indices", "change_storyboard_indices",
                      "reaction_evidence", "downstream_consequence_evidence"):
            self.assertIn(field, prompt)

    def test_a83_prompt_requires_tracking_commitments_misunderstandings_and_consequences(self):
        prompt = build_short_drama_prompt({}, {"drama_business_mode": "general"})
        self.assertIn("narrative_obligations", prompt)
        self.assertIn("承诺、误解和行动后果", prompt)
        self.assertIn("follow_through_storyboard_indices", prompt)

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

    def test_generation_rejects_missing_causal_chain(self):
        plan = sample_plan()
        plan.pop("causal_chain")
        class FakeRouter:
            def resolve_route(self, function): return "profile"
            def complete_json(self, profile, prompt, function=None): return plan
        with self.assertRaisesRegex(ShortDramaPlanError, "至少3步 causal_chain"):
            generate_short_drama(FakeRouter(), {"name": "商品"}, {"drama_business_mode": "product_placement"})

    def test_generation_rejects_causal_evidence_not_in_script(self):
        plan = sample_plan()
        plan["causal_chain"][0]["script_evidence"] = "剧本里没有的事件"
        class FakeRouter:
            def resolve_route(self, function): return "profile"
            def complete_json(self, profile, prompt, function=None): return plan
        with self.assertRaisesRegex(ShortDramaPlanError, "不是 full_script 原文"):
            generate_short_drama(FakeRouter(), {"name": "商品"}, {"drama_business_mode": "product_placement"})

    def test_generation_rejects_causal_chain_with_invalid_storyboard_reference(self):
        plan = sample_plan()
        plan["causal_chain"][1]["storyboard_indices"] = [99]
        class FakeRouter:
            def resolve_route(self, function): return "profile"
            def complete_json(self, profile, prompt, function=None): return plan
        with self.assertRaisesRegex(ShortDramaPlanError, "不存在的分镜位置"):
            generate_short_drama(FakeRouter(), {"name": "商品"}, {"drama_business_mode": "product_placement"})

    def test_audit_flags_causal_script_and_storyboard_mismatch(self):
        plan = sample_plan()
        plan["causal_chain"][0]["script_evidence"] = "不存在于剧本的证据"
        plan["causal_chain"][1]["storyboard_indices"] = [99]
        report = audit_short_drama(plan)
        codes = {item["code"] for item in report["issues"]}
        self.assertIn("CAUSAL_SCRIPT_MISMATCH", codes)
        self.assertIn("CAUSAL_STORYBOARD_MISMATCH", codes)

    def test_generation_rejects_causal_step_without_consequence(self):
        plan = sample_plan()
        del plan["causal_chain"][1]["consequence"]
        class FakeRouter:
            def resolve_route(self, function): return "profile"
            def complete_json(self, profile, prompt, function=None): return plan
        with self.assertRaisesRegex(ShortDramaPlanError, "因果链第2步缺少"):
            generate_short_drama(FakeRouter(), {"name": "商品"}, {"drama_business_mode": "product_placement"})

    def test_audit_warns_when_causal_chain_is_missing(self):
        plan = sample_plan()
        plan.pop("causal_chain")
        report = audit_short_drama(plan)
        self.assertIn("CAUSAL_CHAIN_INCOMPLETE", {item["code"] for item in report["issues"]})

    def test_generation_rejects_character_without_motivation_and_relationship_dynamics(self):
        plan = sample_plan()
        del plan["characters"][0]["motivation"]
        class FakeRouter:
            def resolve_route(self, function): return "profile"
            def complete_json(self, profile, prompt, function=None): return plan
        with self.assertRaisesRegex(ShortDramaPlanError, "人物缺少完整动机/关系字段"):
            generate_short_drama(FakeRouter(), {"name": "商品"}, {"drama_business_mode": "product_placement"})

    def test_audit_warns_when_character_motivation_is_missing(self):
        plan = sample_plan()
        del plan["characters"][0]["motivation"]
        report = audit_short_drama(plan)
        self.assertIn("CHARACTER_MOTIVATION_INCOMPLETE", {item["code"] for item in report["issues"]})

    def test_generation_rejects_duplicate_story_direction_mechanisms(self):
        plan = sample_plan()
        plan["alternative_directions"][1]["conflict_source"] = plan["alternative_directions"][0]["conflict_source"]
        plan["alternative_directions"][1]["protagonist_choice"] = plan["alternative_directions"][0]["protagonist_choice"]
        plan["alternative_directions"][1]["reversal_mechanism"] = plan["alternative_directions"][0]["reversal_mechanism"]
        class FakeRouter:
            def resolve_route(self, function): return "profile"
            def complete_json(self, profile, prompt, function=None): return plan
        with self.assertRaisesRegex(ShortDramaPlanError, "完全重复"):
            generate_short_drama(FakeRouter(), {"name": "商品"}, {"drama_business_mode": "product_placement"})

    def test_generation_requires_distinct_story_direction_fields(self):
        plan = sample_plan()
        del plan["alternative_directions"][0]["audience_hook"]
        class FakeRouter:
            def resolve_route(self, function): return "profile"
            def complete_json(self, profile, prompt, function=None): return plan
        with self.assertRaisesRegex(ShortDramaPlanError, "缺少完整字段"):
            generate_short_drama(FakeRouter(), {"name": "商品"}, {"drama_business_mode": "product_placement"})

    def test_generation_rejects_short_drama_without_causal_story_engine(self):
        plan = sample_plan()
        plan.pop("story_engine")
        class FakeRouter:
            def resolve_route(self, function): return "profile"
            def complete_json(self, profile, prompt, function=None): return plan
        with self.assertRaisesRegex(ShortDramaPlanError, "story_engine"):
            generate_short_drama(FakeRouter(), {"name": "商品"}, {"drama_business_mode": "product_placement"})

    def test_generation_rejects_story_with_too_few_escalation_steps(self):
        plan = sample_plan()
        plan["story_engine"]["escalation_steps"] = ["只有一步"]
        class FakeRouter:
            def resolve_route(self, function): return "profile"
            def complete_json(self, profile, prompt, function=None): return plan
        with self.assertRaisesRegex(ShortDramaPlanError, "至少需要3个具体步骤"):
            generate_short_drama(FakeRouter(), {"name": "商品"}, {"drama_business_mode": "product_placement"})

    def test_generation_prompt_requires_causal_conflict_hook_and_payoff(self):
        prompt = build_short_drama_prompt({"name": "商品"}, {"drama_business_mode": "product_placement"})
        for term in ("story_engine", "hook_design", "causal_chain", "因果步骤", "逐级升级的冲突", "伏笔", "不得只靠角色夸赞"):
            self.assertIn(term, prompt)

    def test_builds_existing_production_contract(self):
        rows = short_drama_production_rows(sample_plan(), "测试商品")
        self.assertEqual(rows[0]["duration_seconds"], 4)
        self.assertEqual(rows[0]["asset_resolution"]["actor_tags"], ["年轻上班族"])
        self.assertEqual(rows[0]["asset_resolution"]["scene_tags"], ["公寓玄关"])
        self.assertEqual(rows[0]["asset_resolution"]["product_tags"], [])
        self.assertEqual(rows[0]["director_mode"], "short_drama")

    def test_audit_flags_missing_story_engine_and_hook_design(self):
        plan = sample_plan()
        plan.pop("story_engine")
        plan.pop("hook_design")
        result = audit_short_drama(plan)
        codes = {issue["code"] for issue in result["issues"]}
        self.assertIn("STORY_ENGINE_INCOMPLETE", codes)
        self.assertIn("HOOK_DESIGN_INCOMPLETE", codes)

    def test_audit_flags_weak_escalation_and_retention_design(self):
        plan = sample_plan()
        plan["story_engine"]["escalation_steps"] = ["一步"]
        plan["hook_design"]["retention_devices"] = ["一种"]
        result = audit_short_drama(plan)
        codes = {issue["code"] for issue in result["issues"]}
        self.assertIn("STORY_ESCALATION_WEAK", codes)
        self.assertIn("RETENTION_DESIGN_WEAK", codes)

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


    def test_continuity_impact_analysis_reports_only_existing_downstream_episodes(self):
        plan = sample_plan()
        plan["format_mode"] = "continuous_series"
        plan["episode_count"] = 3
        state = lambda opening, ending, requirements: {
            "opening_state": opening, "character_state_changes": [], "unresolved_threads": [],
            "ending_state": ending, "next_episode_requirements": requirements,
        }
        plan["episodes"] = [
            {"episode_number": 1, "title": "起因", "full_script": "第一集", "plot_beats": ["起因"], "ending_hook": "线索出现",
             "continuity_state": state("主角出门", "主角拿到便条", ["第二集必须解释便条"]) , "storyboard": [dict(plan["storyboard"][0])]},
            {"episode_number": 2, "title": "追查", "full_script": "第二集", "plot_beats": ["追查"], "ending_hook": "发现旧档案",
             "continuity_state": state("主角拿着便条", "发现档案", ["第三集继续查档案"]), "storyboard": [dict(plan["storyboard"][0])]},
            {"episode_number": 3, "title": "揭晓", "full_script": "第三集", "plot_beats": ["揭晓"], "ending_hook": "结局",
             "continuity_state": state("主角查看档案", "真相揭晓", []), "storyboard": [dict(plan["storyboard"][0])]},
        ]
        plan["storyboard"] = []
        for episode in plan["episodes"]:
            for shot in episode["storyboard"]:
                shot["episode_number"] = episode["episode_number"]
                plan["storyboard"].append(shot)
        plan["continuity_ledger"] = build_episode_continuity_ledger(plan)
        seen = {}
        class FakeRouter:
            def resolve_route(self, function):
                seen["route"] = function
                return "profile"
            def complete_json(self, profile, prompt, function=None):
                seen["prompt"] = prompt
                return {
                    "source_episode_number": 1, "overall_risk": "high", "summary": "便条变化会影响后续追查",
                    "affected_episodes": [{"episode_number": 2, "risk": "high",
                        "affected_elements": ["便条"], "evidence": ["第二集开场依赖便条"],
                        "recommended_actions": ["同步修改第二集开场"]}],
                    "unaffected_reasoning": ["第三集是否受影响需先检查第二集修改结果"],
                }
        report = analyze_episode_continuity_impact(FakeRouter(), plan, 1)
        self.assertEqual(report["source_episode_number"], 1)
        self.assertTrue(report["human_review_required"])
        self.assertEqual(report["affected_episodes"][0]["episode_number"], 2)
        self.assertEqual(seen["route"], "AI短剧编导")
        self.assertIn("不要直接改写", seen["prompt"])

    def test_continuity_impact_analysis_rejects_non_downstream_episode(self):
        plan = sample_plan()
        plan["format_mode"] = "continuous_series"
        plan["episode_count"] = 2
        state = {"opening_state": "A", "character_state_changes": [], "unresolved_threads": [],
                 "ending_state": "B", "next_episode_requirements": []}
        plan["episodes"] = [
            {"episode_number": 1, "continuity_state": dict(state), "storyboard": [dict(plan["storyboard"][0])]},
            {"episode_number": 2, "continuity_state": dict(state), "storyboard": [dict(plan["storyboard"][0])]},
        ]
        plan["storyboard"] = []
        for episode in plan["episodes"]:
            shot = dict(episode["storyboard"][0])
            shot["episode_number"] = episode["episode_number"]
            plan["storyboard"].append(shot)
        class FakeRouter:
            def resolve_route(self, function): return "profile"
            def complete_json(self, profile, prompt, function=None):
                return {"source_episode_number": 1, "overall_risk": "medium", "summary": "风险",
                        "affected_episodes": [{"episode_number": 99, "risk": "high", "affected_elements": [],
                            "evidence": [], "recommended_actions": []}], "unaffected_reasoning": []}
        with self.assertRaisesRegex(ShortDramaPlanError, "不存在或非后续集数"):
            analyze_episode_continuity_impact(FakeRouter(), plan, 1)

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


    def test_product_fact_lock_warns_when_confirmed_fact_has_no_source(self):
        plan = sample_plan()
        plan["drama_business_mode"] = "product_short_drama_ad"
        plan["product_analysis"] = {"product_type": "用品", "target_audience": "普通用户", "selling_points": [], "usage_scenarios": [], "unknown_facts": ["续航24小时"]}
        plan["genre_decision"] = {"selected_genre": "现实轻喜剧", "reasoning": "用于测试"}
        plan["storyboard"][0]["product_fidelity_constraints"] = ["保持真实外观与功能"]
        plan["product_fact_lock"] = {"confirmed_facts": ["耐热200度"], "unknown_or_unverified": ["续航24小时"], "appearance_structure_function_constraints": ["保持真实外观"]}
        plan["full_script"] = "这款产品耐热200度，续航24小时。"
        report = audit_short_drama(plan, {"name": "商品", "description": "普通收纳用品"})
        codes = {item["code"] for item in report["issues"]}
        self.assertIn("PRODUCT_CONFIRMED_FACT_UNSUPPORTED", codes)
        self.assertIn("PRODUCT_UNKNOWN_FACT_USED", codes)

    def test_product_fact_lock_allows_unknown_fact_marked_unverified(self):
        plan = sample_plan()
        plan["drama_business_mode"] = "product_short_drama_ad"
        plan["product_analysis"] = {"product_type": "用品", "target_audience": "普通用户", "selling_points": [], "usage_scenarios": [], "unknown_facts": ["续航24小时"]}
        plan["genre_decision"] = {"selected_genre": "现实轻喜剧", "reasoning": "用于测试"}
        plan["storyboard"][0]["product_fidelity_constraints"] = ["保持真实外观与功能"]
        plan["product_fact_lock"] = {"confirmed_facts": [], "unknown_or_unverified": ["续航24小时"], "appearance_structure_function_constraints": ["保持真实外观"]}
        plan["full_script"] = "续航24小时尚未核实，不得作为宣传结论。"
        report = audit_short_drama(plan, {"name": "商品", "description": "普通用品"})
        self.assertNotIn("PRODUCT_UNKNOWN_FACT_USED", {item["code"] for item in report["issues"]})
    def test_audit_warns_for_selling_point_not_in_shot_text(self):
        plan = sample_plan()
        plan["drama_business_mode"] = "product_placement"
        plan["product_analysis"] = {"selling_points": ["foldable storage"]}
        for shot in plan["storyboard"]:
            shot["product_integration"] = "product sits on a table"
            shot["action"] = "person enters the room and sits down"
        report = audit_short_drama(plan, {"name": "storage item", "description": "daily use"})
        self.assertIn("PRODUCT_SELLING_POINT_NOT_SHOWN", {item["code"] for item in report["issues"]})

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


    def test_product_ad_visual_status_is_reset_on_generation(self):
        class FakeRouter:
            def resolve_route(self, function): return "profile"
            def complete_json(self, profile, prompt, function=None):
                plan = sample_plan()
                plan["drama_business_mode"] = "product_short_drama_ad"
                plan["product_analysis"] = {"product_type": "用品"}
                plan["genre_decision"] = {"selected_genre": "古代", "reasoning": "适合故事"}
                plan["product_fact_lock"] = {"confirmed_facts": [], "unknown_or_unverified": []}
                plan["storyboard"][0]["product_fidelity_constraints"] = ["保持真实外观"]
                plan["storyboard"][0]["visual_verification"] = "passed"
                return plan
        result = generate_short_drama(FakeRouter(), {"name": "商品"}, {"drama_business_mode": "product_short_drama_ad"})
        self.assertEqual(result["storyboard"][0]["visual_verification"], "not_checked")


    def test_manual_product_visual_review_requires_evidence_and_note(self):
        plan = sample_plan()
        plan["drama_business_mode"] = "product_short_drama_ad"
        with self.assertRaisesRegex(ShortDramaPlanError, "必须选择实际生成的图片或视频"):
            record_product_visual_verification(plan, 1, "passed", "", "外观和功能一致")
        with self.assertRaisesRegex(ShortDramaPlanError, "核验备注"):
            record_product_visual_verification(plan, 1, "passed", "C:/renders/shot-01.png", "")
        with self.assertRaisesRegex(ShortDramaPlanError, "镜头编号不存在"):
            record_product_visual_verification(plan, 2, "passed", "C:/renders/shot-01.png", "已核验")

    def test_passed_visual_status_without_manual_evidence_is_still_flagged(self):
        plan = sample_plan()
        plan["drama_business_mode"] = "product_short_drama_ad"
        plan["product_analysis"] = {"product_type": "用品"}
        plan["genre_decision"] = {"selected_genre": "古代", "reasoning": "适合故事"}
        plan["product_fact_lock"] = {
            "confirmed_facts": ["外观以参考图为准"],
            "unknown_or_unverified": ["未确认参数"],
            "appearance_structure_function_constraints": ["不得改变商品外观、结构和功能"],
        }
        plan["storyboard"][0]["product_fidelity_constraints"] = ["保持外观、结构、功能及正确用法"]
        plan["storyboard"][0]["visual_verification"] = "passed"
        report = audit_short_drama(plan, {"name": "商品"})
        self.assertIn("PRODUCT_VISUAL_NOT_VERIFIED", {issue["code"] for issue in report["issues"]})

    def test_audit_rejects_stale_or_missing_manual_visual_evidence(self):
        import tempfile
        from pathlib import Path

        plan = sample_plan()
        plan["drama_business_mode"] = "product_short_drama_ad"
        plan["product_analysis"] = {"product_type": "用品"}
        plan["genre_decision"] = {"selected_genre": "古代", "reasoning": "测试用题材理由"}
        plan["product_fact_lock"] = {
            "confirmed_facts": ["外观以参考图为准"],
            "unknown_or_unverified": ["未确认参数"],
            "appearance_structure_function_constraints": ["不得改变商品外观、结构和功能"],
        }
        shot = plan["storyboard"][0]
        shot["product_fidelity_constraints"] = ["保持外观、结构、功能及正确用法"]
        shot.update({
            "visual_verification": "passed",
            "visual_verification_method": "manual",
            "visual_verification_evidence": "C:/old-render/shot-01.png",
            "visual_verification_note": "曾经人工核验",
        })
        report = audit_short_drama(plan, {"name": "商品"})
        self.assertIn("PRODUCT_VISUAL_NOT_VERIFIED", {issue["code"] for issue in report["issues"]})

        with tempfile.TemporaryDirectory() as folder:
            evidence = Path(folder) / "shot-01.png"
            evidence.write_bytes(b"real image evidence")
            shot["visual_verification_evidence"] = str(evidence)
            report = audit_short_drama(plan, {"name": "商品"})
            self.assertNotIn("PRODUCT_VISUAL_NOT_VERIFIED", {issue["code"] for issue in report["issues"]})

            # Evidence can become stale after a prior pass; re-audit must revoke
            # current trust rather than relying on the historical passed flag.
            evidence.unlink()
            report_after_delete = audit_short_drama(plan, {"name": "商品"})
            self.assertIn("PRODUCT_VISUAL_NOT_VERIFIED", {issue["code"] for issue in report_after_delete["issues"]})

    def test_manual_product_visual_review_persists_real_evidence(self):
        import tempfile
        from pathlib import Path

        plan = sample_plan()
        plan["drama_business_mode"] = "product_short_drama_ad"
        with tempfile.TemporaryDirectory() as folder:
            evidence = Path(folder) / "shot-01.png"
            evidence.write_bytes(b"image evidence")
            reviewed = record_product_visual_verification(
                plan, 1, "passed", str(evidence), "外观、结构、功能及正确用法均与商品资料一致"
            )
            shot = reviewed["storyboard"][0]
            self.assertEqual(shot["visual_verification"], "passed")
            self.assertEqual(shot["visual_verification_evidence"], str(evidence.resolve()))
            self.assertEqual(shot["visual_verification_method"], "manual")
            self.assertIn("外观、结构", shot["visual_verification_note"])

    def test_manual_product_visual_review_rejects_missing_empty_or_unsupported_evidence(self):
        import tempfile
        from pathlib import Path

        plan = sample_plan()
        plan["drama_business_mode"] = "product_short_drama_ad"
        with tempfile.TemporaryDirectory() as folder:
            empty = Path(folder) / "empty.png"
            empty.touch()
            unsupported = Path(folder) / "notes.txt"
            unsupported.write_text("not visual evidence", encoding="utf-8")
            with self.assertRaisesRegex(ShortDramaPlanError, "不存在、为空或无法读取"):
                record_product_visual_verification(
                    plan, 1, "passed", str(Path(folder) / "missing.png"), "已对照商品检查"
                )
            with self.assertRaisesRegex(ShortDramaPlanError, "不存在、为空或无法读取"):
                record_product_visual_verification(plan, 1, "passed", str(empty), "已对照商品检查")
            with self.assertRaisesRegex(ShortDramaPlanError, "受支持的图片或视频"):
                record_product_visual_verification(plan, 1, "passed", str(unsupported), "已对照商品检查")


    def test_ai_visual_comparison_flags_mismatch_without_auto_approval(self):
        import tempfile
        from pathlib import Path

        class VisionProfile:
            id = "vision-test"
            name = "vision-test"
            vision_enabled = True

        class FakeRouter:
            def resolve_route(self, function):
                self.function = function
                return VisionProfile()

            def complete_json(self, profile, prompt, function=None, image_paths=None):
                self.image_paths = image_paths
                return {
                    "identity_match": True, "appearance_match": False,
                    "structure_match": True, "function_match": None, "usage_match": True,
                    "mismatch_detected": True, "confidence": 0.91,
                    "issues": ["商品颜色疑似不一致"], "summary": "发现疑似颜色不一致，需人工确认",
                }

        with tempfile.TemporaryDirectory() as folder:
            ref = Path(folder) / "reference.png"
            generated = Path(folder) / "shot.png"
            ref.write_bytes(b"fake-image-reference")
            generated.write_bytes(b"fake-generated-image")
            plan = sample_plan()
            plan["drama_business_mode"] = "product_short_drama_ad"
            router = FakeRouter()
            result = compare_product_visual_shot(router, plan, 1, [str(ref)], str(generated))
            shot = result["storyboard"][0]
            self.assertEqual(router.function, "商品画面视觉核验")
            self.assertEqual(shot["visual_verification"], "failed")
            self.assertEqual(shot["visual_verification_method"], "ai_vision_assisted")
            self.assertTrue(shot["visual_comparison_result"]["requires_human_review"])
            self.assertEqual(shot["visual_verification_reference_images"], [str(ref)])

    def test_ai_visual_comparison_never_auto_approves_a_match(self):
        import tempfile
        from pathlib import Path

        class VisionProfile:
            id = "vision-test"
            name = "vision-test"
            vision_enabled = True

        class FakeRouter:
            def resolve_route(self, function):
                return VisionProfile()

            def complete_json(self, profile, prompt, function=None, image_paths=None):
                return {
                    "identity_match": True, "appearance_match": True,
                    "structure_match": True, "function_match": True, "usage_match": True,
                    "mismatch_detected": False, "confidence": 0.99,
                    "issues": [], "summary": "未发现明显差异",
                }

        with tempfile.TemporaryDirectory() as folder:
            ref = Path(folder) / "reference.jpg"
            generated = Path(folder) / "shot.jpg"
            ref.write_bytes(b"fake-reference")
            generated.write_bytes(b"fake-generated")
            plan = sample_plan()
            plan["drama_business_mode"] = "product_short_drama_ad"
            result = compare_product_visual_shot(FakeRouter(), plan, 1, [str(ref)], str(generated))
            self.assertEqual(result["storyboard"][0]["visual_verification"], "needs_review")
            self.assertEqual(result["storyboard"][0]["visual_verification_method"], "ai_vision_assisted")

    def test_ai_visual_comparison_rejects_missing_reference_and_wrong_mode(self):
        import tempfile
        from pathlib import Path

        class FakeRouter:
            pass

        with tempfile.TemporaryDirectory() as folder:
            generated = Path(folder) / "shot.png"
            generated.write_bytes(b"fake-generated")
            plan = sample_plan()
            plan["drama_business_mode"] = "general_ai_drama"
            with self.assertRaisesRegex(ShortDramaPlanError, "只适用于"):
                compare_product_visual_shot(FakeRouter(), plan, 1, [str(generated)], str(generated))
            plan["drama_business_mode"] = "product_short_drama_ad"
            with self.assertRaisesRegex(ShortDramaPlanError, "至少选择一张"):
                compare_product_visual_shot(FakeRouter(), plan, 1, [], str(generated))


    def test_ai_visual_comparison_rejects_empty_and_unsupported_files(self):
        import tempfile
        from pathlib import Path

        class FakeRouter:
            pass

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            plan = sample_plan()
            plan["drama_business_mode"] = "product_short_drama_ad"
            empty_ref = root / "empty.png"
            empty_ref.write_bytes(b"")
            generated = root / "shot.png"
            generated.write_bytes(b"image-bytes")
            with self.assertRaisesRegex(ShortDramaPlanError, "为空"):
                compare_product_visual_shot(FakeRouter(), plan, 1, [str(empty_ref)], str(generated))

            unsupported_ref = root / "reference.pdf"
            unsupported_ref.write_bytes(b"pdf-bytes")
            with self.assertRaisesRegex(ShortDramaPlanError, "必须是"):
                compare_product_visual_shot(FakeRouter(), plan, 1, [str(unsupported_ref)], str(generated))

            empty_generated = root / "empty-output.png"
            empty_generated.write_bytes(b"")
            valid_ref = root / "reference.png"
            valid_ref.write_bytes(b"reference-bytes")
            with self.assertRaisesRegex(ShortDramaPlanError, "为空"):
                compare_product_visual_shot(FakeRouter(), plan, 1, [str(valid_ref)], str(empty_generated))

            unsupported_generated = root / "output.bin"
            unsupported_generated.write_bytes(b"unknown-format")
            with self.assertRaisesRegex(ShortDramaPlanError, "仅支持常见图片格式"):
                compare_product_visual_shot(FakeRouter(), plan, 1, [str(valid_ref)], str(unsupported_generated))

    def test_a58_invalid_visual_evidence_never_calls_vision_router_or_mutates_plan(self):
        import tempfile
        from pathlib import Path

        class CountingRouter:
            def __init__(self):
                self.calls = 0
            def resolve_route(self, function):
                self.calls += 1
                raise AssertionError(f"vision route must not be called for invalid evidence: {function}")
            def complete_json(self, *args, **kwargs):
                self.calls += 1
                raise AssertionError("vision completion must not be called for invalid evidence")

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            valid_ref = root / "reference.png"
            valid_ref.write_bytes(b"reference-bytes")
            valid_generated = root / "generated.png"
            valid_generated.write_bytes(b"generated-bytes")
            empty_ref = root / "empty-reference.png"
            empty_ref.write_bytes(b"")
            unsupported_ref = root / "reference.pdf"
            unsupported_ref.write_bytes(b"pdf-bytes")
            empty_generated = root / "empty-generated.png"
            empty_generated.write_bytes(b"")
            unsupported_generated = root / "generated.bin"
            unsupported_generated.write_bytes(b"unknown-bytes")
            missing_ref = root / "missing-reference.png"
            missing_generated = root / "missing-generated.png"

            invalid_cases = [
                ([str(missing_ref)], str(valid_generated)),
                ([str(empty_ref)], str(valid_generated)),
                ([str(unsupported_ref)], str(valid_generated)),
                ([str(valid_ref)], str(missing_generated)),
                ([str(valid_ref)], str(empty_generated)),
                ([str(valid_ref)], str(unsupported_generated)),
            ]
            for refs, target in invalid_cases:
                plan = sample_plan()
                plan["drama_business_mode"] = "product_short_drama_ad"
                before = json.dumps(plan, ensure_ascii=False, sort_keys=True)
                router = CountingRouter()
                with self.assertRaises(ShortDramaPlanError):
                    compare_product_visual_shot(router, plan, 1, refs, target)
                self.assertEqual(router.calls, 0)
                self.assertEqual(json.dumps(plan, ensure_ascii=False, sort_keys=True), before)

    def test_product_drama_regeneration_changes_only_selected_shot_and_preserves_history(self):
        from ad_studio.short_drama import prepare_product_drama_shot_regeneration
        plan = sample_plan()
        plan["drama_business_mode"] = "product_short_drama_ad"
        plan["storyboard"][0].update({"visual_verification":"failed","visual_verification_method":"ai_vision_assisted","visual_verification_evidence":"/tmp/old-shot.mp4","visual_verification_note":"颜色疑似不一致","visual_comparison_result":{"result":{"mismatch_detected":True}}})
        second = json.dumps(plan["storyboard"][1], ensure_ascii=False, sort_keys=True) if len(plan["storyboard"]) > 1 else None
        updated = prepare_product_drama_shot_regeneration(plan, 1, "商品颜色应与参考图一致，不改变瓶盖和标签结构", previous_version=3, previous_video_path="/tmp/old-shot.mp4", estimated_cost_rmb=0.72)
        target = updated["storyboard"][0]
        self.assertEqual(target["visual_verification"], "not_checked")
        self.assertNotIn("visual_comparison_result", target)
        self.assertEqual(target["regeneration_history"][0]["version"], 3)
        self.assertEqual(target["regeneration_history"][0]["visual_verification"], "failed")
        self.assertIn("商品颜色应与参考图一致", target["generation_prompt"])
        self.assertEqual(plan["storyboard"][0]["visual_verification"], "failed")
        if second is not None:
            self.assertEqual(json.dumps(updated["storyboard"][1], ensure_ascii=False, sort_keys=True), second)

    def test_product_drama_regeneration_rejects_wrong_mode_and_empty_correction(self):
        from ad_studio.short_drama import prepare_product_drama_shot_regeneration
        plan = sample_plan()
        with self.assertRaisesRegex(ShortDramaPlanError, "只适用于"):
            prepare_product_drama_shot_regeneration(plan, 1, "fix", previous_version=1)
        plan["drama_business_mode"] = "product_short_drama_ad"
        with self.assertRaisesRegex(ShortDramaPlanError, "修正要求"):
            prepare_product_drama_shot_regeneration(plan, 1, " ", previous_version=1)



    def test_product_visual_correction_suggestion_uses_review_findings_as_editable_draft(self):
        plan = sample_plan()
        plan["drama_business_mode"] = "product_short_drama_ad"
        plan["storyboard"][0]["visual_comparison_result"] = {
            "result": {
                "summary": "标签颜色与参考图疑似不一致",
                "mismatch_detected": True,
                "issues": ["标签颜色偏蓝", {"description": "瓶盖结构不清晰"}],
            }
        }
        draft = product_visual_correction_suggestion(plan, 1)
        self.assertIn("标签颜色与参考图疑似不一致", draft)
        self.assertIn("\n待检查问题：标签颜色偏蓝", draft)
        self.assertIn("标签颜色偏蓝", draft)
        self.assertIn("瓶盖结构不清晰", draft)
        self.assertEqual(product_visual_correction_suggestion(plan, 99), "")
        plan["drama_business_mode"] = "product_placement"
        self.assertEqual(product_visual_correction_suggestion(plan, 1), "")

    def test_product_drama_regeneration_rejects_non_finite_cost_and_invalid_version(self):
        from ad_studio.short_drama import prepare_product_drama_shot_regeneration
        plan = sample_plan()
        plan["drama_business_mode"] = "product_short_drama_ad"
        with self.assertRaisesRegex(ShortDramaPlanError, "有限的非负数"):
            prepare_product_drama_shot_regeneration(
                plan, 1, "保持商品结构", previous_version=1, estimated_cost_rmb=float("nan")
            )
        with self.assertRaisesRegex(ShortDramaPlanError, "正整数"):
            prepare_product_drama_shot_regeneration(
                plan, 1, "保持商品结构", previous_version=0, estimated_cost_rmb=0.72
            )


    def test_product_drama_shot_mapping_uses_stable_storyboard_index_after_insertions(self):
        from ad_studio.short_drama import resolve_product_drama_shot_number
        plan = {
            "drama_business_mode": "product_short_drama_ad",
            "episode_count": 1,
            "storyboard": [{"scene": "卧室"}, {"scene": "厨房"}],
        }
        # Project index has shifted after an extra reviewed shot was inserted.
        project_shot = {
            "index": 4,
            "title": "卧室",
            "episode_number": 1,
            "short_drama_shot_number": 1,
        }
        self.assertEqual(resolve_product_drama_shot_number(plan, project_shot), 1)

    def test_product_drama_legacy_shot_mapping_uses_unique_title_and_episode(self):
        from ad_studio.short_drama import resolve_product_drama_shot_number
        plan = {
            "drama_business_mode": "product_short_drama_ad",
            "episode_count": 1,
            "storyboard": [{"scene": "卧室"}, {"scene": "厨房"}],
        }
        legacy_shot = {"index": 3, "title": "厨房", "episode_number": 1}
        self.assertEqual(resolve_product_drama_shot_number(plan, legacy_shot), 2)

    def test_product_drama_ambiguous_legacy_mapping_fails_closed(self):
        from ad_studio.short_drama import resolve_product_drama_shot_number
        plan = {
            "drama_business_mode": "product_short_drama_ad",
            "episode_count": 1,
            "storyboard": [{"scene": "卧室"}, {"scene": "卧室"}],
        }
        legacy_shot = {"index": 4, "title": "卧室", "episode_number": 1}
        with self.assertRaisesRegex(ShortDramaPlanError, "无法唯一定位|标题在短剧分镜中重复"):
            resolve_product_drama_shot_number(plan, legacy_shot)




    def test_a90_series_asset_ids_are_bound_to_production_rows(self):
        plan = sample_plan()
        plan["series_asset_locks"] = [
            {"asset_type": "actor", "asset_key": "lead", "target": "小林", "canonical_description": "固定演员", "asset_id": "actor-fixed"},
            {"asset_type": "scene", "asset_key": "home", "target": "公寓玄关", "canonical_description": "固定布景", "asset_id": "scene-fixed"},
        ]
        rows = short_drama_production_rows(plan, "测试商品")
        self.assertEqual(rows[0]["asset_resolution"]["actor_asset_id"], "actor-fixed")
        self.assertEqual(rows[0]["asset_resolution"]["scene_asset_id"], "scene-fixed")
        self.assertTrue(rows[0]["asset_resolution"]["generation_if_missing"])  # unlocked product/other assets may still generate

    def test_a90_legacy_series_asset_locks_keep_tag_matching(self):
        plan = sample_plan()
        plan["series_asset_locks"] = [{"asset_type": "actor", "asset_key": "lead", "target": "小林", "canonical_description": "固定演员"}]
        rows = short_drama_production_rows(plan, "测试商品")
        self.assertIsNone(rows[0]["asset_resolution"]["actor_asset_id"])
        self.assertTrue(rows[0]["asset_resolution"]["generation_if_missing"])

    def test_a89_series_asset_locks_flow_into_production_requirements(self):
        plan = sample_plan()
        plan["series_asset_locks"] = [
            {"asset_type": "actor", "asset_key": "lead-01", "target": "小林",
             "canonical_description": "同一张脸、短黑发、深蓝通勤外套"},
            {"asset_type": "scene", "asset_key": "home-entry", "target": "现代公寓",
             "canonical_description": "同一玄关布局、浅木色鞋柜与左侧挂钩"},
        ]
        validated = validate_short_drama(plan)
        shot = validated["storyboard"][0]
        self.assertTrue(any("lead-01" in item and "短黑发" in item for item in shot["actor_requirements"]))
        self.assertTrue(any("home-entry" in item and "浅木色鞋柜" in item for item in shot["scene_requirements"]))
        rows = short_drama_production_rows(plan, "测试商品")
        self.assertTrue(any("lead-01" in item for item in rows[0]["asset_resolution"]["actor_tags"]))
        self.assertTrue(any("home-entry" in item for item in rows[0]["asset_resolution"]["scene_tags"]))

    def test_a89_asset_locks_can_be_episode_scoped_and_bad_schema_is_rejected(self):
        plan = sample_plan()
        plan["series_asset_locks"] = [{"asset_type": "actor", "asset_key": "lead-01", "target": "小林",
            "canonical_description": "固定身份外观", "episode_numbers": [2]}]
        validated = validate_short_drama(plan)
        self.assertFalse(any("lead-01" in item for item in validated["storyboard"][0]["actor_requirements"]))
        plan["series_asset_locks"][0]["episode_numbers"] = [True]
        with self.assertRaises(ShortDramaPlanError):
            validate_short_drama(plan)

    def test_a89_warns_when_asset_lock_target_does_not_match_any_shot(self):
        plan = sample_plan()
        plan["series_asset_locks"] = [{"asset_type": "actor", "asset_key": "missing", "target": "不存在的人物",
            "canonical_description": "固定外观"}]
        codes = {item["code"] for item in audit_short_drama(plan)["issues"]}
        self.assertIn("SERIES_ASSET_LOCK_TARGET_NOT_FOUND", codes)

    def test_a88_checks_cross_character_consistency_but_allows_different_beliefs(self):
        plan = sample_plan()
        plan["characters"].append({"name": "小王", "role": "同事", "goal": "帮忙", "motivation": "合作",
            "fear_or_secret": "无", "relationship": "同事", "relationship_dynamics": "合作",
            "decision_pressure": "时间紧", "arc": "积极行动"})
        def run(rule, claim_b):
            episode = {"episode_number": 1, "full_script": "小林认为钥匙在玄关，小王谈到钥匙位置。",
                "storyboard": [{"index": 1, "action": "小林认为钥匙在玄关，小王谈到钥匙位置。", "dialogue": ""}],
                "continuity_state": {"opening_state": "人物处于初始状态", "character_state_changes": [], "unresolved_threads": [], "ending_state": "本集状态已记录", "next_episode_requirements": [], "cross_character_dependencies": [{
                    "character_a": "小林", "character_b": "小王", "dependency_key": "key_location",
                    "dependency_type": "knowledge_alignment", "consistency_rule": rule,
                    "character_a_claim": "知道钥匙在玄关", "character_b_claim": claim_b,
                    "evidence": "小林认为钥匙在玄关，小王谈到钥匙位置", "storyboard_indices": [1]}]}}
            return {i["code"] for i in audit_short_drama({"format_mode": "continuous_series", "episode_count": 1, "episodes": [episode], **plan})["issues"]}
        self.assertIn("CROSS_CHARACTER_DEPENDENCY_CONTRADICTION", run("same_understanding", "认为钥匙在办公室"))
        self.assertNotIn("CROSS_CHARACTER_DEPENDENCY_CONTRADICTION", run("different_beliefs_allowed", "认为钥匙在办公室"))
        self.assertIn("CROSS_CHARACTER_ASYMMETRY_UNEXPLAINED", run("asymmetric_knowledge", "不知道钥匙位置"))

    def test_a88_warns_for_unknown_character_and_invalid_reference(self):
        plan = sample_plan()
        episode = {"episode_number": 1, "full_script": "小林没有告诉小王钥匙的位置。",
            "storyboard": [{"index": 1, "action": "小林没有告诉小王钥匙的位置。", "dialogue": ""}],
            "continuity_state": {"opening_state": "人物处于初始状态", "character_state_changes": [], "unresolved_threads": [], "ending_state": "本集状态已记录", "next_episode_requirements": [], "cross_character_dependencies": [{
                "character_a": "小林", "character_b": "不存在的人物", "dependency_key": "x",
                "dependency_type": "knowledge_alignment", "consistency_rule": "asymmetric_knowledge",
                "character_a_claim": "知道位置", "character_b_claim": "不知道位置",
                "evidence": "小林没有告诉小王钥匙的位置", "storyboard_indices": [9]}]}}
        codes = {i["code"] for i in audit_short_drama({"format_mode": "continuous_series", "episode_count": 1, "episodes": [episode], **plan})["issues"]}
        self.assertIn("CROSS_CHARACTER_DEPENDENCY_CHARACTERS_INVALID", codes)
        self.assertIn("CROSS_CHARACTER_DEPENDENCY_SHOTS_INVALID", codes)


    def test_product_drama_regeneration_preserves_unknown_cost_instead_of_zero(self):
        from ad_studio.short_drama import prepare_product_drama_shot_regeneration

        plan = {
            "drama_business_mode": "product_short_drama_ad",
            "storyboard": [{
                "generation_prompt": "keep product unchanged",
                "visual_verification": "failed",
            }],
        }
        updated = prepare_product_drama_shot_regeneration(
            plan, 1, "保留商品外观和结构",
            previous_version=2,
            estimated_cost_rmb=None,
            estimated_cost_status="price_missing",
        )
        history = updated["storyboard"][0]["regeneration_history"][0]
        self.assertIsNone(history["estimated_cost_rmb"])
        self.assertEqual(history["estimated_cost_status"], "price_missing")

        with self.assertRaisesRegex(Exception, "未知/未配置价格不能用数字金额伪装"):
            prepare_product_drama_shot_regeneration(
                plan, 1, "保留商品外观和结构",
                previous_version=2,
                estimated_cost_rmb=0.0,
                estimated_cost_status="price_missing",
            )

if __name__ == "__main__":
    unittest.main()
