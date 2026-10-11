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
    "episodes": [{"episode_number": "integer", "title": "集名", "logline": "本集梗概", "plot_beats": ["本集节拍"], "ending_hook": "本集结尾/悬念", "full_script": "本集完整剧本", "continuity_state": {"opening_state": "本集开始时承接的剧情/人物状态", "character_state_changes": ["本集人物状态或关系的变化"], "unresolved_threads": ["本集结束后仍未解决的悬念/冲突"], "ending_state": "本集结束时可供后续承接的事实状态", "next_episode_requirements": ["下一集必须承接的事件/事实；最终集可为空列表"]}, "storyboard": ["本集分镜，字段与根级 storyboard 相同"]}],
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
        "relationship": "人物关系",
        "arc": "人物变化"
    }],
    "plot_beats": ["开场钩子", "矛盾升级", "转折/反转", "结局"],
    "conflict_and_reversal": "核心冲突与反转逻辑",
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
        "generation_prompt": "可执行的镜头生成提示"
    }],
    "product_truths": ["剧情必须遵守的商品事实"],
    "risk_notes": ["待确认信息、广告表达风险或制作风险"],
    "alternative_directions": [{
        "title": "备选方向",
        "mechanism": "不同的故事机制",
        "conversion_path": "商业转化路径"
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
        "2. 必须建立清晰的故事引擎：主角可观察的目标、具体阻力、失败代价、逐级升级的冲突、改变局势的转折、前后呼应的伏笔与兑现，以及情绪回报。输出 story_engine 对象，包含 protagonist_goal、opposing_force、stakes、escalation_steps（至少3项且因果递进）、turning_point、setup_and_payoff、emotional_payoff。\\n"
         "2.1 同时输出 hook_design，包含 opening_question、retention_devices（至少2项）、payoff。开场尽快制造具体问题/意外/选择；每个主要情节都必须改变人物处境或观众认知。\\n"
         "2.2 禁止用没有因果的巧合硬推剧情、只靠误会反复拖延、角色突然降智、结尾突然说教或硬塞购买口号。\\n"
         "2.3 商品植入/转化/商品短剧广告：商品只能在剧情逻辑允许时成为解决问题或引发选择的真实工具，不能凭空解决与其功能无关的冲突；商品卖点必须通过可拍摄的行为展示，不得只靠角色夸赞。\\n"
         "2.4 至少提供两个故事方向时，方向之间必须在冲突来源、人物选择或反转机制上有实质区别；不要仅更换场景、人物姓名或题材标签。\\n"
         "2. 设计完整的人物目标与关系、场景、冲突、节奏、转折和结尾；故事要有因果，不是卖点罗列。\n"
        "3. 商品是否出现必须服从所选创作目标：通用模式允许不出现；商品植入/转化模式应按目标呈现。任何模式都不得篡改商品外观、结构、核心功能、使用方式、规格、功效或其他事实。\n"
        "4. 未提供或无法验证的商品信息必须标为待确认，不得编造认证、销量、价格、效果或用户证言。\n"
        "5. 输出完整剧本和可执行分镜。每个分镜必须说明动作、台词、场景、人物、商品融入方式、素材需求和生成提示。\n"
        "6. 提供至少两个故事方向备选，机制应有实质差异，不只是换标题。\n"
        "7. 本次只做创作方案，不要调用素材生成或视频生成，不要假称已经生成成片。\n"
        "8. 只输出符合给定结构的合法JSON，不要输出Markdown。\n"
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

    if len(checked.get("alternative_directions", [])) < 2:
        add("warning", "ALT_DIRECTIONS", "备选故事方向少于两个；尚未满足多方向创作要求。")

    character_names = {
        str(item.get("name", "")).strip()
        for item in checked.get("characters", [])
        if isinstance(item, dict) and str(item.get("name", "")).strip()
    }
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
        "continuity_state 必须含 opening_state、character_state_changes（列表）、unresolved_threads（列表）、ending_state、next_episode_requirements（列表）。"
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
