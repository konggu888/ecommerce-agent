from __future__ import annotations

from dataclasses import dataclass, asdict, field
import json
from typing import Any, Protocol


@dataclass
class CreativeShot:
    index: int
    objective: str = ""
    visual: str = ""
    dialogue: str = ""
    duration_seconds: int = 3
    actor_requirements: list[str] = field(default_factory=list)
    scene_requirements: list[str] = field(default_factory=list)
    product_asset_requirements: list[str] = field(default_factory=list)
    asset_resolution: dict = field(default_factory=dict)
    on_screen_text: list[str] = field(default_factory=list)
    cta_role: str = ""
    generation_prompt: str = ""
    composition: str = "主体清晰居中"
    focus_x: float = 0.5
    focus_y: float = 0.5
    subtitle_position: str = "底部安全区"
    subtitle_style: str = "白字黑边"
    pacing: str = "标准"
    speed: float = 1.0
    bgm_intensity: str = "低"
    bgm_volume: float = 0.16
    transition: str = "硬切"


@dataclass
class CreativePlan:
    product_summary: str
    product_type: str
    selling_points: list[str]
    target_audience: list[str]
    pain_points: list[str]
    usage_scenes: list[str]
    positioning: str
    ad_level: str
    video_form: str
    duration_seconds: int
    strategy: str
    hook: str
    script: str
    shots: list[CreativeShot]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CreativeLLM(Protocol):
    def create_plan(self, product: dict[str, Any], constraints: dict[str, Any]) -> dict[str, Any]:
        ...


class CreativePlanError(ValueError):
    pass


CREATIVE_SYSTEM_PROMPT = """你是电商广告创意总导演。
你的任务不是机械改写商品资料，而是根据商品资料、平台、广告强度和用户约束，
独立判断商品卖点、目标人群、痛点、竞争差异、广告策略、视频形式、剧本和分镜。

重要规则：
1. 商品资料可能不完整，不要编造商品不存在的规格、功效、认证、销量或价格。
2. 对无法确认的事实，用“待确认”或降低表述强度。
3. 广告表达必须避免明显违反中国广告法的绝对化、虚假、无法证明的承诺。
4. 视频形式、广告强度、镜头数量都由你根据商品和目标决定，而不是由固定模板决定。
5. 当 task_type=广告投放视频且存在 creative_variant_axis 时，必须围绕该测试轴做真实创意差异；禁止仅替换几个同义词。
5. 每个镜头必须能落地：说明画面、人物、场景、商品素材、台词/字幕和生成提示。
6. 优先复用已有演员、场景、商品素材；只有缺少合适资产时才建议生成新资产。
7. 输出必须是严格 JSON，不要输出 Markdown。"""

JSON_SCHEMA = {
    "product_summary": "string",
    "product_type": "string",
    "selling_points": ["string"],
    "target_audience": ["string"],
    "pain_points": ["string"],
    "usage_scenes": ["string"],
    "positioning": "string",
    "ad_level": "纯种草|轻广告|标准广告|强转化|极强转化",
    "video_form": "string",
    "duration_seconds": "integer",
    "strategy": "string",
    "hook": "string",
    "script": "string",
    "shots": [{
        "index": "integer",
        "objective": "string",
        "visual": "string",
        "dialogue": "string",
        "duration_seconds": "integer",
        "actor_requirements": ["string"],
        "scene_requirements": ["string"],
        "product_asset_requirements": ["string"],
        "on_screen_text": ["string"],
        "cta_role": "string",
        "generation_prompt": "string",
        "composition": "string",
        "focus_x": "number 0..1",
        "focus_y": "number 0..1",
        "subtitle_position": "顶部安全区|中部安全区|底部安全区|不显示",
        "subtitle_style": "白字黑边|黄字黑边|简洁白字",
        "pacing": "慢|标准|快|极快",
        "speed": "number 0.75..1.5",
        "bgm_intensity": "无|低|中|高",
        "bgm_volume": "number 0..0.35",
        "transition": "硬切|淡入|淡出"
    }]
}


def build_creative_prompt(product: dict[str, Any], constraints: dict[str, Any]) -> str:
    payload = {
        "product_material": product,
        "constraints": constraints,
        "required_output_schema": JSON_SCHEMA,
    }
    return CREATIVE_SYSTEM_PROMPT + "\n\n输入与约束：\n" + json.dumps(
        payload, ensure_ascii=False, indent=2
    )


def _text_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(x).strip() for x in value if str(x).strip()]


def validate_plan(raw: dict[str, Any]) -> CreativePlan:
    if not isinstance(raw, dict):
        raise CreativePlanError("LLM没有返回JSON对象")

    required = [
        "product_summary", "product_type", "selling_points",
        "target_audience", "pain_points", "usage_scenes",
        "positioning", "ad_level", "video_form", "duration_seconds",
        "strategy", "hook", "script", "shots",
    ]
    missing = [key for key in required if key not in raw]
    if missing:
        raise CreativePlanError("创意计划缺少字段：" + "、".join(missing))

    shots = raw["shots"]
    if not isinstance(shots, list) or not shots:
        raise CreativePlanError("创意计划没有有效分镜")

    creative_shots = []
    for i, shot in enumerate(shots, 1):
        if not isinstance(shot, dict):
            raise CreativePlanError(f"第{i}个分镜不是对象")
        creative_shots.append(
            CreativeShot(
                index=int(shot.get("index", i)),
                objective=str(shot.get("objective", "")),
                visual=str(shot.get("visual", "")),
                dialogue=str(shot.get("dialogue", "")),
                duration_seconds=max(1, int(shot.get("duration_seconds", 3))),
                actor_requirements=_text_list(shot.get("actor_requirements")),
                scene_requirements=_text_list(shot.get("scene_requirements")),
                product_asset_requirements=_text_list(shot.get("product_asset_requirements")),
                on_screen_text=_text_list(shot.get("on_screen_text")),
                cta_role=str(shot.get("cta_role", "")),
                generation_prompt=str(shot.get("generation_prompt", "")),
                composition=str(shot.get("composition", "主体清晰居中")),
                focus_x=min(1.0, max(0.0, float(shot.get("focus_x", 0.5)))),
                focus_y=min(1.0, max(0.0, float(shot.get("focus_y", 0.5)))),
                subtitle_position=str(shot.get("subtitle_position", "底部安全区")),
                subtitle_style=str(shot.get("subtitle_style", "白字黑边")),
                pacing=str(shot.get("pacing", "标准")),
                speed=min(1.5, max(0.75, float(shot.get("speed", 1.0)))),
                bgm_intensity=str(shot.get("bgm_intensity", "低")),
                bgm_volume=min(0.35, max(0.0, float(shot.get("bgm_volume", 0.16)))),
                transition=str(shot.get("transition", "硬切")),
            )
        )

    return CreativePlan(
        product_summary=str(raw["product_summary"]),
        product_type=str(raw["product_type"]),
        selling_points=_text_list(raw["selling_points"]),
        target_audience=_text_list(raw["target_audience"]),
        pain_points=_text_list(raw["pain_points"]),
        usage_scenes=_text_list(raw["usage_scenes"]),
        positioning=str(raw["positioning"]),
        ad_level=str(raw["ad_level"]),
        video_form=str(raw["video_form"]),
        duration_seconds=max(1, int(raw["duration_seconds"])),
        strategy=str(raw["strategy"]),
        hook=str(raw["hook"]),
        script=str(raw["script"]),
        shots=creative_shots,
    )


TASK_TYPE_POLICIES = {
    "电商短视频": {"min_seconds": 20, "max_seconds": 60, "required": ["hook"], "sequence": ["hook", "pain_point", "selling_points", "proof", "cta"]},
    "商品主图视频": {"min_seconds": 8, "max_seconds": 30, "required": ["product"], "sequence": ["product", "detail", "function", "usage", "cta"]},
    "广告投放视频": {"min_seconds": 15, "max_seconds": 45, "required": ["hook", "cta"], "sequence": ["hook", "core_selling_point", "proof", "objection", "cta"]},
}


def apply_task_type_policy(raw: dict[str, Any], constraints: dict[str, Any] | None = None) -> dict[str, Any]:
    """把三种任务的成片结构变成确定性可检查规则。"""
    constraints = constraints or {}
    task_type = str(constraints.get("task_type", "电商短视频")).strip() or "电商短视频"
    policy = TASK_TYPE_POLICIES.get(task_type)
    if not policy:
        raise CreativePlanError(f"不支持的任务类型：{task_type}")
    raw["task_policy"] = policy
    duration = max(1, int(raw.get("duration_seconds", 1)))
    raw["duration_seconds"] = min(policy["max_seconds"], max(policy["min_seconds"], duration))
    shots = raw.get("shots", [])
    if task_type == "商品主图视频" and isinstance(shots, list) and len(shots) > 8:
        raw["shots"] = shots[:8]
    raw["task_type"] = task_type
    return raw


def validate_task_type_plan(raw: dict[str, Any], constraints: dict[str, Any] | None = None) -> dict[str, Any]:
    """确定性检查本次任务是否真正反映在创意方案结构中。"""
    constraints = constraints or {}
    task_type = str(constraints.get("task_type", "电商短视频")).strip() or "电商短视频"
    if task_type not in {"电商短视频", "商品主图视频", "广告投放视频"}:
        raise CreativePlanError(f"不支持的任务类型：{task_type}")
    shots = raw.get("shots") if isinstance(raw, dict) else None
    if not isinstance(shots, list) or not shots:
        raise CreativePlanError("任务类型检查失败：没有分镜")
    texts = " ".join(str(raw.get(k, "")) for k in ("strategy", "hook", "script")) + " " + " ".join(str(s.get(k, "")) for s in shots if isinstance(s, dict) for k in ("objective", "visual", "dialogue", "on_screen_text", "cta_role"))
    if task_type == "广告投放视频" and not any(x in texts for x in ("CTA", "行动", "购买", "下单", "立即", "点击", "咨询", "转化")):
        raise CreativePlanError("广告投放视频缺少明确转化/CTA结构，不能进入成片")
    if task_type == "商品主图视频" and sum(1 for x in ("商品", "产品", "细节", "展示", "特写", "功能", "材质", "接口", "外观", "参数", "使用") if x in texts) < 2:
        raise CreativePlanError("商品主图视频缺少商品本体/细节/功能展示结构，不能进入成片")
    if task_type == "电商短视频" and not str(raw.get("hook", "")).strip():
        raise CreativePlanError("电商短视频缺少开场钩子，不能进入成片")
    raw = apply_task_type_policy(raw, constraints)
    raw["task_validation"] = {"ok": True, "task_type": task_type, "method": "确定性任务结构检查"}
    return raw


class CreativeEngine:
    def __init__(self, llm: CreativeLLM):
        self.llm = llm

    def plan(self, product: dict[str, Any], constraints: dict[str, Any] | None = None) -> CreativePlan:
        raw = self.llm.create_plan(product, constraints or {})
        return validate_plan(validate_task_type_plan(raw, constraints))
