"""Standalone AI short-drama director planning, separate from the existing ad workflow.

This module creates a story-first drama package. It does not overwrite the
existing ad creative plan or silently trigger paid asset/video generation.
"""
from __future__ import annotations

import json
from typing import Any


SHORT_DRAMA_SCHEMA = {
    "genre": "AI根据商品、人群、卖点和场景自主判断的短剧题材",
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
        "不是把常规广告脚本扩写成几个镜头。必须先理解商品与目标人群，再自主选择最合适的故事机制。\n"
        "要求：\n"
        "1. 题材必须根据商品事实、目标人群、使用场景和传播目标推导，不得机械套用固定题材清单。\n"
        "2. 设计完整的人物目标与关系、场景、冲突、节奏、转折和结尾；故事要有因果，不是卖点罗列。\n"
        "3. 商品应在剧情中自然出现，但不得篡改商品外观、结构、核心功能、使用方式、规格、功效或其他事实。\n"
        "4. 未提供或无法验证的商品信息必须标为待确认，不得编造认证、销量、价格、效果或用户证言。\n"
        "5. 输出完整剧本和可执行分镜。每个分镜必须说明动作、台词、场景、人物、商品融入方式、素材需求和生成提示。\n"
        "6. 提供至少两个故事方向备选，机制应有实质差异，不只是换标题。\n"
        "7. 本次只做创作方案，不要调用素材生成或视频生成，不要假称已经生成成片。\n"
        "8. 只输出符合给定结构的合法JSON，不要输出Markdown。\n\n输入与约束：\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
    )


def validate_short_drama(raw: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ShortDramaPlanError("AI短剧编导没有返回JSON对象。")
    required = [
        "genre", "genre_reasoning", "logline", "premise", "world",
        "characters", "plot_beats", "conflict_and_reversal", "ending",
        "full_script", "storyboard", "product_truths", "risk_notes",
        "alternative_directions",
    ]
    missing = [key for key in required if key not in raw]
    if missing:
        raise ShortDramaPlanError("短剧方案缺少字段：" + "、".join(missing))
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
    return validate_short_drama(result)


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
        rows.append({
            "index": int(shot.get("index", index)),
            "title": title,
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
            "product_integration": integration,
        })
    return rows
