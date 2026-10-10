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
    "episodes": [{"episode_number": "integer", "title": "集名", "logline": "本集梗概", "plot_beats": ["本集节拍"], "ending_hook": "本集结尾/悬念", "full_script": "本集完整剧本", "storyboard": ["本集分镜，字段与根级 storyboard 相同"]}],
    "drama_business_mode": "通用AI短剧/商品植入短剧/商品转化短剧",
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

        "11. 每个镜头必须带 episode_number；同一角色的外貌、身份、关键服装和关系在 series_bible 中保持稳定。\n"
        "12. 输出必须包含 drama_business_mode，且与 constraints.drama_business_mode 一致；人物、场景、商品素材需求要与所选模式匹配。\n\n输入与约束：\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
    )


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
    if raw.get("drama_business_mode") not in {"general", "product_placement", "product_conversion"}:
        raise ShortDramaPlanError("短剧商业模式无效，必须是通用AI短剧、商品植入短剧或商品转化短剧。")
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
    if validated.get("drama_business_mode") != requested_business_mode:
        raise ShortDramaPlanError(
            f"模型返回的短剧商业模式为 {validated.get('drama_business_mode')}，与所选模式 {requested_business_mode} 不一致；请重新生成，避免创作目标错位。"
        )
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
