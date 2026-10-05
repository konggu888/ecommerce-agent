from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import json
import os
import urllib.request


FUNCTIONS = [
    "商品理解",
    "卖点提炼",
    "人群与痛点",
    "广告策略",
    "广告强度判断",
    "视频形式判断",
    "剧本",
    "分镜",
    "素材选择",
]


@dataclass
class ModelProfile:
    id: str
    name: str
    provider: str = "openai_compatible"
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-5.6"
    api_key: str = ""
    enabled: bool = True

    def public(self) -> dict[str, Any]:
        data = asdict(self)
        data["api_key"] = "***" if self.api_key else ""
        return data


class ModelRouter:
    """Local multi-model pool + per-function routing.

    The application owns routing/configuration; the LLM owns creative decisions.
    Providers can be OpenAI-compatible APIs, domestic gateways, or local servers.
    """

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.data = self._load()
        self._ensure_defaults()

    def _load(self) -> dict[str, Any]:
        if not self.config_path.exists():
            return {"default_model": "gpt-default", "models": [], "routes": {}}
        try:
            return json.loads(self.config_path.read_text(encoding="utf-8"))
        except Exception:
            return {"default_model": "gpt-default", "models": [], "routes": {}}

    def save(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _ensure_defaults(self) -> None:
        models = self.data.setdefault("models", [])
        if not any(m.get("id") == "gpt-default" for m in models):
            models.insert(0, asdict(ModelProfile(
                id="gpt-default",
                name="GPT（默认）",
                model=os.getenv("AD_STUDIO_GPT_MODEL", "gpt-5.6"),
            )))
        self.data.setdefault("default_model", "gpt-default")
        routes = self.data.setdefault("routes", {})
        for function in FUNCTIONS:
            routes.setdefault(function, self.data["default_model"])
        self.save()

    def profiles(self) -> list[ModelProfile]:
        return [ModelProfile(**m) for m in self.data.get("models", [])]

    def get(self, model_id: str) -> ModelProfile:
        for profile in self.profiles():
            if profile.id == model_id:
                return profile
        raise KeyError(f"未找到模型：{model_id}")

    def route(self, function: str) -> ModelProfile:
        model_id = self.data.get("routes", {}).get(function) or self.data["default_model"]
        return self.get(model_id)

    def set_route(self, function: str, model_id: str) -> None:
        self.get(model_id)
        self.data.setdefault("routes", {})[function] = model_id
        self.save()

    def add_or_update(self, profile: ModelProfile) -> None:
        models = self.data.setdefault("models", [])
        for i, item in enumerate(models):
            if item.get("id") == profile.id:
                models[i] = asdict(profile)
                self.save()
                return
        models.append(asdict(profile))
        self.save()

    def set_default(self, model_id: str) -> None:
        self.get(model_id)
        self.data["default_model"] = model_id
        self.save()

    def create_plan(self, product: dict[str, Any], constraints: dict[str, Any]) -> dict[str, Any]:
        """Run the creative pipeline through independently routed model stages."""
        from .creative_engine import build_stage_prompt

        analysis = self.complete_json(
            self.route("商品理解"),
            build_stage_prompt("analysis", product, constraints),
        )
        strategy_input = {"product_analysis": analysis, "constraints": constraints}
        strategy = self.complete_json(
            self.route("广告策略"),
            build_stage_prompt("strategy", strategy_input, constraints),
        )
        script_input = {
            "product_analysis": analysis,
            "strategy": strategy,
            "constraints": constraints,
        }
        script = self.complete_json(
            self.route("剧本"),
            build_stage_prompt("script", script_input, constraints),
        )
        merged = dict(analysis)
        merged.update(strategy)
        merged.update(script)
        return merged

    def complete_json(self, profile: ModelProfile, prompt: str) -> dict[str, Any]:
        if not profile.api_key:
            raise RuntimeError(
                f"模型「{profile.name}」尚未配置 API Key。请打开“模型设置”，"
                "或使用本地兼容 OpenAI API 的模型服务。"
            )
        if profile.provider != "openai_compatible":
            raise RuntimeError(f"暂不支持的模型提供方式：{profile.provider}")

        url = profile.base_url.rstrip("/") + "/chat/completions"
        payload = {
            "model": profile.model,
            "messages": [
                {"role": "system", "content": "你是电商广告创意总监，只输出合法 JSON。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "response_format": {"type": "json_object"},
        }
        request = urllib.request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {profile.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                body = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise RuntimeError(f"模型「{profile.name}」调用失败：{exc}") from exc

        try:
            content = body["choices"][0]["message"]["content"]
            return json.loads(content)
        except Exception as exc:
            raise RuntimeError(f"模型「{profile.name}」返回的不是有效 JSON") from exc

STAGE_SCHEMAS = {
    "analysis": {
        "product_summary": "string", "product_type": "string",
        "selling_points": ["string"], "target_audience": ["string"],
        "pain_points": ["string"], "usage_scenes": ["string"],
        "positioning": "string"
    },
    "strategy": {
        "ad_level": "纯种草|轻广告|标准广告|强转化|极强转化",
        "video_form": "string", "duration_seconds": "integer",
        "strategy": "string", "hook": "string"
    },
    "script": {
        "script": "string",
        "shots": [{
            "index": "integer", "objective": "string", "visual": "string",
            "dialogue": "string", "duration_seconds": "integer",
            "actor_requirements": ["string"], "scene_requirements": ["string"],
            "product_asset_requirements": ["string"], "on_screen_text": ["string"],
            "cta_role": "string", "generation_prompt": "string"
        }]
    }
}


def build_stage_prompt(stage: str, data: dict[str, Any], constraints: dict[str, Any]) -> str:
    instructions = {
        "analysis": "只负责商品理解、卖点、人群、痛点、使用场景和定位，不写剧本。",
        "strategy": "只负责广告策略、广告强度、视频形式、时长和开头钩子，不写完整分镜。",
        "script": "根据前两阶段结果，负责完整剧本和可执行分镜。优先复用已有资产。",
    }
    schema = STAGE_SCHEMAS[stage]
    return (
        CREATIVE_SYSTEM_PROMPT
        + f"\\n\\n当前阶段：{stage}\\n任务：{instructions[stage]}"
        + "\\n\\n输入：\\n" + json.dumps(data, ensure_ascii=False, indent=2)
        + "\\n\\n全局约束：\\n" + json.dumps(constraints, ensure_ascii=False, indent=2)
        + "\\n\\n本阶段只输出以下JSON结构：\\n"
        + json.dumps(schema, ensure_ascii=False, indent=2)
    )

