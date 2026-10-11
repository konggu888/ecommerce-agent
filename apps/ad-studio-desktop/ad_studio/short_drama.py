"""Standalone AI short-drama director planning and deterministic pre-production audit, separate from the existing ad workflow.

This module creates a story-first drama package. It does not overwrite the
existing ad creative plan or silently trigger paid asset/video generation.
"""
from __future__ import annotations

import json
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
        "0.3 product_short_drama_ad 是独立的AI短剧形式商品广告目标，不能与普通商品植入/商品转化混同。先分析商品类型、目标人群、已确认卖点、使用场景和未知信息，再自主决定题材/时代（例如古代或现代）并说明理由，让商品自然成为剧情机制的一部分。\\n"
        "0.4 product_short_drama_ad 必须输出 product_analysis、genre_decision、product_fact_lock。将事实分为已确认与未知/未核实；禁止编造参数、认证、效果、价格、销量、材料或功能。未知信息只能标待确认，不得当作事实使用。\\n"
        "0.5 每个 product_short_drama_ad 分镜都必须有 product_fidelity_constraints，明确本镜商品外观、颜色/款式、结构、关键部件、核心功能和正确使用方式哪些必须保持不变；需要时指定参考商品图片/素材。不得为了古代/奇幻剧情把真实商品改成不同款式、改变结构或赋予不存在的功能。\\n"
        "0.6 每个商品广告分镜增加 visual_verification 字段，初始值必须明确为 not_checked；结构/文字复核不能冒充生成画面视觉核验。生成画面后需由后续视觉检查或人工确认，发现问题只重生成问题镜头。\\n"
        "1. 题材必须根据创作目标、商品事实（如适用）、目标人群、使用场景和传播目标推导，不得机械套用固定题材清单。\n"
        "2. 设计完整的人物目标与关系、场景、冲突、节奏、转折和结尾；故事要有因果，不是卖点罗列。\n"
        "3. 商品是否出现必须服从所选创作目标：通用模式允许不出现；商品植入/转化模式应按目标呈现。任何模式都不得篡改商品外观、结构、核心功能、使用方式、规格、功效或其他事实。\n"
        "4. 未提供或无法验证的商品信息必须标为待确认，不得编造认证、销量、价格、效果或用户证言。\n"
        "5. 输出完整剧本和可执行分镜。每个分镜必须说明动作、台词、场景、人物、商品融入方式、素材需求和生成提示。\n"
        "6. 提供至少两个故事方向备选，机制应有实质差异，不只是换标题。\n"
        "7. 本次只做创作方案，不要调用素材生成或视频生成，不要假称已经生成成片。\n"
        "8. 只输出符合给定结构的合法JSON，不要输出Markdown。\n"
        "9. 如果 constraints.short_drama_mode 为 continuous_series 或 anthology_series，必须输出指定数量的 episodes；每集有独立剧本、分镜和结尾钩子。根级 storyboard 必须按集顺序汇总全部分镜，每个镜头带 episode_number；不要把多集缩成一集。\n"
        "10. continuous_series 必须跨集承接人物状态、因果和悬念；anthology_series 共用人物/世界观但每集有相对独立的故事。单集模式 episodes 可以只含一集。\n"

        "10.1 每集必须输出 continuity_state：opening_state（开集承接状态）、character_state_changes（人物/关系变化列表）、unresolved_threads（集末未解决线索列表）、ending_state（集末确定状态）、next_episode_requirements（下一集必须承接的要求；最终集可为空列表）。连续剧第N集 opening_state 必须承接第N-1集 ending_state 和 next_episode_requirements，不能重置人物记忆或忽略未解决悬念。\\n"
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
            raw["full_script"] = "\\n\\n".join(
                f"第{e.get('episode_number', i)}集：{e.get('title', '')}\\n{e.get('full_script', '')}"
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
    shot = shots[shot_number - 1]
    shot["visual_verification"] = status
    shot["visual_verification_evidence"] = str(evidence_path).strip()
    shot["visual_verification_method"] = "manual"
    shot["visual_verification_note"] = str(reviewer_note).strip()
    return updated


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
            if status != "passed":
                add("warning", "PRODUCT_VISUAL_NOT_VERIFIED", f"第{number}镜商品画面视觉核验状态为“{status}”；文字规则检查不能证明生成画面真实还原商品。")
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
    script_text = "\\n".join(content_parts)
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
