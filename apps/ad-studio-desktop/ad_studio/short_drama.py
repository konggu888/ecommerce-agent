"""Standalone AI short-drama director planning and deterministic pre-production audit, separate from the existing ad workflow.

This module creates a story-first drama package. It does not overwrite the
existing ad creative plan or silently trigger paid asset/video generation.
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


SHORT_DRAMA_SCHEMA = {
    "format_mode": "single_episode / continuous_series / anthology_series",
    "episode_count": "integer",
    "series_bible": {"series_arc": "全剧主线", "character_state": "人物长期状态与关系", "continuity_rules": ["跨集必须保持的事实"]},
    "episodes": [{"episode_number": "integer", "title": "集名", "logline": "本集梗概", "plot_beats": ["本集节拍"], "ending_hook": "本集结尾/悬念", "full_script": "本集完整剧本", "continuity_state": {"opening_state": "本集开始时承接的剧情/人物状态", "character_state_changes": ["本集人物状态或关系的变化"], "character_state_ledger": [{"character_name": "人物姓名", "dimension": "心理/知识/秘密/承诺/关系等状态维度；关系可用关系:人物A-人物B", "state_description": "本集结束时该维度的明确状态", "status": "established / changed / persisting / resolved", "must_persist": "boolean；true 表示下一集仍需保持或明确转变", "evidence": "剧本或分镜中可定位的状态证据", "storyboard_indices": ["本集分镜从1开始的位置"], "transition_evidence": "状态变化时解释变化原因的可定位证据", "trigger_event": "直接触发状态变化的具体事件/信息", "trigger_storyboard_indices": ["触发事件所在的本集分镜位置"], "change_storyboard_indices": ["状态实际改变发生的本集分镜位置"], "reaction_evidence": "人物对触发事件的可定位反应", "reaction_storyboard_indices": ["反应所在的本集分镜位置"], "downstream_consequence_evidence": "状态变化影响后续行动/选择的可定位证据", "downstream_storyboard_indices": ["后续影响所在的本集分镜位置"], "observable_manifestation": "人物状态变化在镜头中可观察到的具体动作/台词/表情或互动，不要只写心理标签", "observable_storyboard_indices": ["直接表现该状态变化的本集分镜位置"]}], "unresolved_threads": ["本集结束后仍未解决的悬念/冲突"], "ending_state": "本集结束时可供后续承接的事实状态", "next_episode_requirements": ["下一集必须承接的事件/事实；最终集可为空列表"]}, "storyboard": ["本集分镜，字段与根级 storyboard 相同"]}],
    "continuity_ledger": [{"episode_number": "integer", "opening_state": "承接状态", "character_state_changes": ["人物状态变化"], "unresolved_threads": ["未解决线索"], "ending_state": "集末状态", "next_episode_requirements": ["下一集承接要求"]}],
    "drama_business_mode": "通用AI短剧/商品植入短剧/商品转化短剧/AI短剧形式商品广告",
    "product_analysis": {"product_type": "商品类型", "target_audience": "目标人群", "selling_points": ["已确认卖点"], "usage_scenarios": ["使用场景"], "unknown_facts": ["未知或待确认信息"]},
    "genre_decision": {"selected_genre": "自主选择的题材", "reasoning": "选择理由", "world_style": "时代与世界设定", "story_product_role": "商品在剧情中的自然作用"},
    "product_fact_lock": {"confirmed_facts": ["已确认事实"], "unknown_or_unverified": ["未核实事实"], "appearance_structure_function_constraints": ["外观/结构/功能约束"], "reference_assets_required": ["参考商品素材要求"], "do_not_change": ["不可改变项"]},
    "genre": "AI根据创作目标、人群、卖点和场景自主判断的短剧题材",
    "genre_reasoning": "为什么该题材适合这个商品与目标受众",
    "logline": "一句话故事梗概",
    "premise": "故事前提与核心创意机制",
    "world": "故事世界、时代、地点和风格",
    "characters": [{
        "name": "人物名",
        "role": "人物作用",
        "goal": "人物目标",
        "motivation": "目标背后的深层动机",
        "fear_or_secret": "人物害怕失去的东西或影响选择的秘密；没有则明确说明",
        "relationship": "与其他人物的关系",
        "relationship_dynamics": "关系中的利益冲突、依赖、误解或权力变化",
        "decision_pressure": "迫使人物作出选择的具体压力",
        "arc": "人物如何因事件和选择而改变"
    }],
    "plot_beats": ["开场钩子", "矛盾升级", "转折/反转", "结局"],
    "conflict_and_reversal": "核心冲突与反转逻辑",
    "causal_chain": [{
        "step": "integer",
        "event": "本步发生的具体事件",
        "caused_by": "直接导致本事件的前置行动、决定或新信息；开场可写初始条件",
        "character_choice": "人物在本步作出的选择；若无主动选择，说明原因",
        "consequence": "本事件直接造成的后果",
        "state_change": "本步结束后人物处境、关系、信息或资源发生的可观察变化",
        "relationship_change": "本步对人物之间信任、利益、误解、依赖或权力关系的可观察影响；若无变化，明确写无变化及原因",
        "state_continuity": {"affected_characters": ["受本步状态变化影响的人物姓名"], "required_follow_through": "后续必须体现的状态/信息/承诺/误解/关系影响；若无后续影响需明确说明", "storyboard_indices": ["后续承接镜头在根级 storyboard 中从1开始的位置"]},
        "script_evidence": "完整剧本中能逐字找到的本步剧情证据片段",
        "storyboard_indices": ["integer，引用根级 storyboard 的从1开始位置"]
    }],
    "narrative_obligations": [{
        "kind": "commitment / misunderstanding / action_consequence",
        "character_name": "承担承诺、误解或行动后果的人物",
        "obligation": "需要持续追踪的承诺、误解或行动结果",
        "origin_storyboard_index": "integer，首次建立该事项的根级分镜位置（从1开始）",
        "origin_evidence": "来源镜头中可逐字定位的动作/台词/提示文本",
        "expected_follow_through": "后续应兑现、澄清或持续体现的具体可拍摄结果",
        "follow_through_storyboard_indices": ["后续承接镜头位置列表"],
        "status": "open / resolved / intentionally_abandoned",
        "resolution_rationale": "已解决或有意放弃时的剧情依据；未解决时说明仍待处理",
        "cross_episode_required": "boolean；true 表示该事项必须由后续集承接，false 表示只在本集内处理"
    }],
    "story_engine": {
        "protagonist_goal": "主角本集具体、可观察的目标",
        "opposing_force": "阻碍目标的具体人物/环境/误解/规则",
        "stakes": "失败会失去什么或造成什么代价",
        "escalation_steps": ["冲突如何逐步升级，至少三步且因果递进"],
        "turning_point": "改变主角判断或行动方向的关键转折",
        "setup_and_payoff": "前面埋下什么线索，结尾如何兑现",
        "emotional_payoff": "观众最终获得的情绪回报"
    },
    "hook_design": {
        "opening_question": "开场建立的观众疑问",
        "retention_devices": ["推动观众继续看的信息差/未解问题"],
        "payoff": "结尾对开场疑问的回应"
    },
    "ending": "结尾及情绪落点",
    "full_script": "完整短剧剧本，包含场景、动作和台词",
    "storyboard": [{
        "index": "integer",
        "scene": "场景名称",
        "location": "场景地点",
        "characters": ["人物名"],
        "action": "可执行的画面动作",
        "dialogue": "台词/旁白",
        "product_integration": "商品如何自然进入剧情；不适用时说明",
        "product_fidelity_constraints": ["商品外观/结构/功能/正确使用方式不可改变的约束；普通短剧模式可为空"],
        "visual_verification": "not_checked / passed / needs_review / failed；not_checked 表示尚未进行画面级核验",
        "asset_needs": ["演员/场景/商品素材/实拍素材需求"],
        "actor_requirements": ["具体人物/演员标签"],
        "scene_requirements": ["具体场景标签"],
        "product_asset_requirements": ["需要展示的商品素材标签"],
        "shot_type": "景别与镜头运动",
        "duration_seconds": "integer",
        "generation_prompt": "可执行的镜头生成提示", "narrative_function": "本镜在剧情中的作用", "story_event_reference": ["对应 causal_chain.step 编号"], "character_action_basis": [{"character_name": "行动人物姓名", "goal_or_motivation": "本次行动对应的目标/动机", "known_information": "人物行动时已经掌握的信息", "knowledge_source": "full_script 中可定位的信息来源原文", "knowledge_origin": "storyboard 或 preexisting；storyboard表示剧情中获得，preexisting表示故事开始前已知", "knowledge_source_storyboard_indices": ["剧情中获得信息时对应的更早根级分镜位置；preexisting时为空列表"], "decision_pressure": "促使人物现在行动的压力", "choice_rationale": "人物为何作出该选择及可观察动作"}]
    }],
    "product_truths": ["剧情必须遵守的商品事实"],
    "risk_notes": ["待确认信息、广告表达风险或制作风险"],
    "alternative_directions": [{
        "title": "备选方向",
        "mechanism": "故事的核心叙事机制",
        "conflict_source": "主要冲突来自哪里",
        "protagonist_choice": "主角必须做出的关键选择",
        "reversal_mechanism": "反转如何由前面线索与选择自然产生",
        "product_role": "商品在该方向中的剧情作用；通用模式可说明不适用",
        "audience_hook": "目标受众为什么会关心这个故事",
        "conversion_path": "商业转化路径；通用模式可说明不适用"
    }]
}


class ShortDramaPlanError(ValueError):
    """The model output cannot be used as a short-drama plan."""


def build_short_drama_prompt(product: dict[str, Any], constraints: dict[str, Any],
                             existing_creative_plan: dict[str, Any] | None = None) -> str:
    payload = {
        "product_material": product,
        "constraints": constraints,
        "existing_ad_plan_is_reference_only": existing_creative_plan or {},
        "required_output_schema": SHORT_DRAMA_SCHEMA,
    }
    return (
        "你是独立的AI短剧编剧、导演和商业叙事设计师。当前任务是创作完整短剧，"
        "不是把常规广告脚本扩写成几个镜头。必须先理解用户选择的创作目标、已有素材和目标受众（如适用），再自主选择最合适的故事机制。\n"
        "要求：\n"
        "0. 先严格识别 constraints.drama_business_mode：general=通用AI短剧，允许完全不带商品；product_placement=商品植入短剧，商品自然参与剧情但不能挤压故事；product_conversion=商品转化短剧，剧情服务于指定商品的目标人群与转化目标。不得把三种模式混为一谈。\n"
        "0.1 通用AI短剧不要求必须出现商品；如果没有商品资料，不得编造商品，分镜 product_integration 应写明“不适用”或“本镜不出现商品”。若用户提供商品，也只在剧情合理且用户选择允许时使用。\n"
        "0.2 商品植入/商品转化模式必须有指定商品资料；商品植入应自然，商品转化需明确剧情节点、真实卖点展示和转化路径，但不得夸大效果或虚构事实。\n"
        "0.3 product_short_drama_ad 是独立的AI短剧形式商品广告目标，不能与普通商品植入/商品转化混同。先分析商品类型、目标人群、已确认卖点、使用场景和未知信息，再自主决定题材/时代（例如古代或现代）并说明理由，让商品自然成为剧情机制的一部分。\n"
        "0.4 product_short_drama_ad 必须输出 product_analysis、genre_decision、product_fact_lock。将事实分为已确认与未知/未核实；禁止编造参数、认证、效果、价格、销量、材料或功能。未知信息只能标待确认，不得当作事实使用。\n"
        "0.5 每个 product_short_drama_ad 分镜都必须有 product_fidelity_constraints，明确本镜商品外观、颜色/款式、结构、关键部件、核心功能和正确使用方式哪些必须保持不变；需要时指定参考商品图片/素材。不得为了古代/奇幻剧情把真实商品改成不同款式、改变结构或赋予不存在的功能。\n"
        "0.6 每个商品广告分镜增加 visual_verification 字段，初始值必须明确为 not_checked；结构/文字复核不能冒充生成画面视觉核验。生成画面后需由后续视觉检查或人工确认，发现问题只重生成问题镜头。\n"
        "1. 题材必须根据创作目标、商品事实（如适用）、目标人群、使用场景和传播目标推导，不得机械套用固定题材清单。\n"
        "2. 必须建立清晰的故事引擎：主角可观察的目标、具体阻力、失败代价、逐级升级的冲突、改变局势的转折、前后呼应的伏笔与兑现，以及情绪回报。输出 story_engine 对象，包含 protagonist_goal、opposing_force、stakes、escalation_steps（至少3项且因果递进）、turning_point、setup_and_payoff、emotional_payoff。\n"
         "2.1 同时输出 hook_design，包含 opening_question、retention_devices（至少2项）、payoff。开场尽快制造具体问题/意外/选择；每个主要情节都必须改变人物处境或观众认知。\n"
         "2.2 禁止用没有因果的巧合硬推剧情、只靠误会反复拖延、角色突然降智、结尾突然说教或硬塞购买口号。\n"
         "2.3 商品植入/转化/商品短剧广告：商品只能在剧情逻辑允许时成为解决问题或引发选择的真实工具，不能凭空解决与其功能无关的冲突；商品卖点必须通过可拍摄的行为展示，不得只靠角色夸赞。\n"
         "2.4 至少提供两个故事方向，且每个方向必须分别输出 conflict_source、protagonist_choice、reversal_mechanism、product_role、audience_hook 和 conversion_path。方向必须在冲突来源、人物关键选择或反转机制上有实质区别；不要仅更换场景、人物姓名、题材标签或营销话术。各方向必须能单独扩展成完整故事，并说明商品角色（不适用时如实写不适用）。\n"
         "2. 每个主要人物必须说明目标、目标背后的动机、恐惧/秘密、人物关系动态、决策压力和人物弧光；人物关系要产生可观察的利益冲突、依赖或变化，不能只写“朋友/同事”等标签。重要行动必须能追溯到人物目标、动机或压力。\n"
         "2.5 必须输出 causal_chain，按实际剧情顺序列出至少3个因果步骤。每步写明 event、caused_by、character_choice、consequence、state_change、relationship_change（人物关系的具体变化；若本步无变化，明确写“无直接关系变化”及原因），并提供 state_continuity 对象：affected_characters（受状态变化影响的人物姓名列表）、required_follow_through（后续必须体现的状态/信息/承诺/误解/关系影响；无后续影响须明确说明）、storyboard_indices（后续承接镜头位置列表）。后续承接镜头必须位于本步事件镜头之后，引用人物必须存在于角色设定表，且后续镜头文本应能直接找到要求体现的影响；若该状态没有后续影响，需明确写“无后续影响”并使用空列表。还必须提供 script_evidence（从 full_script 原文逐字摘取、能定位本步事件的片段）和 storyboard_indices（根级 storyboard 中对应镜头的从1开始位置列表）。每步至少引用一个真实存在的分镜位置；script_evidence 必须是 full_script 的原文子串，不能写概述或编造引用。除开场初始条件外，每个重要事件必须指出具体前因；前因要在剧本/分镜中可找到，后果必须改变人物处境、关系、信息或可用资源。若是意外事件，必须说明合理来源及其后续影响，不得用巧合直接解决主冲突。因果链必须与 plot_beats、full_script 和 storyboard 一致。\n"
         "设计完整的场景、冲突、节奏、转折和结尾；故事要有因果，不是卖点罗列。\n"
        "3. 商品是否出现必须服从所选创作目标：通用模式允许不出现；商品植入/转化模式应按目标呈现。任何模式都不得篡改商品外观、结构、核心功能、使用方式、规格、功效或其他事实。\n"
        "4. 未提供或无法验证的商品信息必须标为待确认，不得编造认证、销量、价格、效果或用户证言。\n"
        "5. 输出完整剧本和可执行分镜。每个分镜必须说明动作、台词、场景、人物、商品融入方式、素材需求和生成提示；新增 narrative_function（本镜在剧情中的作用）、story_event_reference（对应的 causal_chain.step 编号列表）和 character_action_basis（逐个列出本镜每个行动人物的 goal_or_motivation、known_information、knowledge_source、knowledge_origin、knowledge_source_storyboard_indices、decision_pressure、choice_rationale）。knowledge_source 必须是 full_script 中可逐字定位的信息来源原文；knowledge_origin 必须是 storyboard 或 preexisting：若信息在本剧分镜中首次获得，knowledge_source_storyboard_indices 必须引用本镜之前真实发生的信息揭示镜头，且来源原文必须出现在引用镜头的动作/台词/生成提示中；若属于故事开始前已知的信息，knowledge_source_storyboard_indices 必须为空列表。禁止引用本镜之后才揭示的信息作为当前行动依据。人物不能使用其当时尚未获知的信息。关键选择必须落实为可拍摄动作，人物行动应与人物目标、动机、关系压力及当时已知信息相容。反转必须有可定位的前置线索。\n"
        "5.1 输出 narrative_obligations 列表，追踪会影响后续剧情的承诺、误解和行动后果；每项增加 cross_episode_required 布尔值，只有确实需要跨集承接时才设为 true。\n" +
        "5.1a 每项必须说明 kind（commitment/misunderstanding/action_consequence）、character_name、obligation、origin_storyboard_index、origin_evidence、expected_follow_through、follow_through_storyboard_indices、status（open/resolved/intentionally_abandoned）及必要时的 resolution_rationale。来源证据必须出现在来源镜头文本中；后续引用必须有效且晚于来源镜头；跨集未解决事项还必须同步到来源集 continuity_state 的未解线索/下一集要求/集末状态及下一集开场状态/未解线索。旧方案兼容，缺少列表只产生审查警告。\n"
        "6. 提供至少两个故事方向备选，机制应有实质差异，不只是换标题。\n"
        "7. 本次只做创作方案，不要调用素材生成或视频生成，不要假称已经生成成片。\n"
        "7.1 A86人物状态变化必须形成“触发事件/信息→状态实际改变→人物反应→后续行动或剧情后果”的可核对闭环。对 status=changed 的台账项，填写 trigger_event、trigger_storyboard_indices、change_storyboard_indices、reaction_evidence/reaction_storyboard_indices、downstream_consequence_evidence/downstream_storyboard_indices；触发镜头必须早于状态改变镜头，反应和后续影响必须出现在改变之后。每段证据必须能在本集剧本或所引用分镜中定位；不得用“他想通了”等无事件依据的概述代替触发事件。旧方案可不提供人物状态台账。\n"
        "7.2 A87人物状态变化必须落实为可拍摄、可观察的动作/台词/表情或互动。对 status=changed 的台账项，填写 observable_manifestation 和 observable_storyboard_indices；不能只写“愤怒、怀疑、原谅、信任”等抽象心理标签。所引用镜头的 action/dialogue/generation_prompt/narrative_function/story_event_reference 中必须能直接定位所写的可观察表现，且引用有效；若只有状态结论、没有可观察行为，发出审查警告。文本检查不能替代生成画面的人工/视觉核验。旧方案可不提供可选人物状态台账。\n"
        +"8. 只输出符合给定结构的合法JSON，不要输出Markdown。\n"
        "9. 如果 constraints.short_drama_mode 为 continuous_series 或 anthology_series，必须输出指定数量的 episodes；每集有独立剧本、分镜和结尾钩子。根级 storyboard 必须按集顺序汇总全部分镜，每个镜头带 episode_number；不要把多集缩成一集。\n"
        "10. continuous_series 必须跨集承接人物状态、因果和悬念；anthology_series 共用人物/世界观但每集有相对独立的故事。单集模式 episodes 可以只含一集。\n"

        "10.1 每集必须输出 continuity_state：opening_state（开集承接状态）、character_state_changes（人物/关系变化列表）、unresolved_threads（集末未解决线索列表）、ending_state（集末确定状态）、next_episode_requirements（下一集必须承接的要求；最终集可为空列表）。连续剧第N集 opening_state 必须承接第N-1集 ending_state 和 next_episode_requirements，不能重置人物记忆或忽略未解决悬念。\n"
        "11. 每个镜头必须带 episode_number；同一角色的外貌、身份、关键服装和关系在 series_bible 中保持稳定。\n"
        "12. 输出必须包含 drama_business_mode，且与 constraints.drama_business_mode 一致；人物、场景、商品素材需求要与所选模式匹配。\n\n输入与约束：\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
    )


def build_episode_continuity_ledger(plan: dict[str, Any]) -> list[dict[str, Any]]:
    """Return an ordered, JSON-safe continuity ledger from per-episode state declarations."""
    episodes = plan.get("episodes")
    if not isinstance(episodes, list):
        return []
    ledger: list[dict[str, Any]] = []
    for position, episode in enumerate(episodes, 1):
        if not isinstance(episode, dict):
            continue
        state = episode.get("continuity_state")
        if not isinstance(state, dict):
            state = {}
        try:
            number = int(episode.get("episode_number", position))
        except (TypeError, ValueError):
            number = position
        ledger.append({
            "episode_number": number,
            "opening_state": str(state.get("opening_state", "")).strip(),
            "character_state_changes": [str(x).strip() for x in state.get("character_state_changes", []) if str(x).strip()] if isinstance(state.get("character_state_changes", []), list) else [],
            "unresolved_threads": [str(x).strip() for x in state.get("unresolved_threads", []) if str(x).strip()] if isinstance(state.get("unresolved_threads", []), list) else [],
            "ending_state": str(state.get("ending_state", "")).strip(),
            "next_episode_requirements": [str(x).strip() for x in state.get("next_episode_requirements", []) if str(x).strip()] if isinstance(state.get("next_episode_requirements", []), list) else [],
        })
    return ledger


def validate_short_drama(raw: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ShortDramaPlanError("AI短剧编导没有返回JSON对象。")
    # Backward compatible: older one-episode plans need not contain series fields.
    episodes = raw.get("episodes")
    if isinstance(episodes, list) and episodes:
        flattened = []
        for episode_index, episode in enumerate(episodes, 1):
            if not isinstance(episode, dict):
                raise ShortDramaPlanError(f"第{episode_index}集结构无效。")
            try:
                episode_number = int(episode.get("episode_number", episode_index))
            except (TypeError, ValueError) as exc:
                raise ShortDramaPlanError(f"第{episode_index}集编号无效。") from exc
            episode_shots = episode.get("storyboard", [])
            if not isinstance(episode_shots, list) or not episode_shots:
                raise ShortDramaPlanError(f"第{episode_number}集没有分镜。")
            for shot in episode_shots:
                if not isinstance(shot, dict):
                    raise ShortDramaPlanError(f"第{episode_number}集存在无效分镜。")
                shot.setdefault("episode_number", episode_number)
                flattened.append(shot)
        if not raw.get("storyboard"):
            raw["storyboard"] = flattened
        raw.setdefault("episode_count", len(episodes))
        raw.setdefault("format_mode", "single_episode" if len(episodes) == 1 else "continuous_series")
        raw.setdefault("series_bible", {})
        if not raw.get("full_script"):
            raw["full_script"] = "\n\n".join(
                f"第{e.get('episode_number', i)}集：{e.get('title', '')}\n{e.get('full_script', '')}"
                for i, e in enumerate(episodes, 1)
            )
    raw.setdefault("drama_business_mode", "product_placement")
    if raw.get("drama_business_mode") not in {"general", "product_placement", "product_conversion", "product_short_drama_ad"}:
        raise ShortDramaPlanError("短剧创作目标无效。")
    raw.setdefault("format_mode", "single_episode")
    raw.setdefault("episode_count", 1)
    raw.setdefault("series_bible", {})
    required = [
        "genre", "genre_reasoning", "logline", "premise", "world",
        "characters", "plot_beats", "conflict_and_reversal", "ending",
        "full_script", "storyboard", "product_truths", "risk_notes",
        "alternative_directions",
    ]
    missing = [key for key in required if key not in raw]
    if missing:
        raise ShortDramaPlanError("短剧方案缺少字段：" + "、".join(missing))
    if raw.get("format_mode") not in {"single_episode", "continuous_series", "anthology_series"}:
        raise ShortDramaPlanError("短剧模式无效，必须是单集、连续多集或系列剧。")
    if not isinstance(raw.get("episode_count"), int) or raw["episode_count"] < 1:
        raise ShortDramaPlanError("短剧集数必须是正整数。")
    if raw.get("format_mode") != "single_episode":
        episodes = raw.get("episodes")
        if not isinstance(episodes, list) or len(episodes) != raw["episode_count"]:
            raise ShortDramaPlanError(f"多集短剧要求恰好提供 {raw['episode_count']} 集，实际为 {len(episodes) if isinstance(episodes, list) else 0} 集。")
        expected = list(range(1, raw["episode_count"] + 1))
        actual = [int(e.get("episode_number", i)) for i, e in enumerate(episodes, 1) if isinstance(e, dict)]
        if actual != expected:
            raise ShortDramaPlanError("分集编号必须从第1集开始连续递增，不能缺集或重复。")
        for episode in episodes:
            state = episode.get("continuity_state")
            number = episode["episode_number"]
            if not isinstance(state, dict):
                raise ShortDramaPlanError(f"第{number}集缺少跨集连续性状态 continuity_state。")
            for field in ("opening_state", "character_state_changes", "unresolved_threads", "ending_state", "next_episode_requirements"):
                if field not in state:
                    raise ShortDramaPlanError(f"第{number}集连续性状态缺少字段 {field}。")
            if not str(state.get("opening_state", "")).strip():
                raise ShortDramaPlanError(f"第{number}集必须说明开集承接状态。")
            if not str(state.get("ending_state", "")).strip():
                raise ShortDramaPlanError(f"第{number}集必须说明集末人物/剧情状态。")
            for field in ("character_state_changes", "unresolved_threads", "next_episode_requirements"):
                if not isinstance(state.get(field), list):
                    raise ShortDramaPlanError(f"第{number}集连续性字段 {field} 必须是列表。")
        raw["continuity_ledger"] = build_episode_continuity_ledger(raw)
    if raw.get("drama_business_mode") == "product_short_drama_ad":
        for field in ("product_analysis", "genre_decision", "product_fact_lock"):
            if not isinstance(raw.get(field), dict) or not raw[field]:
                raise ShortDramaPlanError(f"AI短剧形式商品广告缺少必需的商品真实性字段：{field}。")
        decision = raw["genre_decision"]
        if not str(decision.get("selected_genre", raw.get("genre", ""))).strip() or not str(decision.get("reasoning", raw.get("genre_reasoning", ""))).strip():
            raise ShortDramaPlanError("AI短剧形式商品广告必须说明题材选择及理由。")
        lock = raw["product_fact_lock"]
        if not isinstance(lock.get("confirmed_facts", []), list) or not isinstance(lock.get("unknown_or_unverified", []), list):
            raise ShortDramaPlanError("商品事实锁定中的已确认/未知事实必须使用列表。")
        for index, shot in enumerate(raw["storyboard"], 1):
            constraints = shot.get("product_fidelity_constraints")
            if not isinstance(constraints, list) or not any(str(item).strip() for item in constraints):
                raise ShortDramaPlanError(f"AI短剧形式商品广告第{index}镜缺少商品外观/结构/功能真实性约束。")
            shot.setdefault("visual_verification", "not_checked")
            if shot["visual_verification"] not in {"not_checked", "passed", "needs_review", "failed"}:
                raise ShortDramaPlanError(f"第{index}镜 visual_verification 状态无效。")
    if not isinstance(raw["characters"], list) or not raw["characters"]:
        raise ShortDramaPlanError("短剧必须至少设计一个人物。")
    if not isinstance(raw["storyboard"], list) or not raw["storyboard"]:
        raise ShortDramaPlanError("短剧必须包含可执行分镜。")
    if not isinstance(raw["plot_beats"], list) or len(raw["plot_beats"]) < 3:
        raise ShortDramaPlanError("剧情节拍至少需要三个阶段。")
    for index, shot in enumerate(raw["storyboard"], 1):
        if not isinstance(shot, dict):
            raise ShortDramaPlanError(f"第{index}个短剧分镜格式无效。")
        if not shot.get("action") or not shot.get("scene"):
            raise ShortDramaPlanError(f"第{index}个短剧分镜缺少场景或动作。")
        try:
            shot["index"] = int(shot.get("index", index))
            shot["duration_seconds"] = max(1, int(shot.get("duration_seconds", 4)))
        except (TypeError, ValueError) as exc:
            raise ShortDramaPlanError(f"第{index}个短剧分镜时长无效。") from exc
        shot.setdefault("episode_number", 1)
        try:
            shot["episode_number"] = int(shot["episode_number"])
        except (TypeError, ValueError) as exc:
            raise ShortDramaPlanError(f"第{index}个分镜集数无效。") from exc
        if shot["episode_number"] < 1 or shot["episode_number"] > raw["episode_count"]:
            raise ShortDramaPlanError(f"第{index}个分镜引用了不存在的集数。")
        for key in ("characters", "asset_needs", "actor_requirements", "scene_requirements", "product_asset_requirements"):
            if not isinstance(shot.get(key), list):
                shot[key] = []
    for key in ("characters", "plot_beats", "product_truths", "risk_notes", "alternative_directions"):
        if not isinstance(raw[key], list):
            raise ShortDramaPlanError(f"短剧方案字段 {key} 必须是列表。")
    if raw.get("format_mode") == "single_episode":
        raw.setdefault("continuity_ledger", build_episode_continuity_ledger(raw))
    return raw


def generate_short_drama(model_router, product: dict[str, Any], constraints: dict[str, Any],
                         existing_creative_plan: dict[str, Any] | None = None) -> dict[str, Any]:
    """Generate and validate a story-first plan through its independently routed model."""
    profile = model_router.resolve_route("AI短剧编导")
    prompt = build_short_drama_prompt(product, constraints, existing_creative_plan)
    try:
        result = model_router.complete_json(profile, prompt, function="AI短剧编导")
    except TypeError as exc:
        if "unexpected keyword argument 'function'" not in str(exc):
            raise
        result = model_router.complete_json(profile, prompt)
    validated = validate_short_drama(result)
    # Enforce stronger structure on new generations while keeping saved legacy plans readable.
    story_engine = validated.get("story_engine")
    hook_design = validated.get("hook_design")
    required_engine = ("protagonist_goal", "opposing_force", "stakes", "turning_point", "setup_and_payoff", "emotional_payoff")
    if not isinstance(story_engine, dict) or any(not str(story_engine.get(key, "")).strip() for key in required_engine):
        raise ShortDramaPlanError("新生成的短剧缺少完整 story_engine（主角目标、阻力、代价、转折、伏笔兑现、情绪回报）；请重新生成。")
    escalation = story_engine.get("escalation_steps")
    if not isinstance(escalation, list) or len([item for item in escalation if str(item).strip()]) < 3:
        raise ShortDramaPlanError("新生成的短剧冲突升级不足：story_engine.escalation_steps 至少需要3个具体步骤。")
    if not isinstance(hook_design, dict) or not str(hook_design.get("opening_question", "")).strip() or not str(hook_design.get("payoff", "")).strip():
        raise ShortDramaPlanError("新生成的短剧缺少 hook_design 开场疑问或结尾兑现。")
    retention = hook_design.get("retention_devices")
    if not isinstance(retention, list) or len([item for item in retention if str(item).strip()]) < 2:
        raise ShortDramaPlanError("新生成的短剧留存设计不足：hook_design.retention_devices 至少需要2项。")
    causal_chain = validated.get("causal_chain")
    causal_fields = ("event", "caused_by", "character_choice", "consequence", "state_change", "script_evidence")
    storyboard = validated.get("storyboard", [])
    if not isinstance(causal_chain, list) or len(causal_chain) < 3:
        raise ShortDramaPlanError("新生成短剧必须提供至少3步 causal_chain 因果链。")
    for index, step in enumerate(causal_chain, 1):
        if not isinstance(step, dict) or any(not str(step.get(key, "")).strip() for key in causal_fields):
            raise ShortDramaPlanError(f"因果链第{index}步缺少事件、前因、人物选择、后果、状态变化或剧本证据。")
        if str(step["script_evidence"]) not in str(validated.get("full_script", "")):
            raise ShortDramaPlanError(f"因果链第{index}步的 script_evidence 不是 full_script 原文，无法核对剧情一致性。")
        shot_refs = step.get("storyboard_indices")
        if not isinstance(shot_refs, list) or not shot_refs:
            raise ShortDramaPlanError(f"因果链第{index}步必须引用至少一个 storyboard_indices 分镜位置。")
        for shot_ref in shot_refs:
            if isinstance(shot_ref, bool) or not isinstance(shot_ref, int) or shot_ref < 1 or shot_ref > len(storyboard):
                raise ShortDramaPlanError(f"因果链第{index}步引用了不存在的分镜位置。")
        if step.get("step") is not None:
            try:
                step["step"] = int(step["step"])
            except (TypeError, ValueError) as exc:
                raise ShortDramaPlanError(f"因果链第{index}步编号无效。") from exc
    if [step.get("step", index) for index, step in enumerate(causal_chain, 1)] != list(range(1, len(causal_chain) + 1)):
        raise ShortDramaPlanError("因果链步骤必须按从1开始的顺序连续编号。")
    directions = validated.get("alternative_directions", [])
    if len(directions) < 2:
        raise ShortDramaPlanError("新生成方案至少需要两个故事方向，才能比较不同的叙事机制。")
    direction_fields = ("title", "mechanism", "conflict_source", "protagonist_choice", "reversal_mechanism", "product_role", "audience_hook", "conversion_path")
    signatures = []
    for index, direction in enumerate(directions, 1):
        if not isinstance(direction, dict) or any(not str(direction.get(key, "")).strip() for key in direction_fields):
            raise ShortDramaPlanError(f"第{index}个备选故事方向缺少完整字段（冲突来源、人物选择、反转机制、商品角色、受众吸引点及转化路径）。")
        signature = tuple(" ".join(str(direction.get(key, "")).lower().split()) for key in ("conflict_source", "protagonist_choice", "reversal_mechanism"))
        signatures.append(signature)
    if len(set(signatures)) < 2:
        raise ShortDramaPlanError("备选故事方向的冲突来源、人物选择和反转机制完全重复；请重新生成有实质区别的方向。")
    characters = validated.get("characters", [])
    character_fields = ("name", "role", "goal", "motivation", "fear_or_secret", "relationship", "relationship_dynamics", "decision_pressure", "arc")
    for index, character in enumerate(characters, 1):
        if not isinstance(character, dict) or any(not str(character.get(key, "")).strip() for key in character_fields):
            raise ShortDramaPlanError(f"新生成短剧的第{index}个人物缺少完整动机/关系字段；请补齐目标、动机、恐惧或秘密、关系动态、决策压力和人物弧光。")
    requested_mode = str(constraints.get("short_drama_mode", "single_episode"))
    requested_count = int(constraints.get("episode_count", 1))
    requested_business_mode = str(constraints.get("drama_business_mode", "product_placement"))
    if requested_business_mode == "product_short_drama_ad" and not product:
        raise ShortDramaPlanError("AI短剧形式商品广告必须提供商品资料，才能分析商品并锁定真实外观、结构和功能。")
    if validated.get("drama_business_mode") != requested_business_mode:
        raise ShortDramaPlanError(
            f"模型返回的短剧商业模式为 {validated.get('drama_business_mode')}，与所选模式 {requested_business_mode} 不一致；请重新生成，避免创作目标错位。"
        )
    # A language model cannot certify that an image faithfully depicts the real product.
    # Reset each new product-ad shot to an explicitly unchecked state, even if the
    # model returned "passed"; only a later visual review may change this state.
    if requested_business_mode == "product_short_drama_ad":
        for shot in validated.get("storyboard", []):
            shot["visual_verification"] = "not_checked"

    if validated.get("format_mode") != requested_mode:
        raise ShortDramaPlanError(
            f"模型返回的短剧模式为 {validated.get('format_mode')}，与所选模式 {requested_mode} 不一致；请重新生成，避免把多集需求误当成单集。"
        )
    if validated.get("episode_count") != requested_count:
        raise ShortDramaPlanError(
            f"模型返回 {validated.get('episode_count')} 集，但用户选择了 {requested_count} 集；未保存不匹配的方案。"
        )
    return validated


def short_drama_production_rows(plan: dict[str, Any], product_name: str) -> list[dict[str, Any]]:
    """Translate a validated drama storyboard into the existing production data contract."""
    validated = validate_short_drama(dict(plan))
    rows: list[dict[str, Any]] = []
    for index, shot in enumerate(validated["storyboard"], 1):
        actor_tags = [str(x).strip() for x in shot.get("actor_requirements", []) if str(x).strip()]
        scene_tags = [str(x).strip() for x in shot.get("scene_requirements", []) if str(x).strip()]
        product_tags = [str(x).strip() for x in shot.get("product_asset_requirements", []) if str(x).strip()]
        if not actor_tags:
            actor_tags = [str(x).strip() for x in shot.get("characters", []) if str(x).strip()]
        if not scene_tags:
            scene_tags = [str(shot.get("location") or shot.get("scene") or "").strip()]
            scene_tags = [x for x in scene_tags if x]
        integration = str(shot.get("product_integration", "")).strip()
        if integration and integration not in {"不适用", "暂不出现", "无"} and not product_tags:
            product_tags = [str(product_name).strip()] if str(product_name).strip() else []
        title = str(shot.get("scene") or f"短剧镜头{index}")
        action = str(shot.get("action", "")).strip()
        location = str(shot.get("location", "")).strip()
        shot_type = str(shot.get("shot_type", "")).strip()
        prompt = str(shot.get("generation_prompt", "")).strip()
        visual = "；".join(part for part in (
            f"地点：{location}" if location else "",
            f"动作：{action}" if action else "",
            f"景别/运动：{shot_type}" if shot_type else "",
            f"商品融入：{integration}" if integration else "",
            f"生成要求：{prompt}" if prompt else "",
        ) if part)
        episode_number = int(shot.get("episode_number", 1))
        rows.append({
            "index": index,
            "episode_shot_index": int(shot.get("index", index)),
            "episode_number": episode_number,
            "title": f"第{episode_number}集｜{title}" if validated.get("episode_count", 1) > 1 else title,
            "visual": visual,
            "script": str(shot.get("dialogue", "")).strip(),
            "duration_seconds": max(1, int(shot.get("duration_seconds", 4))),
            "asset_resolution": {
                "actor_tags": actor_tags,
                "scene_tags": scene_tags,
                "product_tags": product_tags,
                "generation_if_missing": True,
            },
            "director_mode": "short_drama",
            "story_scene": title,
            "story_action": action,
            "episode_number": episode_number,
            "product_integration": integration,
        })
    return rows



def prepare_product_drama_shot_regeneration(
    plan: dict[str, Any],
    shot_number: int,
    correction_note: str,
    *,
    previous_version: int,
    previous_video_path: str | None = None,
    estimated_cost_rmb: float = 0.0,
) -> dict[str, Any]:
    """Prepare one product-drama shot for regeneration without calling a provider."""
    if plan.get("drama_business_mode") != "product_short_drama_ad":
        raise ShortDramaPlanError("局部商品镜头修复只适用于“AI短剧形式商品广告”模式。")
    note = str(correction_note or "").strip()
    if not note:
        raise ShortDramaPlanError("请写明该镜头的问题和修正要求。")
    shots = plan.get("storyboard", [])
    if not isinstance(shots, list) or shot_number < 1 or shot_number > len(shots):
        raise ShortDramaPlanError("指定镜头编号不存在。")
    try:
        estimated_cost = float(estimated_cost_rmb)
        old_version = int(previous_version)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ShortDramaPlanError("预计生成费用或旧版本号无效。") from exc
    if not math.isfinite(estimated_cost) or estimated_cost < 0:
        raise ShortDramaPlanError("预计生成费用必须是有限的非负数。")
    if old_version < 1:
        raise ShortDramaPlanError("旧版本号必须是正整数。")
    updated = json.loads(json.dumps(plan, ensure_ascii=False))
    shot = updated["storyboard"][shot_number - 1]
    history = list(shot.get("regeneration_history", []) or [])
    history.append({
        "version": old_version,
        "video_path": str(previous_video_path or ""),
        "correction_note": note,
        "estimated_cost_rmb": round(estimated_cost, 4),
        "visual_verification": shot.get("visual_verification", "not_checked"),
        "visual_verification_method": shot.get("visual_verification_method", ""),
        "visual_verification_evidence": shot.get("visual_verification_evidence", ""),
        "visual_verification_note": shot.get("visual_verification_note", ""),
        "visual_comparison_result": shot.get("visual_comparison_result"),
    })
    shot["regeneration_history"] = history
    shot["last_regeneration_correction"] = note
    old_prompt = str(shot.get("generation_prompt", "")).strip()
    shot["generation_prompt"] = (old_prompt + "\n商品画面修正要求（本次只修复当前镜头）： " + note).strip()
    shot["visual_verification"] = "not_checked"
    shot["visual_verification_method"] = ""
    shot["visual_verification_evidence"] = ""
    shot["visual_verification_reference_images"] = []
    shot["visual_verification_note"] = ""
    shot.pop("visual_comparison_result", None)
    return updated


def resolve_product_drama_shot_number(plan: dict[str, Any], shot_reference: Any) -> int:
    """Resolve a project Shot to its stable 1-based storyboard position.

    Project display indexes can change when reviewed supplemental shots are inserted.
    New projects persist the original storyboard index; legacy projects fall back to
    a unique title + episode match and fail closed when that match is ambiguous.
    """
    if plan.get("drama_business_mode") != "product_short_drama_ad":
        raise ShortDramaPlanError("镜头映射只适用于“AI短剧形式商品广告”模式。")
    storyboard = plan.get("storyboard", [])
    if not isinstance(storyboard, list) or not storyboard:
        raise ShortDramaPlanError("商品短剧没有有效分镜，无法安全定位镜头。")

    def field(name: str, default: Any = None) -> Any:
        return shot_reference.get(name, default) if isinstance(shot_reference, dict) else getattr(shot_reference, name, default)

    stable = field("short_drama_shot_number")
    if stable not in (None, ""):
        try:
            number = int(stable)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ShortDramaPlanError("保存的短剧分镜映射编号无效；为避免改错镜头，已停止。") from exc
        if number < 1 or number > len(storyboard):
            raise ShortDramaPlanError("保存的短剧分镜映射已失效；为避免改错镜头，已停止。")
        return number

    title = str(field("title", "") or "").strip()
    try:
        episode = int(field("episode_number", 1) or 1)
        episode_count = int(plan.get("episode_count") or len(plan.get("episodes", []) or []) or 1)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ShortDramaPlanError("镜头标题或分集编号无效，无法安全定位。") from exc

    matches = []
    for number, item in enumerate(storyboard, 1):
        if not isinstance(item, dict):
            continue
        try:
            item_episode = int(item.get("episode_number", 1) or 1)
        except (TypeError, ValueError, OverflowError):
            continue
        scene = str(item.get("scene") or f"短剧镜头{number}").strip()
        expected_title = f"第{item_episode}集｜{scene}" if episode_count > 1 else scene
        if item_episode == episode and expected_title == title:
            matches.append(number)
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise ShortDramaPlanError("该镜头标题在短剧分镜中重复，无法唯一定位；请先检查分镜映射，未修改任何镜头。")
    raise ShortDramaPlanError("无法将当前项目镜头唯一映射到短剧分镜；为避免修错镜头，未修改任何内容。")


def product_visual_correction_suggestion(plan: dict[str, Any], shot_number: int) -> str:
    """Build an editable correction draft from the latest vision-review result."""
    if plan.get("drama_business_mode") != "product_short_drama_ad":
        return ""
    shots = plan.get("storyboard", [])
    if not isinstance(shots, list) or shot_number < 1 or shot_number > len(shots):
        return ""
    comparison = shots[shot_number - 1].get("visual_comparison_result")
    if not isinstance(comparison, dict):
        return ""
    result = comparison.get("result")
    if not isinstance(result, dict):
        return ""
    lines = ["基于上次AI视觉核验结果整理的修正草稿（请对照参考图确认，可自行编辑）："]
    summary = str(result.get("summary", "")).strip()
    if summary:
        lines.append("核验摘要：" + summary)
    issues = result.get("issues", [])
    if isinstance(issues, list):
        for item in issues:
            if isinstance(item, dict):
                text = str(item.get("description") or item.get("message") or item.get("issue") or "").strip()
            else:
                text = str(item).strip()
            if text:
                lines.append("待检查问题：" + text)
    if len(lines) == 1 and result.get("mismatch_detected") is True:
        lines.append("AI提示商品画面可能与参考图不一致；请逐项检查商品身份、外观、结构、功能和正确使用方式。")
    return "\n".join(lines) if len(lines) > 1 else ""


def record_product_visual_verification(
    plan: dict[str, Any], shot_number: int, status: str, evidence_path: str, reviewer_note: str
) -> dict[str, Any]:
    """Record an explicit human visual review tied to a concrete local image/video file."""
    allowed = {"passed", "needs_review", "failed"}
    if status not in allowed:
        raise ShortDramaPlanError("人工画面核验状态必须是 passed、needs_review 或 failed。")
    if not str(evidence_path).strip():
        raise ShortDramaPlanError("记录商品画面核验必须选择实际生成的图片或视频作为证据。")
    if not str(reviewer_note).strip():
        raise ShortDramaPlanError("请填写核验备注，说明外观、结构、功能或使用方式的检查结果。")
    updated = json.loads(json.dumps(plan, ensure_ascii=False))
    shots = updated.get("storyboard", [])
    if not isinstance(shots, list) or shot_number < 1 or shot_number > len(shots):
        raise ShortDramaPlanError("指定镜头编号不存在。")
    if updated.get("drama_business_mode") != "product_short_drama_ad":
        raise ShortDramaPlanError("人工商品视觉核验只适用于“AI短剧形式商品广告”模式。")
    evidence = Path(str(evidence_path).strip()).expanduser()
    image_exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
    video_exts = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi", ".mpeg", ".mpg"}
    if evidence.suffix.lower() not in image_exts | video_exts:
        raise ShortDramaPlanError("人工核验证据必须是受支持的图片或视频文件。")
    try:
        evidence_is_valid = evidence.is_file() and evidence.stat().st_size > 0
    except OSError:
        evidence_is_valid = False
    if not evidence_is_valid:
        raise ShortDramaPlanError("人工核验证据文件不存在、为空或无法读取；请选择实际生成的图片或视频。")
    shot = shots[shot_number - 1]
    shot["visual_verification"] = status
    shot["visual_verification_evidence"] = str(evidence.resolve())
    shot["visual_verification_method"] = "manual"
    shot["visual_verification_note"] = str(reviewer_note).strip()
    return updated



def compare_product_visual_shot(
    model_router: Any,
    plan: dict[str, Any],
    shot_number: int,
    reference_image_paths: list[str],
    generated_visual_path: str,
) -> dict[str, Any]:
    """Compare product reference images with a generated shot using a vision model.

    The model can flag likely mismatches, but it can never automatically certify
    product fidelity. Non-mismatch results remain needs_review for human approval.
    Video evidence is sampled into temporary JPEG frames through FFmpeg.
    """
    if plan.get("drama_business_mode") != "product_short_drama_ad":
        raise ShortDramaPlanError("自动商品画面对比只适用于“AI短剧形式商品广告”模式。")
    shots = plan.get("storyboard", [])
    if not isinstance(shots, list) or shot_number < 1 or shot_number > len(shots):
        raise ShortDramaPlanError("指定镜头编号不存在。")
    image_exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
    video_exts = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi", ".mpeg", ".mpg"}
    refs = [Path(p).expanduser() for p in reference_image_paths if str(p).strip()]
    if not refs:
        raise ShortDramaPlanError("请至少选择一张商品参考图片。")
    if any(not p.is_file() or p.stat().st_size <= 0 for p in refs):
        raise ShortDramaPlanError("有商品参考图片不存在、为空或无法读取。")
    if any(p.suffix.lower() not in image_exts for p in refs):
        raise ShortDramaPlanError("商品参考文件必须是 PNG、JPG、JPEG、WEBP 或 BMP 图片。")
    generated = Path(generated_visual_path).expanduser()
    if not generated.is_file() or generated.stat().st_size <= 0:
        raise ShortDramaPlanError("生成画面文件不存在、为空或无法读取。")
    frame_paths: list[Path] = []
    temp_dir = None
    if generated.suffix.lower() in image_exts:
        frame_paths = [generated]
    elif generated.suffix.lower() in video_exts:
        ffmpeg = shutil.which("ffmpeg")
        ffprobe = shutil.which("ffprobe")
        if not ffmpeg or not ffprobe:
            raise ShortDramaPlanError("对比视频需要安装 FFmpeg 和 FFprobe，并加入系统 PATH。")
        try:
            probe = subprocess.run(
                [ffprobe, "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(generated)],
                capture_output=True, text=True, timeout=15, check=True,
            )
            duration = max(0.1, float(probe.stdout.strip()))
        except Exception as exc:
            raise ShortDramaPlanError(f"无法读取视频时长：{exc}") from exc
        temp_dir = tempfile.TemporaryDirectory(prefix="ad-studio-product-visual-")
        temp_root = Path(temp_dir.name)
        timestamps = sorted({0.0, duration * 0.5, max(0.0, duration * 0.85)})
        for idx, timestamp in enumerate(timestamps, start=1):
            frame = temp_root / f"frame-{idx}.jpg"
            try:
                subprocess.run(
                    [ffmpeg, "-y", "-ss", f"{timestamp:.3f}", "-i", str(generated),
                     "-frames:v", "1", "-q:v", "3", str(frame)],
                    capture_output=True, text=True, timeout=30, check=True,
                )
            except Exception as exc:
                temp_dir.cleanup()
                raise ShortDramaPlanError(f"无法从视频提取第 {idx} 个核验帧：{exc}") from exc
            if frame.is_file() and frame.stat().st_size:
                frame_paths.append(frame)
        if not frame_paths:
            temp_dir.cleanup()
            raise ShortDramaPlanError("未能从视频中提取可用于核验的画面帧。")
    else:
        raise ShortDramaPlanError("生成画面仅支持常见图片格式或 MP4/MOV/M4V/MKV/WEBM/AVI/MPEG 视频。")
    try:
        profile = model_router.resolve_route("商品画面视觉核验")
        if not getattr(profile, "vision_enabled", False):
            raise ShortDramaPlanError(
                f"当前模型「{profile.name}」未启用视觉输入。请在模型设置中启用图片/视频帧分析。"
            )
        shot = shots[shot_number - 1]
        product_facts = plan.get("product_fact_lock", {})
        prompt = (
            "你是商品广告画面真实性复核助手。请对照商品参考图片与后续生成画面帧，"
            "重点检查商品身份、颜色/外观、结构/部件、可见功能表现、正确使用方式是否一致。"
            "不要把光线、背景、角度变化直接认定为商品变化；看不清或证据不足时必须标记不确定。"
            "不要臆测图片中看不到的参数或内部结构。此结果仅供人工复核，不可视为最终认证。\n"
            f"镜头描述：{shot.get('description', shot.get('visual', '未提供'))}\n"
            f"商品事实锁定：{json.dumps(product_facts, ensure_ascii=False)}\n"
            f"分镜约束：{json.dumps(shot.get('product_fidelity_constraints', []), ensure_ascii=False)}\n"
            "请严格返回 JSON：identity_match (true/false/null), appearance_match (true/false/null), "
            "structure_match (true/false/null), function_match (true/false/null), usage_match (true/false/null), "
            "mismatch_detected (boolean), confidence (0到1), issues (字符串数组), summary (字符串)。"
        )
        response = model_router.complete_json(
            profile, prompt, function="商品画面视觉核验",
            image_paths=[str(p) for p in refs[:8] + frame_paths[:8]],
        )
        updated = json.loads(json.dumps(plan, ensure_ascii=False))
        target = updated["storyboard"][shot_number - 1]
        mismatch = response.get("mismatch_detected") is True or any(
            response.get(key) is False for key in (
                "identity_match", "appearance_match", "structure_match", "function_match", "usage_match"
            )
        )
        target["visual_verification"] = "failed" if mismatch else "needs_review"
        target["visual_verification_method"] = "ai_vision_assisted"
        target["visual_verification_evidence"] = str(generated)
        target["visual_verification_reference_images"] = [str(p) for p in refs]
        target["visual_verification_note"] = str(response.get("summary", "AI 视觉对比已完成，仍需人工复核。"))
        target["visual_comparison_result"] = {
            "model_id": getattr(profile, "id", ""),
            "result": response,
            "sampled_frame_count": len(frame_paths),
            "requires_human_review": True,
        }
        return updated
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


def audit_short_drama(plan: dict[str, Any], product_material: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run deterministic pre-production checks; warnings require human review, not blind approval."""
    checked = validate_short_drama(json.loads(json.dumps(plan, ensure_ascii=False)))
    issues: list[dict[str, str]] = []
    def add(level: str, code: str, message: str) -> None:
        issues.append({"level": level, "code": code, "message": message})

    story_engine = checked.get("story_engine")
    engine_required = ("protagonist_goal", "opposing_force", "stakes", "turning_point", "setup_and_payoff", "emotional_payoff")
    if not isinstance(story_engine, dict) or any(not str(story_engine.get(key, "")).strip() for key in engine_required):
        add("warning", "STORY_ENGINE_INCOMPLETE", "缺少完整故事引擎字段（主角目标、阻力、代价、转折、伏笔兑现、情绪回报）；剧情质量需要人工复核。")
    elif not isinstance(story_engine.get("escalation_steps"), list) or len([x for x in story_engine.get("escalation_steps", []) if str(x).strip()]) < 3:
        add("warning", "STORY_ESCALATION_WEAK", "冲突升级步骤少于三项，或未形成可检查的递进结构。")
    hook_design = checked.get("hook_design")
    if not isinstance(hook_design, dict) or not str(hook_design.get("opening_question", "")).strip() or not str(hook_design.get("payoff", "")).strip():
        add("warning", "HOOK_DESIGN_INCOMPLETE", "缺少开场疑问或结尾兑现设计，需检查开场是否吸引观众并在结尾回应。")
    elif not isinstance(hook_design.get("retention_devices"), list) or len([x for x in hook_design.get("retention_devices", []) if str(x).strip()]) < 2:
        add("warning", "RETENTION_DESIGN_WEAK", "留存设计少于两个可识别的装置，需人工检查观众继续观看的理由。")

    character_names = {
        str(item.get("name", "")).strip()
        for item in checked.get("characters", [])
        if isinstance(item, dict) and str(item.get("name", "")).strip()
    }
    causal_chain = checked.get("causal_chain")
    causal_fields = ("event", "caused_by", "character_choice", "consequence", "state_change", "script_evidence")
    audit_script = str(checked.get("full_script", ""))
    storyboard = checked.get("storyboard", [])
    if not isinstance(causal_chain, list) or len(causal_chain) < 3:
        add("warning", "CAUSAL_CHAIN_INCOMPLETE", "缺少至少三步的显式剧情因果链；请人工核对重要事件是否有前因、选择、后果和状态变化。")
    else:
        for index, step in enumerate(causal_chain, 1):
            if not isinstance(step, dict) or any(not str(step.get(key, "")).strip() for key in causal_fields):
                add("warning", "CAUSAL_STEP_INCOMPLETE", f"因果链第{index}步缺少前因/选择/后果/状态变化或剧本证据。")
                continue
            relationship_change = str(step.get("relationship_change", "")).strip()
            if len(checked.get("characters", [])) >= 2 and not relationship_change:
                add("warning", "RELATIONSHIP_CHANGE_UNSPECIFIED", f"因果链第{index}步没有说明人物关系是否发生变化；请写明可观察变化，或明确说明本步无直接关系变化及原因。")
            # A81: track consequences of state changes into later shots, not only the originating beat.
            continuity = step.get("state_continuity")
            if not isinstance(continuity, dict):
                add("warning", "STATE_CONTINUITY_UNSPECIFIED", f"因果链第{index}步未说明人物状态变化是否会影响后续剧情；请补充 state_continuity，或明确写无后续影响。")
            else:
                affected = continuity.get("affected_characters")
                follow_text = str(continuity.get("required_follow_through", "")).strip()
                follow_refs = continuity.get("storyboard_indices")
                if not isinstance(affected, list):
                    add("warning", "STATE_CONTINUITY_CHARACTERS_INVALID", f"因果链第{index}步 state_continuity.affected_characters 必须是人物姓名列表。")
                    affected = []
                unknown = [str(name).strip() for name in affected if str(name).strip() and str(name).strip() not in character_names]
                if unknown:
                    add("warning", "STATE_CONTINUITY_UNKNOWN_CHARACTER", f"因果链第{index}步状态连续性引用了未定义人物：{'、'.join(unknown)}。")
                if not follow_text:
                    add("warning", "STATE_CONTINUITY_FOLLOW_THROUGH_MISSING", f"因果链第{index}步没有说明后续需要延续的状态影响；无后续影响也必须明确写出。")
                no_follow_through = any(marker in follow_text for marker in ("无后续影响", "无需后续承接", "不影响后续剧情"))
                if not isinstance(follow_refs, list):
                    add("warning", "STATE_CONTINUITY_SHOTS_INVALID", f"因果链第{index}步 state_continuity.storyboard_indices 必须是镜头位置列表。")
                    follow_refs = []
                if no_follow_through:
                    if follow_refs:
                        add("warning", "STATE_CONTINUITY_UNEXPECTED_SHOTS", f"因果链第{index}步声明无后续影响，却仍引用了承接镜头；请核对。")
                elif not follow_refs:
                    add("warning", "STATE_CONTINUITY_SHOTS_MISSING", f"因果链第{index}步声明有后续状态影响，但没有引用承接镜头。")
                else:
                    origin_refs = step.get("storyboard_indices", [])
                    valid_origins = [ref for ref in origin_refs if isinstance(ref, int) and not isinstance(ref, bool) and 1 <= ref <= len(storyboard)] if isinstance(origin_refs, list) else []
                    valid_follow_refs = [ref for ref in follow_refs if isinstance(ref, int) and not isinstance(ref, bool) and 1 <= ref <= len(storyboard)]
                    if len(valid_follow_refs) != len(follow_refs):
                        add("warning", "STATE_CONTINUITY_SHOTS_INVALID", f"因果链第{index}步状态承接引用了不存在的分镜位置。")
                    if valid_origins and any(ref <= max(valid_origins) for ref in valid_follow_refs):
                        add("warning", "STATE_CONTINUITY_NOT_LATER", f"因果链第{index}步状态承接镜头必须位于本步事件镜头之后。")
                    follow_shot_text = " ".join(
                        " ".join(str(storyboard[ref - 1].get(key, "")) for key in ("action", "dialogue", "generation_prompt", "narrative_function", "story_event_reference")).casefold()
                        for ref in valid_follow_refs if isinstance(storyboard[ref - 1], dict)
                    )
                    if follow_text and not no_follow_through and follow_text.casefold() not in follow_shot_text:
                        add("warning", "STATE_CONTINUITY_NOT_SHOWN", f"因果链第{index}步要求后续体现的状态影响“{follow_text}”未在所引用的后续镜头文本中直接体现；请补充可拍摄后果或修正引用。")
            if relationship_change:
                shot_refs_for_relationship = step.get("storyboard_indices")
                valid_relationship_refs = (
                    [ref for ref in shot_refs_for_relationship if isinstance(ref, int) and not isinstance(ref, bool) and 1 <= ref <= len(storyboard)]
                    if isinstance(shot_refs_for_relationship, list) else []
                )
                relationship_shot_text = " ".join(
                    " ".join(str(storyboard[ref - 1].get(key, "")) for key in (
                        "action", "dialogue", "generation_prompt", "narrative_function", "story_event_reference"
                    )).casefold()
                    for ref in valid_relationship_refs
                    if isinstance(storyboard[ref - 1], dict)
                )
                no_change_markers = ("无直接关系变化", "关系无变化", "没有关系变化", "关系保持不变")
                if not any(marker in relationship_change for marker in no_change_markers) and relationship_change.casefold() not in relationship_shot_text:
                    add("warning", "RELATIONSHIP_CHANGE_NOT_SHOWN", f"因果链第{index}步描述的人物关系变化“{relationship_change}”未在其引用分镜的动作、台词或生成提示中直接体现；请补充可拍摄互动，或修正镜头引用。")
            if str(step.get("script_evidence", "")) not in audit_script:
                add("warning", "CAUSAL_SCRIPT_MISMATCH", f"因果链第{index}步的剧本证据无法在 full_script 原文中定位。")
            shot_refs = step.get("storyboard_indices")
            if not isinstance(shot_refs, list) or not shot_refs:
                add("warning", "CAUSAL_STORYBOARD_MISSING", f"因果链第{index}步没有引用对应分镜。")
            elif any(isinstance(ref, bool) or not isinstance(ref, int) or ref < 1 or ref > len(storyboard) for ref in shot_refs):
                add("warning", "CAUSAL_STORYBOARD_MISMATCH", f"因果链第{index}步引用了不存在的分镜位置。")
    if len(checked.get("alternative_directions", [])) < 2:
        add("warning", "ALT_DIRECTIONS", "备选故事方向少于两个；尚未满足多方向创作要求。")

    character_names = {
        str(item.get("name", "")).strip()
        for item in checked.get("characters", [])
        if isinstance(item, dict) and str(item.get("name", "")).strip()
    }
    for index, character in enumerate(checked.get("characters", []), 1):
        if not isinstance(character, dict):
            add("warning", "CHARACTER_PROFILE_INCOMPLETE", f"第{index}个人物设定格式无效。")
            continue
        for field in ("goal", "motivation", "fear_or_secret", "relationship", "relationship_dynamics", "decision_pressure", "arc"):
            if not str(character.get(field, "")).strip():
                add("warning", "CHARACTER_MOTIVATION_INCOMPLETE", f"人物“{character.get('name', f'第{index}人')}”缺少 {field}，请复核其行动动机与关系因果。")
    # A77: check whether important causal events are represented by referenced, shootable shots.
    # Deterministic text coverage is not proof of acting quality or semantic foreshadowing.
    shot_texts: list[str] = []
    for shot in storyboard:
        shot_texts.append(" ".join(str(shot.get(key, "")) for key in (
            "action", "dialogue", "product_integration", "generation_prompt",
            "narrative_function", "story_event_reference"
        )).casefold())
    # A78: trace character actions to motivation, available knowledge and pressure.
    full_script_for_character_audit = str(checked.get("full_script", ""))
    for shot_index, shot in enumerate(storyboard, 1):
        shot_characters = [str(x).strip() for x in shot.get("characters", []) if str(x).strip()]
        bases = shot.get("character_action_basis", [])
        if not isinstance(bases, list):
            bases = []
        bases_by_name = {
            str(item.get("character_name", "")).strip(): item
            for item in bases if isinstance(item, dict) and str(item.get("character_name", "")).strip()
        }
        # A79: action-basis records must map to declared characters in this exact shot.
        for basis_name in bases_by_name:
            if basis_name not in shot_characters:
                add("warning", "CHARACTER_ACTION_BASIS_NOT_IN_SHOT", f"第{shot_index}镜行动依据记录了“{basis_name}”，但该人物不在本镜人物列表中；请检查人物/镜头绑定。")
            if basis_name not in character_names:
                add("warning", "CHARACTER_ACTION_BASIS_UNKNOWN_CHARACTER", f"第{shot_index}镜行动依据引用了人物“{basis_name}”，但人物设定表中没有该人物。")
        for character_name in shot_characters:
            basis = bases_by_name.get(character_name)
            if basis is None:
                add("warning", "CHARACTER_ACTION_BASIS_MISSING", f"第{shot_index}镜人物“{character_name}”缺少行动依据记录；请说明其目标/动机、已知信息、决策压力和选择理由。")
                continue
            required_basis = ("goal_or_motivation", "known_information", "knowledge_source", "decision_pressure", "choice_rationale")
            missing_basis = [field for field in required_basis if not str(basis.get(field, "")).strip()]
            if missing_basis:
                add("warning", "CHARACTER_ACTION_BASIS_INCOMPLETE", f"第{shot_index}镜人物“{character_name}”的行动依据缺少：{', '.join(missing_basis)}。")
            knowledge_source = str(basis.get("knowledge_source", "")).strip()
            if knowledge_source and knowledge_source not in full_script_for_character_audit:
                add("warning", "CHARACTER_KNOWLEDGE_SOURCE_UNTRACEABLE", f"第{shot_index}镜人物“{character_name}”所依赖的信息来源无法在 full_script 原文中定位；请核实人物是否提前知道了不应知道的信息。")
            # A82: distinguish information learned during the depicted story from pre-existing knowledge.
            knowledge_origin = str(basis.get("knowledge_origin", "")).strip()
            source_refs = basis.get("knowledge_source_storyboard_indices")
            if knowledge_origin not in ("storyboard", "preexisting"):
                add("warning", "CHARACTER_KNOWLEDGE_TIMELINE_UNSPECIFIED", f"第{shot_index}镜人物“{character_name}”没有说明信息是在剧情中获得还是故事开始前已知。")
            if not isinstance(source_refs, list):
                add("warning", "CHARACTER_KNOWLEDGE_SOURCE_SHOTS_INVALID", f"第{shot_index}镜人物“{character_name}”的信息来源镜头必须使用列表。")
                source_refs = []
            valid_source_refs = [ref for ref in source_refs if isinstance(ref, int) and not isinstance(ref, bool) and 1 <= ref <= len(storyboard)]
            if len(valid_source_refs) != len(source_refs):
                add("warning", "CHARACTER_KNOWLEDGE_SOURCE_SHOTS_INVALID", f"第{shot_index}镜人物“{character_name}”引用了不存在的信息来源镜头。")
            if knowledge_origin == "preexisting":
                if source_refs:
                    add("warning", "CHARACTER_KNOWLEDGE_PREEXISTING_HAS_SHOTS", f"第{shot_index}镜人物“{character_name}”标记信息为故事开始前已知，却仍引用剧情内来源镜头。")
                if not str(basis.get("known_information", "")).strip():
                    add("warning", "CHARACTER_KNOWN_INFORMATION_MISSING", f"第{shot_index}镜人物“{character_name}”没有说明故事开始前已知的信息。")
            elif knowledge_origin == "storyboard":
                if not valid_source_refs:
                    add("warning", "CHARACTER_KNOWLEDGE_SOURCE_SHOTS_MISSING", f"第{shot_index}镜人物“{character_name}”声称在剧情中获得信息，但没有有效的信息揭示镜头。")
                if any(ref >= shot_index for ref in valid_source_refs):
                    add("warning", "CHARACTER_KNOWLEDGE_REVEALED_LATER", f"第{shot_index}镜人物“{character_name}”引用的信息来源镜头没有早于当前镜头；可能使用了尚未获知的信息。")
                if knowledge_source and valid_source_refs:
                    missing_source_shots = [ref for ref in valid_source_refs if knowledge_source.casefold() not in shot_texts[ref - 1].casefold()]
                    if missing_source_shots:
                        add("warning", "CHARACTER_KNOWLEDGE_SOURCE_NOT_IN_SOURCE_SHOT", f"第{shot_index}镜人物“{character_name}”声明的信息来源原文没有出现在引用的信息揭示镜头中；请修正来源引用或补充可观察的揭示动作/台词。")
    if isinstance(causal_chain, list):
        for step_index, step in enumerate(causal_chain, 1):
            if not isinstance(step, dict):
                continue
            choice = str(step.get("character_choice", "")).strip()
            refs = step.get("storyboard_indices", [])
            valid_refs = [ref for ref in refs if isinstance(ref, int) and not isinstance(ref, bool) and 1 <= ref <= len(storyboard)] if isinstance(refs, list) else []
            if choice and valid_refs:
                referenced_text = " ".join(shot_texts[ref - 1] for ref in valid_refs)
                if choice.casefold() not in referenced_text:
                    add("warning", "CHARACTER_CHOICE_NOT_SHOWN", f"因果链第{step_index}步的人物选择“{choice}”没有直接体现在引用镜头中；请补充可拍摄的选择动作或修正镜头引用。")

    if isinstance(causal_chain, list):
        for step_index, step in enumerate(causal_chain, 1):
            if not isinstance(step, dict):
                continue
            event = str(step.get("event", "")).strip()
            refs = step.get("storyboard_indices", [])
            valid_refs = [ref for ref in refs if isinstance(ref, int) and not isinstance(ref, bool) and 1 <= ref <= len(storyboard)] if isinstance(refs, list) else []
            if event and valid_refs:
                referenced_text = " ".join(shot_texts[ref - 1] for ref in valid_refs)
                if event.casefold() not in referenced_text:
                    add("warning", "CAUSAL_EVENT_NOT_SHOWN", f"因果链第{step_index}步“{event}”虽引用了分镜，但事件描述没有直接出现在对应镜头动作/台词/生成提示中；请补成可拍摄证据或修正引用。")
    turning_point = str((story_engine or {}).get("turning_point", "")).strip() if isinstance(story_engine, dict) else ""
    if turning_point and turning_point.casefold() not in " ".join(shot_texts):
        add("warning", "TURNING_POINT_NOT_STORYBOARDED", "故事引擎的关键转折未在任何分镜动作、台词或生成提示中直接体现；请补出角色发现/选择/行动的可拍摄镜头。")
    setup_payoff = str((story_engine or {}).get("setup_and_payoff", "")).strip() if isinstance(story_engine, dict) else ""
    if setup_payoff and setup_payoff.casefold() not in " ".join(shot_texts):
        add("warning", "SETUP_PAYOFF_NOT_STORYBOARDED", "伏笔与兑现设计未在分镜文本中直接体现；请分别标明前置线索与兑现动作，避免反转只存在于梗概。")

    # A83: track promises, misunderstandings and action consequences through later shots.
    obligations = checked.get("narrative_obligations")
    if not isinstance(obligations, list):
        add("warning", "NARRATIVE_OBLIGATIONS_UNSPECIFIED", "未提供 narrative_obligations；请追踪会影响后续剧情的承诺、误解与行动后果，旧方案仍可读取。")
        obligations = []
    valid_obligation_kinds = {"commitment", "misunderstanding", "action_consequence"}
    valid_obligation_statuses = {"open", "resolved", "intentionally_abandoned"}
    for obligation_index, item in enumerate(obligations, 1):
        if not isinstance(item, dict):
            add("warning", "NARRATIVE_OBLIGATION_INVALID", f"第{obligation_index}项剧情承接事项不是对象。")
            continue
        kind = str(item.get("kind", "")).strip()
        character_name = str(item.get("character_name", "")).strip()
        description = str(item.get("obligation", "")).strip()
        origin_evidence = str(item.get("origin_evidence", "")).strip()
        expected = str(item.get("expected_follow_through", "")).strip()
        status = str(item.get("status", "")).strip()
        origin_index = item.get("origin_storyboard_index")
        follow_refs = item.get("follow_through_storyboard_indices")
        if kind not in valid_obligation_kinds:
            add("warning", "NARRATIVE_OBLIGATION_KIND_INVALID", f"第{obligation_index}项剧情承接事项类型无效；应为 commitment、misunderstanding 或 action_consequence。")
        if not character_name or character_name not in character_names:
            add("warning", "NARRATIVE_OBLIGATION_UNKNOWN_CHARACTER", f"第{obligation_index}项剧情承接事项缺少有效人物，或人物“{character_name}”未在角色设定表中定义。")
        if not description:
            add("warning", "NARRATIVE_OBLIGATION_DESCRIPTION_MISSING", f"第{obligation_index}项剧情承接事项缺少 obligation 描述。")
        if not origin_evidence:
            add("warning", "NARRATIVE_OBLIGATION_ORIGIN_EVIDENCE_MISSING", f"第{obligation_index}项剧情承接事项缺少来源证据。")
        valid_origin = isinstance(origin_index, int) and not isinstance(origin_index, bool) and 1 <= origin_index <= len(storyboard)
        if not valid_origin:
            add("warning", "NARRATIVE_OBLIGATION_ORIGIN_INVALID", f"第{obligation_index}项剧情承接事项引用了无效的来源分镜位置。")
        elif origin_evidence:
            origin_shot = storyboard[origin_index - 1]
            origin_text = " ".join(str(origin_shot.get(key, "")) for key in (
                "action", "dialogue", "generation_prompt", "narrative_function", "story_event_reference"
            )).casefold() if isinstance(origin_shot, dict) else ""
            if origin_evidence.casefold() not in origin_text:
                add("warning", "NARRATIVE_OBLIGATION_ORIGIN_NOT_SHOWN", f"第{obligation_index}项剧情承接事项的来源证据未在第{origin_index}镜动作、台词或提示文本中找到。")
        if status not in valid_obligation_statuses:
            add("warning", "NARRATIVE_OBLIGATION_STATUS_INVALID", f"第{obligation_index}项剧情承接事项状态无效；应为 open、resolved 或 intentionally_abandoned。")
        if not isinstance(follow_refs, list):
            add("warning", "NARRATIVE_OBLIGATION_FOLLOW_SHOTS_INVALID", f"第{obligation_index}项剧情承接事项的后续镜头引用必须是列表。")
            follow_refs = []
        valid_follow_refs = [
            ref for ref in follow_refs
            if isinstance(ref, int) and not isinstance(ref, bool) and 1 <= ref <= len(storyboard)
        ]
        if len(valid_follow_refs) != len(follow_refs):
            add("warning", "NARRATIVE_OBLIGATION_FOLLOW_SHOTS_INVALID", f"第{obligation_index}项剧情承接事项引用了不存在的后续分镜位置。")
        if valid_origin and any(ref <= origin_index for ref in valid_follow_refs):
            add("warning", "NARRATIVE_OBLIGATION_FOLLOW_SHOTS_NOT_LATER", f"第{obligation_index}项剧情承接事项的后续镜头必须严格晚于来源镜头。")
        if not expected:
            add("warning", "NARRATIVE_OBLIGATION_FOLLOW_THROUGH_MISSING", f"第{obligation_index}项剧情承接事项没有说明后续应兑现、澄清或体现的具体结果。")
        if status == "intentionally_abandoned" and not str(item.get("resolution_rationale", "")).strip():
            add("warning", "NARRATIVE_OBLIGATION_ABANDONMENT_UNEXPLAINED", f"第{obligation_index}项剧情承接事项标记为有意放弃，但没有说明剧情依据。")
        if status in {"open", "resolved"} and not valid_follow_refs:
            add("warning", "NARRATIVE_OBLIGATION_FOLLOW_SHOTS_MISSING", f"第{obligation_index}项剧情承接事项仍需后续承接，但没有引用有效的后续镜头。")
        if expected and valid_follow_refs:
            follow_text = " ".join(shot_texts[ref - 1] for ref in valid_follow_refs)
            if expected.casefold() not in follow_text:
                add("warning", "NARRATIVE_OBLIGATION_FOLLOW_THROUGH_NOT_SHOWN", f"第{obligation_index}项剧情承接事项要求后续体现“{expected}”，但引用镜头中未找到对应文本。")

    # A84: cross-episode obligation handoff checks. Only explicit opt-in items are
    # required to cross episode boundaries, preserving compatibility with older plans.
    episode_rows = checked.get("episodes", [])
    episode_by_number: dict[int, dict[str, Any]] = {}
    if isinstance(episode_rows, list):
        for position, episode in enumerate(episode_rows, 1):
            if not isinstance(episode, dict):
                continue
            try:
                episode_number = int(episode.get("episode_number", position))
            except (TypeError, ValueError):
                continue
            episode_by_number[episode_number] = episode
    shot_episode_numbers: dict[int, int] = {}
    for shot_index, shot in enumerate(storyboard, 1):
        if not isinstance(shot, dict):
            continue
        try:
            shot_episode_numbers[shot_index] = int(shot.get("episode_number", 1) or 1)
        except (TypeError, ValueError):
            shot_episode_numbers[shot_index] = 1
    for obligation_index, item in enumerate(obligations, 1):
        if not isinstance(item, dict):
            continue
        cross_episode_required = item.get("cross_episode_required", False)
        if not isinstance(cross_episode_required, bool):
            add("warning", "NARRATIVE_OBLIGATION_CROSS_EPISODE_FLAG_INVALID", f"第{obligation_index}项剧情承接事项的 cross_episode_required 必须是布尔值。")
            continue
        if not cross_episode_required:
            continue
        origin_index = item.get("origin_storyboard_index")
        if not isinstance(origin_index, int) or isinstance(origin_index, bool) or origin_index not in shot_episode_numbers:
            continue
        origin_episode = shot_episode_numbers[origin_index]
        later_episode_numbers = sorted(number for number in episode_by_number if number > origin_episode)
        if not later_episode_numbers:
            add("warning", "NARRATIVE_OBLIGATION_CROSS_EPISODE_TARGET_MISSING", f"第{obligation_index}项剧情承接事项标记为跨集承接，但来源在第{origin_episode}集之后没有可承接的后续集。")
            continue
        follow_refs = item.get("follow_through_storyboard_indices", [])
        later_follow_refs = [
            ref for ref in follow_refs
            if isinstance(ref, int) and not isinstance(ref, bool)
            and ref in shot_episode_numbers and shot_episode_numbers[ref] > origin_episode
        ] if isinstance(follow_refs, list) else []
        if not later_follow_refs:
            add("warning", "NARRATIVE_OBLIGATION_CROSS_EPISODE_FOLLOW_THROUGH_MISSING", f"第{obligation_index}项剧情承接事项要求跨集延续，但没有引用来源集之后的分镜。")
        if str(item.get("status", "")).strip() != "open":
            continue
        obligation_text = str(item.get("obligation", "")).strip().casefold()
        expected_text = str(item.get("expected_follow_through", "")).strip().casefold()
        origin_episode_row = episode_by_number.get(origin_episode, {})
        origin_state = origin_episode_row.get("continuity_state", {}) if isinstance(origin_episode_row, dict) else {}
        if not isinstance(origin_state, dict):
            origin_state = {}
        origin_handoff_values = [str(origin_state.get("ending_state", ""))]
        for field in ("unresolved_threads", "next_episode_requirements"):
            value = origin_state.get(field, [])
            if isinstance(value, list):
                origin_handoff_values.extend(str(entry) for entry in value)
        origin_handoff_text = " ".join(origin_handoff_values).casefold()
        if not ((obligation_text and obligation_text in origin_handoff_text) or (expected_text and expected_text in origin_handoff_text)):
            add("warning", "NARRATIVE_OBLIGATION_NOT_IN_EPISODE_HANDOFF", f"第{obligation_index}项仍未解决的跨集事项没有写入第{origin_episode}集的未解线索/下一集承接要求/集末状态。")
        next_episode = episode_by_number.get(later_episode_numbers[0], {})
        next_state = next_episode.get("continuity_state", {}) if isinstance(next_episode, dict) else {}
        if not isinstance(next_state, dict):
            next_state = {}
        next_values = [str(next_state.get("opening_state", ""))]
        unresolved = next_state.get("unresolved_threads", [])
        if isinstance(unresolved, list):
            next_values.extend(str(entry) for entry in unresolved)
        next_handoff_text = " ".join(next_values).casefold()
        if not ((obligation_text and obligation_text in next_handoff_text) or (expected_text and expected_text in next_handoff_text)):
            add("warning", "NARRATIVE_OBLIGATION_NOT_CARRIED_FORWARD", f"第{obligation_index}项仍未解决的跨集事项没有在第{later_episode_numbers[0]}集开场状态或未解线索中继续出现。")

    # A85: explicit cross-episode character and relationship state ledger.
    # Legacy episodes without this optional ledger remain compatible.
    valid_character_state_statuses = {"established", "changed", "persisting", "resolved"}
    episode_character_states: dict[int, dict[tuple[str, str], dict[str, Any]]] = {}
    for episode_number, episode in sorted(episode_by_number.items()):
        if not isinstance(episode, dict):
            continue
        continuity_state = episode.get("continuity_state", {})
        if not isinstance(continuity_state, dict) or "character_state_ledger" not in continuity_state:
            continue
        records = continuity_state.get("character_state_ledger")
        if not isinstance(records, list):
            add("warning", "CHARACTER_STATE_LEDGER_INVALID", f"第{episode_number}集 character_state_ledger 必须是列表。")
            continue
        state_map: dict[tuple[str, str], dict[str, Any]] = {}
        script = str(episode.get("full_script", ""))
        shots = episode.get("storyboard", [])
        if not isinstance(shots, list):
            shots = []
        shot_texts_local = [
            " ".join(str(shot.get(key, "")) for key in ("action", "dialogue", "generation_prompt", "narrative_function", "story_event_reference")).casefold()
            for shot in shots if isinstance(shot, dict)
        ]
        for record_index, record in enumerate(records, 1):
            if not isinstance(record, dict):
                add("warning", "CHARACTER_STATE_RECORD_INVALID", f"第{episode_number}集人物状态台账第{record_index}项必须是对象。")
                continue
            name = str(record.get("character_name", "")).strip()
            dimension = str(record.get("dimension", "")).strip()
            description = str(record.get("state_description", "")).strip()
            status = str(record.get("status", "")).strip()
            evidence = str(record.get("evidence", "")).strip()
            if not name or name not in character_names:
                add("warning", "CHARACTER_STATE_UNKNOWN_CHARACTER", f"第{episode_number}集人物状态台账引用了未定义人物“{name}”。")
            if not dimension:
                add("warning", "CHARACTER_STATE_DIMENSION_MISSING", f"第{episode_number}集人物状态台账缺少 dimension。")
            if not description:
                add("warning", "CHARACTER_STATE_DESCRIPTION_MISSING", f"第{episode_number}集人物状态台账缺少 state_description。")
            if status not in valid_character_state_statuses:
                add("warning", "CHARACTER_STATE_STATUS_INVALID", f"第{episode_number}集人物状态 status 无效。")
            persist = record.get("must_persist", False)
            if not isinstance(persist, bool):
                add("warning", "CHARACTER_STATE_PERSIST_FLAG_INVALID", f"第{episode_number}集人物状态 must_persist 必须是布尔值。")
                persist = False
            if not evidence:
                add("warning", "CHARACTER_STATE_EVIDENCE_MISSING", f"第{episode_number}集人物状态缺少 evidence。")
            elif evidence.casefold() not in script.casefold() and not any(evidence.casefold() in text for text in shot_texts_local):
                add("warning", "CHARACTER_STATE_EVIDENCE_UNTRACEABLE", f"第{episode_number}集人物“{name}”的状态证据无法在本集剧本或分镜中定位。")
            refs = record.get("storyboard_indices", [])
            if not isinstance(refs, list):
                add("warning", "CHARACTER_STATE_SHOTS_INVALID", f"第{episode_number}集 storyboard_indices 必须是列表。")
                refs = []
            valid_refs = [ref for ref in refs if isinstance(ref, int) and not isinstance(ref, bool) and 1 <= ref <= len(shots)]
            if len(valid_refs) != len(refs):
                add("warning", "CHARACTER_STATE_SHOTS_INVALID", f"第{episode_number}集人物状态引用了不存在的本集分镜。")
            if persist and status != "resolved" and not valid_refs:
                add("warning", "CHARACTER_STATE_SHOTS_MISSING", f"第{episode_number}集人物“{name}”的跨集状态未引用有效本集分镜。")
            # A86: changed states need an ordered trigger -> change -> reaction -> consequence chain.
            if status == "changed":
                episode = episode_by_number.get(episode_number, {})
                episode_script = str(episode.get("full_script", "")) if isinstance(episode, dict) else ""
                episode_shots = episode.get("storyboard", []) if isinstance(episode, dict) else []
                if not isinstance(episode_shots, list):
                    episode_shots = []
                def _state_refs(field: str, code_name: str) -> list[int]:
                    raw_refs = record.get(field, [])
                    if not isinstance(raw_refs, list):
                        add("warning", code_name, f"第{episode_number}集人物“{name}”的 {field} 必须是本集分镜位置列表。")
                        return []
                    valid = [value for value in raw_refs if isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= len(episode_shots)]
                    if len(valid) != len(raw_refs):
                        add("warning", code_name, f"第{episode_number}集人物“{name}”的 {field} 引用了不存在的本集分镜。")
                    return sorted(set(valid))
                trigger_event = str(record.get("trigger_event", "")).strip()
                trigger_refs = _state_refs("trigger_storyboard_indices", "CHARACTER_STATE_TRIGGER_SHOTS_INVALID")
                change_refs = _state_refs("change_storyboard_indices", "CHARACTER_STATE_CHANGE_SHOTS_INVALID")
                reaction_evidence = str(record.get("reaction_evidence", "")).strip()
                reaction_refs = _state_refs("reaction_storyboard_indices", "CHARACTER_STATE_REACTION_SHOTS_INVALID")
                consequence_evidence = str(record.get("downstream_consequence_evidence", "")).strip()
                consequence_refs = _state_refs("downstream_storyboard_indices", "CHARACTER_STATE_CONSEQUENCE_SHOTS_INVALID")
                def _evidence_located(value: str, refs: list[int]) -> bool:
                    if not value:
                        return False
                    if value.casefold() in episode_script.casefold():
                        return True
                    return any(
                        value.casefold() in " ".join(
                            str(episode_shots[index - 1].get(field, ""))
                            for field in ("action", "dialogue", "generation_prompt", "narrative_function", "story_event_reference")
                        ).casefold()
                        for index in refs
                        if isinstance(episode_shots[index - 1], dict)
                    )
                if not trigger_event or not trigger_refs or not _evidence_located(trigger_event, trigger_refs):
                    add("warning", "CHARACTER_STATE_TRIGGER_MISSING", f"第{episode_number}集人物“{name}”的状态标记 changed，但缺少可定位的触发事件及其分镜引用。")
                if not change_refs:
                    add("warning", "CHARACTER_STATE_CHANGE_SHOTS_MISSING", f"第{episode_number}集人物“{name}”标记 changed，但没有引用状态实际改变发生的镜头。")
                if trigger_refs and change_refs and max(trigger_refs) >= min(change_refs):
                    add("warning", "CHARACTER_STATE_TRIGGER_NOT_BEFORE_CHANGE", f"第{episode_number}集人物“{name}”的触发事件镜头必须早于状态改变镜头。")
                if not reaction_evidence or not reaction_refs or not _evidence_located(reaction_evidence, reaction_refs):
                    add("warning", "CHARACTER_STATE_REACTION_MISSING", f"第{episode_number}集人物“{name}”的状态变化缺少可定位的人物反应及其分镜引用。")
                elif change_refs and min(reaction_refs) <= max(change_refs):
                    add("warning", "CHARACTER_STATE_REACTION_NOT_LATER", f"第{episode_number}集人物“{name}”的反应镜头必须位于状态改变镜头之后。")
                # A87: require a concrete, observable performance cue, not only an abstract emotion label.
                manifestation = str(record.get("observable_manifestation", "")).strip()
                manifestation_refs = _state_refs("observable_storyboard_indices", "CHARACTER_STATE_MANIFESTATION_SHOTS_INVALID")
                abstract_only_markers = ("感到愤怒", "感到怀疑", "感到信任", "感到原谅", "内心愤怒", "内心怀疑", "态度改变", "心态改变", "不再信任", "开始信任", "原谅了对方")
                manifestation_is_abstract = manifestation and any(
                    marker in manifestation for marker in abstract_only_markers
                ) and not any(
                    marker in manifestation for marker in ("说", "问", "喊", "退", "躲", "握", "放下", "转身", "推开", "递", "拒绝", "点头", "摇头", "皱眉", "避开", "停下", "看向", "移开", "哭", "笑", "沉默", "拿起", "交出", "删除", "关闭", "打开", "后退", "靠近", "拥抱", "拍", "抓住", "挡住", "藏起", "离开", "行动")
                )
                if not manifestation or not manifestation_refs:
                    add("warning", "CHARACTER_STATE_MANIFESTATION_MISSING", f"第{episode_number}集人物“{name}”的状态标记 changed，但缺少可观察的表演描述或对应分镜引用。")
                elif not _evidence_located(manifestation, manifestation_refs):
                    add("warning", "CHARACTER_STATE_MANIFESTATION_NOT_SHOWN", f"第{episode_number}集人物“{name}”声明的可观察表现无法在指定分镜/剧本中定位；请把状态变化落实到动作、台词、表情或互动。")
                if manifestation_is_abstract:
                    add("warning", "CHARACTER_STATE_MANIFESTATION_TOO_ABSTRACT", f"第{episode_number}集人物“{name}”只写了抽象心理状态，未说明观众能看到或听到的行为。")
                if not consequence_evidence or not consequence_refs or not _evidence_located(consequence_evidence, consequence_refs):
                    add("warning", "CHARACTER_STATE_CONSEQUENCE_MISSING", f"第{episode_number}集人物“{name}”的状态变化缺少可定位的后续行动/剧情后果及其分镜引用。")
                elif change_refs and min(consequence_refs) <= max(change_refs):
                    add("warning", "CHARACTER_STATE_CONSEQUENCE_NOT_LATER", f"第{episode_number}集人物“{name}”的后续影响镜头必须位于状态改变镜头之后。")
            key = (name, dimension)
            if key in state_map:
                add("warning", "CHARACTER_STATE_DUPLICATE_DIMENSION", f"第{episode_number}集人物“{name}”的状态维度“{dimension}”重复声明。")
            else:
                state_map[key] = record
        episode_character_states[episode_number] = state_map

    ordered_episode_numbers = sorted(episode_by_number)
    if checked.get("format_mode") == "continuous_series":
        for position, episode_number in enumerate(ordered_episode_numbers[:-1]):
            next_number = ordered_episode_numbers[position + 1]
            for (name, dimension), previous in episode_character_states.get(episode_number, {}).items():
                if previous.get("must_persist") is not True or previous.get("status") == "resolved":
                    continue
                current = episode_character_states.get(next_number, {}).get((name, dimension))
                if current is None:
                    add("warning", "CHARACTER_STATE_NOT_CARRIED_FORWARD", f"第{episode_number}集人物“{name}”的状态维度“{dimension}”要求跨集保持，但第{next_number}集没有对应记录。")
                    continue
                old_state = str(previous.get("state_description", "")).strip()
                new_state = str(current.get("state_description", "")).strip()
                new_status = str(current.get("status", "")).strip()
                if old_state and new_state and old_state != new_state:
                    if new_status not in {"changed", "resolved"}:
                        add("warning", "CHARACTER_STATE_CHANGED_WITHOUT_DECLARATION", f"第{next_number}集人物“{name}”的状态维度“{dimension}”与上一集不一致，却未声明 changed/resolved。")
                    elif new_status == "changed":
                        transition = str(current.get("transition_evidence", "")).strip()
                        next_episode = episode_by_number.get(next_number, {})
                        next_script = str(next_episode.get("full_script", "")) if isinstance(next_episode, dict) else ""
                        next_shots = next_episode.get("storyboard", []) if isinstance(next_episode, dict) else []
                        next_shot_text = " ".join(
                            " ".join(str(shot.get(key, "")) for key in ("action", "dialogue", "generation_prompt", "narrative_function", "story_event_reference"))
                            for shot in next_shots if isinstance(shot, dict)
                        )
                        if not transition or (transition.casefold() not in next_script.casefold() and transition.casefold() not in next_shot_text.casefold()):
                            add("warning", "CHARACTER_STATE_CHANGE_UNJUSTIFIED", f"第{next_number}集人物“{name}”的状态维度“{dimension}”标记 changed，但缺少可定位的 transition_evidence。")

    seen_scene_locations: dict[str, str] = {}
    total_seconds = 0
    for number, shot in enumerate(checked.get("storyboard", []), 1):
        total_seconds += int(shot.get("duration_seconds", 0))
        if not str(shot.get("shot_type", "")).strip():
            add("warning", "SHOT_TYPE", f"第{number}镜缺少景别/镜头运动。")
        if not str(shot.get("generation_prompt", "")).strip():
            add("warning", "GENERATION_PROMPT", f"第{number}镜缺少可执行的生成提示。")
        if not str(shot.get("product_integration", "")).strip():
            add("warning", "PRODUCT_INTEGRATION", f"第{number}镜未说明商品是否出现及如何融入剧情。")
        if checked.get("drama_business_mode") == "product_short_drama_ad":
            fidelity = shot.get("product_fidelity_constraints")
            if not isinstance(fidelity, list) or not any(str(item).strip() for item in fidelity):
                add("error", "PRODUCT_FIDELITY_CONSTRAINTS", f"第{number}镜缺少商品外观/结构/功能锁定约束。")
            status = str(shot.get("visual_verification", "not_checked"))
            evidence_path = Path(str(shot.get("visual_verification_evidence", "")).strip()).expanduser()
            evidence_exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi", ".mpeg", ".mpg"}
            try:
                evidence_is_real = (
                    evidence_path.suffix.lower() in evidence_exts
                    and evidence_path.is_file()
                    and evidence_path.stat().st_size > 0
                )
            except OSError:
                evidence_is_real = False
            has_manual_evidence = (
                evidence_is_real
                and shot.get("visual_verification_method") == "manual"
                and bool(str(shot.get("visual_verification_note", "")).strip())
            )
            if status != "passed" or not has_manual_evidence:
                detail = f"状态为“{status}”"
                if status == "passed" and not has_manual_evidence:
                    detail = "虽标记为 passed，但人工核验证据文件不存在/为空/格式不支持，或缺少人工核验方式/备注"
                add("warning", "PRODUCT_VISUAL_NOT_VERIFIED", f"第{number}镜商品画面{detail}；只有关联实际存在且非空的生成画面文件并保存人工核验记录后，才能计为通过。")
        shot_characters = [str(x).strip() for x in shot.get("characters", []) if str(x).strip()]
        for name in shot_characters:
            if character_names and name not in character_names:
                add("warning", "UNKNOWN_CHARACTER", f"第{number}镜出现人物“{name}”，但人物表中没有对应设定。")
        scene = str(shot.get("scene", "")).strip()
        location = str(shot.get("location", "")).strip()
        if scene and location:
            previous = seen_scene_locations.get(scene)
            if previous and previous != location:
                add("warning", "SCENE_CONTINUITY", f"场景“{scene}”在分镜中对应不同地点（“{previous}”/“{location}”），请确认是有意变化还是连续性错误。")
            else:
                seen_scene_locations[scene] = location

    if total_seconds <= 0:
        add("error", "DURATION", "分镜总时长无效。")
    if total_seconds > 180:
        add("warning", "LONG_RUNTIME", f"当前分镜合计约{total_seconds}秒，请确认这符合本次短剧投放时长目标。")

    content_parts: list[str] = [
        str(checked.get("full_script", "")),
        str(checked.get("conflict_and_reversal", "")),
        str(checked.get("ending", "")),
        " ".join(str(x) for x in checked.get("product_truths", [])),
        " ".join(str(x) for x in checked.get("plot_beats", [])),
    ]
    for shot in checked.get("storyboard", []):
        content_parts.extend(str(shot.get(key, "")) for key in ("action", "dialogue", "product_integration", "generation_prompt"))
    script_text = "\n".join(content_parts)
    ledger = checked.get("continuity_ledger", [])
    if checked.get("format_mode") != "single_episode":
        if not isinstance(ledger, list) or len(ledger) != checked.get("episode_count"):
            add("warning", "CONTINUITY_LEDGER", "跨集连续性台账缺失或集数不完整；后续续写/修改影响分析可能不可靠。")
        else:
            for idx, item in enumerate(ledger):
                if not item.get("opening_state") or not item.get("ending_state"):
                    add("warning", "EPISODE_CONTINUITY_STATE", f"第{idx + 1}集缺少开集承接或集末状态。")
                if idx > 0 and checked.get("format_mode") == "continuous_series":
                    previous = ledger[idx - 1]
                    if not previous.get("next_episode_requirements"):
                        add("warning", "NEXT_EPISODE_HANDOFF", f"第{idx}集没有明确下一集必须承接的事项；请人工核对第{idx + 1}集是否延续前情。")
    for note in checked.get("risk_notes", []):
        note_text = str(note).strip()
        if note_text:
            add("warning", "MODEL_RISK_NOTE", f"编导模型标记的待确认风险：{note_text}")
    risky_claims = [
        ("绝对化/极限词", ("百分百", "100%", "第一", "最强", "顶级", "唯一", "绝对", "保证有效", "永久有效")),
        ("医疗/健康功效表述", ("根治", "治愈", "无副作用", "包治", "降血糖", "抗癌")),
        ("安全保证表述", ("零风险", "绝对安全", "完全无害")),
    ]
    for category, terms in risky_claims:
        matched = [term for term in terms if term in script_text]
        if matched:
            add("warning", "AD_CLAIM_REVIEW", f"检测到可能需要广告合规人工复核的{category}词语：{'、'.join(matched)}。该提示不等同于法律结论。")

    material = product_material or {}
    def flatten(value: Any) -> list[str]:
        if isinstance(value, dict):
            result: list[str] = []
            for key, item in value.items():
                result.extend(flatten(item))
            return result
        if isinstance(value, (list, tuple, set)):
            result = []
            for item in value:
                result.extend(flatten(item))
            return result
        if isinstance(value, (str, int, float)) and str(value).strip():
            return [str(value).strip()]
        return []
    trusted_text = " ".join(flatten(material))
    # A75: cross-check the product fact lock against source material and script claims.
    fact_lock = checked.get("product_fact_lock", {})
    if isinstance(fact_lock, dict):
        confirmed_facts = fact_lock.get("confirmed_facts", [])
        unknown_facts = fact_lock.get("unknown_or_unverified", [])
        if isinstance(confirmed_facts, list):
            for fact in confirmed_facts:
                claim = str(fact).strip()
                if claim and trusted_text and claim not in trusted_text:
                    add("warning", "PRODUCT_CONFIRMED_FACT_UNSUPPORTED", f"已确认商品事实“{claim}”未在当前商品资料中找到直接文本依据，请人工核实。")
                elif claim and not trusted_text:
                    add("warning", "PRODUCT_FACT_SOURCE_MISSING", "事实锁中存在已确认商品事实，但当前没有可供比对的商品资料。")
                    break
        if isinstance(unknown_facts, list):
            uncertainty_markers = ("待确认", "未确认", "未核实", "未知", "不确定", "不可声称", "不得宣称", "尚无资料")
            for fact in unknown_facts:
                claim = str(fact).strip()
                if not claim:
                    continue
                position = script_text.find(claim)
                if position >= 0:
                    context = script_text[max(0, position - 18):position + len(claim) + 18]
                    if not any(marker in context for marker in uncertainty_markers):
                        add("warning", "PRODUCT_UNKNOWN_FACT_USED", f"未核实商品信息“{claim}”出现在剧本/分镜内容中，附近未发现明确的不确定性标记，请人工核实。")
    # A76: check whether confirmed selling points appear as observable storyboard content.
    if checked.get("drama_business_mode") in {"product_placement", "product_conversion", "product_short_drama_ad"}:
        analysis = checked.get("product_analysis", {})
        points = analysis.get("selling_points", []) if isinstance(analysis, dict) else []
        shot_texts = [" ".join(str(shot.get(key, "")) for key in ("action", "product_integration", "dialogue", "generation_prompt")) for shot in checked.get("storyboard", []) if isinstance(shot, dict)]
        if isinstance(points, list):
            for point in points:
                claim = str(point).strip()
                if claim and not any(claim in text for text in shot_texts):
                    add("warning", "PRODUCT_SELLING_POINT_NOT_SHOWN", f"已确认卖点“{claim}”尚未在任何分镜动作、商品融入、台词或生成提示中被直接体现；请补充可拍摄的真实行为证据，或确认本片无需展示该卖点。")
    for truth in checked.get("product_truths", []):
        claim = str(truth).strip()
        if claim and trusted_text and claim not in trusted_text:
            add("warning", "PRODUCT_TRUTH_UNVERIFIED", f"商品事实“{claim}”未在当前商品资料中找到直接对应文本，请人工核实。")
        elif claim and not trusted_text:
            add("warning", "PRODUCT_MATERIAL_EMPTY", "当前没有可供比对的商品资料，商品事实无法自动核验。")
            break

    counts: dict[str, int] = {}
    for issue in issues:
        counts[issue["level"]] = counts.get(issue["level"], 0) + 1
    return {
        "passed": not any(issue["level"] == "error" for issue in issues),
        "status": "需人工复核" if issues else "规则检查未发现问题",
        "total_duration_seconds": total_seconds,
        "issue_count": len(issues),
        "counts": counts,
        "issues": issues,
        "limitations": [
            "本报告是确定性规则检查，不等于AI语义审查或法律意见。",
            "人物/场景一致性只能检查可结构化的信息，不能保证生成画面身份完全一致。",
            "商品事实未在资料中逐字匹配时只标记待核实，不直接判定为虚假。"
        ],
    }


def generate_next_short_drama_episode(model_router, plan: dict[str, Any],
                                      product: dict[str, Any] | None = None) -> dict[str, Any]:
    """Append one validated episode generated from the saved continuity handoff."""
    source = validate_short_drama(json.loads(json.dumps(plan, ensure_ascii=False)))
    if source.get("format_mode") == "single_episode":
        raise ShortDramaPlanError("当前是单集短剧，不能直接续写；请先创建连续多集或系列短剧方案。")
    episodes = source.get("episodes", [])
    if not episodes:
        raise ShortDramaPlanError("当前方案没有分集剧本，无法续写下一集。")
    previous_number = int(source.get("episode_count", len(episodes)))
    if previous_number >= 50:
        raise ShortDramaPlanError("短剧最多支持50集，当前已达到上限。")
    previous = episodes[-1]
    state = previous.get("continuity_state", {})
    if not isinstance(state, dict):
        raise ShortDramaPlanError(f"第{previous_number}集缺少连续性状态，无法安全续写。")
    next_number = previous_number + 1
    handoff = {
        "previous_episode": previous,
        "previous_episode_continuity": state,
        "continuity_ledger": source.get("continuity_ledger") or build_episode_continuity_ledger(source),
        "series_bible": source.get("series_bible", {}),
        "characters": source.get("characters", []),
        "world": source.get("world", ""),
        "genre": source.get("genre", ""),
        "drama_business_mode": source.get("drama_business_mode", "general"),
        "product_truths": source.get("product_truths", []),
        "product_material": product or {},
        "format_mode": source.get("format_mode"),
        "new_episode_number": next_number,
    }
    prompt = (
        "你是负责续写既有短剧的编剧。只生成下一集的JSON对象，不要输出整季，不要改写旧集。\n"
        f"本次必须生成第{next_number}集。输入包含上一集完整内容、人物状态、连续性台账和系列设定。\n"
        "连续多集：必须因果承接上一集结尾、人物变化、未解线索和下一集承接要求；不能让人物忘记已发生的事，不能无解释地改变地点、关系或道具状态。\n"
        "系列短剧：共享世界观与人物设定，但本集故事可以相对独立；只继承必要的长期人物状态，不要强行把上一集悬念变成本集主线。\n"
        "通用AI短剧可以不出现商品；商品植入/转化遵守商品事实，不编造功效或参数。\n"
        "输出对象必须包含 episode_number、title、logline、plot_beats、ending_hook、full_script、continuity_state、storyboard。"
        "continuity_state 必须含 opening_state、character_state_changes（列表）、unresolved_threads（列表）、ending_state、next_episode_requirements（列表）；连续多集还应提供 character_state_ledger，逐人物记录心理/知识/秘密/承诺/关系等需跨集保持的状态、状态维度、明确状态、status、must_persist、证据及本集分镜位置。若状态改变，必须给出可在本集剧本或分镜中定位的 transition_evidence；不得无解释重置人物关系、已知信息或承诺。"
        "storyboard 至少一个镜头；每个镜头含 index、scene、location、characters（列表）、action、dialogue、product_integration、asset_needs（列表）、actor_requirements（列表）、scene_requirements（列表）、product_asset_requirements（列表）、shot_type、duration_seconds、generation_prompt。"
        "index 从本集第1镜开始。只返回合法JSON。\n输入：\n"
        + json.dumps(handoff, ensure_ascii=False, indent=2)
    )
    profile = model_router.resolve_route("AI短剧编导")
    try:
        generated = model_router.complete_json(profile, prompt, function="AI短剧编导")
    except TypeError as exc:
        if "unexpected keyword argument 'function'" not in str(exc):
            raise
        generated = model_router.complete_json(profile, prompt)
    if isinstance(generated, dict) and isinstance(generated.get("episode"), dict):
        generated = generated["episode"]
    if not isinstance(generated, dict):
        raise ShortDramaPlanError("模型没有返回有效的下一集JSON对象。")
    try:
        returned_number = int(generated.get("episode_number", next_number))
    except (TypeError, ValueError) as exc:
        raise ShortDramaPlanError("续写结果的集数编号无效。") from exc
    if returned_number != next_number:
        raise ShortDramaPlanError(f"模型返回第{returned_number}集，但本次要求第{next_number}集；原方案未修改。")
    required = ("title", "logline", "plot_beats", "ending_hook", "full_script", "continuity_state", "storyboard")
    missing = [key for key in required if key not in generated]
    if missing:
        raise ShortDramaPlanError("续写结果缺少字段：" + "、".join(missing))
    state = generated.get("continuity_state")
    if not isinstance(state, dict):
        raise ShortDramaPlanError(f"第{next_number}集缺少连续性状态。")
    for key in ("opening_state", "character_state_changes", "unresolved_threads", "ending_state", "next_episode_requirements"):
        if key not in state:
            raise ShortDramaPlanError(f"第{next_number}集连续性状态缺少字段 {key}。")
    if not str(state.get("opening_state", "")).strip() or not str(state.get("ending_state", "")).strip():
        raise ShortDramaPlanError(f"第{next_number}集必须填写开集承接状态和集末状态。")
    if not all(isinstance(state.get(key), list) for key in ("character_state_changes", "unresolved_threads", "next_episode_requirements")):
        raise ShortDramaPlanError(f"第{next_number}集的人物变化、未解线索和下一集承接要求必须使用列表。")
    if not isinstance(generated.get("storyboard"), list) or not generated["storyboard"]:
        raise ShortDramaPlanError(f"第{next_number}集没有分镜。")
    generated["episode_number"] = next_number
    new_shots = []
    for index, shot in enumerate(generated["storyboard"], 1):
        if not isinstance(shot, dict) or not shot.get("scene") or not shot.get("action"):
            raise ShortDramaPlanError(f"第{next_number}集第{index}镜缺少场景或动作。")
        shot["episode_number"] = next_number
        shot["index"] = index
        new_shots.append(shot)
    result = json.loads(json.dumps(source, ensure_ascii=False))
    result["episodes"].append(generated)
    result["episode_count"] = next_number
    result["storyboard"].extend(new_shots)
    result["full_script"] = str(result.get("full_script", "")).rstrip() + f"\n\n第{next_number}集：{generated.get('title', '')}\n" + str(generated.get("full_script", ""))
    result["continuity_ledger"] = build_episode_continuity_ledger(result)
    result["next_episode_generated_at"] = __import__("datetime").datetime.now().isoformat(timespec="seconds")
    return validate_short_drama(result)


def analyze_episode_continuity_impact(model_router, plan: dict[str, Any], episode_number: int) -> dict[str, Any]:
    """Ask the director model to identify downstream episode risks without rewriting any episode."""
    source = validate_short_drama(json.loads(json.dumps(plan, ensure_ascii=False)))
    episodes = source.get("episodes", [])
    if not isinstance(episodes, list) or len(episodes) < 2:
        raise ShortDramaPlanError("剧情影响分析至少需要包含两集的短剧方案。")
    try:
        selected_number = int(episode_number)
    except (TypeError, ValueError) as exc:
        raise ShortDramaPlanError("请选择有效的集数。") from exc
    selected = next((e for e in episodes if isinstance(e, dict) and int(e.get("episode_number", 0) or 0) == selected_number), None)
    if selected is None:
        raise ShortDramaPlanError(f"方案中不存在第{selected_number}集。")
    downstream = [e for e in episodes if isinstance(e, dict) and int(e.get("episode_number", 0) or 0) > selected_number]
    if not downstream:
        raise ShortDramaPlanError(f"第{selected_number}集之后没有后续集数，无需进行后续剧情影响分析。")
    payload = {
        "format_mode": source.get("format_mode"),
        "series_bible": source.get("series_bible", {}),
        "selected_episode": selected,
        "downstream_episodes": downstream,
        "continuity_ledger": source.get("continuity_ledger") or build_episode_continuity_ledger(source),
        "product_fact_lock": source.get("product_fact_lock", {}),
        "required_output": {
            "source_episode_number": selected_number,
            "overall_risk": "low / medium / high",
            "summary": "总体影响摘要",
            "affected_episodes": [{
                "episode_number": "必须是实际存在且晚于 source_episode_number 的集数",
                "risk": "low / medium / high",
                "affected_elements": ["受影响的人物状态/线索/道具/地点/商品事实/因果"],
                "evidence": ["引用具体的原剧情字段或内容说明原因"],
                "recommended_actions": ["建议如何同步调整，不要直接改写剧本"]
            }],
            "unaffected_reasoning": ["为什么其他后续集数暂时看起来不受影响"],
            "human_review_required": True
        }
    }
    prompt = (
        "你是负责整季连续性的短剧总编剧。请分析指定集数的剧情变化可能对后续集造成的影响。"
        "你只能分析现有内容，不得编造未提供的剧情事实；每个受影响集必须引用具体字段作为依据。"
        "区分明确冲突、可能风险和无证据猜测；不要直接改写或覆盖任何集的剧本/分镜。"
        "只输出合法JSON。human_review_required 必须为 true。\n输入：\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
    )
    profile = model_router.resolve_route("AI短剧编导")
    try:
        generated = model_router.complete_json(profile, prompt, function="AI短剧编导")
    except TypeError as exc:
        if "unexpected keyword argument 'function'" not in str(exc):
            raise
        generated = model_router.complete_json(profile, prompt)
    if isinstance(generated, dict) and isinstance(generated.get("report"), dict):
        generated = generated["report"]
    if not isinstance(generated, dict):
        raise ShortDramaPlanError("模型没有返回有效的剧情影响分析JSON。")
    if int(generated.get("source_episode_number", -1) or -1) != selected_number:
        raise ShortDramaPlanError("剧情影响报告的源集编号与所选集数不一致。")
    if generated.get("overall_risk") not in {"low", "medium", "high"}:
        raise ShortDramaPlanError("剧情影响报告缺少有效的 overall_risk（low/medium/high）。")
    if not str(generated.get("summary", "")).strip():
        raise ShortDramaPlanError("剧情影响报告缺少总体摘要。")
    valid_downstream = {int(e.get("episode_number", 0) or 0) for e in downstream}
    affected = generated.get("affected_episodes")
    if not isinstance(affected, list):
        raise ShortDramaPlanError("剧情影响报告的 affected_episodes 必须是列表。")
    for item in affected:
        if not isinstance(item, dict):
            raise ShortDramaPlanError("受影响集报告必须是对象。")
        try:
            number = int(item.get("episode_number", 0) or 0)
        except (TypeError, ValueError) as exc:
            raise ShortDramaPlanError("受影响集编号无效。") from exc
        if number not in valid_downstream:
            raise ShortDramaPlanError(f"模型报告了不存在或非后续集数：第{number}集。")
        if item.get("risk") not in {"low", "medium", "high"}:
            raise ShortDramaPlanError(f"第{number}集缺少有效风险等级。")
        for key in ("affected_elements", "evidence", "recommended_actions"):
            if not isinstance(item.get(key), list):
                raise ShortDramaPlanError(f"第{number}集的 {key} 必须是列表。")
    if not isinstance(generated.get("unaffected_reasoning", []), list):
        raise ShortDramaPlanError("unaffected_reasoning 必须是列表。")
    generated["source_episode_number"] = selected_number
    generated["human_review_required"] = True
    generated["analysis_kind"] = "downstream_continuity_impact"
    generated["analyzed_at"] = __import__("datetime").datetime.now().isoformat(timespec="seconds")
    return generated
