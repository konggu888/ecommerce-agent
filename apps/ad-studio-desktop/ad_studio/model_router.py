from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import json
import os
import base64
import urllib.request
import time

from .usage_ledger import UsageLedger
from .creative_engine import CREATIVE_SYSTEM_PROMPT


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
    "素材剪辑导演",
    "口播转写",
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
    input_price_rmb_per_1k: float = 0.0
    output_price_rmb_per_1k: float = 0.0
    vision_enabled: bool = False
    transcription_enabled: bool = False

    def public(self) -> dict[str, Any]:
        data = asdict(self)
        data["api_key"] = "***" if self.api_key else ""
        return data


class ModelRouter:
    """Local multi-model pool + per-function routing.

    The application owns routing/configuration; the LLM owns creative decisions.
    Every creative function is routed independently, so changing one dropdown
    changes the actual model call for that stage.
    """

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.data = self._load()
        self._ensure_defaults()
        self.ledger = UsageLedger(self.config_path.parent / "usage-ledger.json")
        self._hardware = None

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
                vision_enabled=True,
            )))
        self.data.setdefault("default_model", "gpt-default")
        for m in models:
            if m.get("id") == "gpt-default" and "vision_enabled" not in m:
                m["vision_enabled"] = True
        routes = self.data.setdefault("routes", {})
        for function in FUNCTIONS:
            routes.setdefault(function, self.data["default_model"])
        self.save()

    def profiles(self) -> list[ModelProfile]:
        fields = {f.name for f in __import__("dataclasses").fields(ModelProfile)}
        return [ModelProfile(**{k: v for k, v in m.items() if k in fields})
                for m in self.data.get("models", [])]

    def get(self, model_id: str) -> ModelProfile:
        for profile in self.profiles():
            if profile.id == model_id:
                return profile
        raise KeyError(f"未找到模型：{model_id}")

    def route(self, function: str) -> ModelProfile:
        model_id = self.data.get("routes", {}).get(function) or self.data["default_model"]
        return self.get(model_id)

    def _usable(self, profile: ModelProfile) -> bool:
        return profile.enabled and (profile.provider == "local_openai" or bool(profile.api_key))

    def _first_local_model(self) -> ModelProfile | None:
        for p in self.profiles():
            if p.enabled and p.provider == "local_openai":
                return p
        return None

    def resolve_route(self, function: str) -> ModelProfile:
        """按硬件能力与模型池自动决定该功能实际调用的模型。

        决策优先级：
        1. 显式路由的模型可调用（本地 OpenAI 兼容服务或已配 API Key）→ 用它；
        2. 硬件要求云端优先且云端模型有凭据 → 用云端模型；
        3. 本地模型池有可用的本地模型 → 用本地模型（电脑有能力就用）；
        4. 否则回退显式路由，调用时给出明确配置错误。
        """
        profile = self.route(function)
        if self._usable(profile):
            return profile
        if self._hardware is None:
            try:
                from .hardware import detect_hardware
                self._hardware = detect_hardware()
            except Exception:
                self._hardware = None
        mode = getattr(self._hardware, "execution_mode", "") if self._hardware else ""
        if mode == "cloud_first":
            for p in self.profiles():
                if p.enabled and p.provider != "local_openai" and p.api_key:
                    return p
        local = self._first_local_model()
        if local:
            return local
        return profile

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
        """Run all nine creative functions through their independently routed models."""
        context: dict[str, Any] = {"product": product, "constraints": constraints}

        def run(function: str, stage: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
            data = dict(context)
            if extra:
                data.update(extra)
            prompt = build_stage_prompt(stage, data, constraints)
            try:
                result = self.complete_json(
                    self.resolve_route(function),
                    prompt,
                    function=function,
                )
            except TypeError as exc:
                # Keep older test doubles/backward-compatible adapters working;
                # the real router accepts the function label and records usage.
                if "unexpected keyword argument 'function'" not in str(exc):
                    raise
                result = self.complete_json(self.resolve_route(function), prompt)
            context[stage] = result
            return result

        understanding = run("商品理解", "product_understanding")
        selling = run("卖点提炼", "selling_points", {"product_understanding": understanding})
        audience = run("人群与痛点", "audience_pain", {
            "product_understanding": understanding,
            "selling_points": selling,
        })
        strategy = run("广告策略", "ad_strategy", {
            "product_understanding": understanding,
            "selling_points": selling,
            "audience_pain": audience,
        })
        intensity = run("广告强度判断", "ad_intensity", {
            "product_understanding": understanding,
            "selling_points": selling,
            "audience_pain": audience,
            "ad_strategy": strategy,
        })
        form = run("视频形式判断", "video_form", {
            "product_understanding": understanding,
            "audience_pain": audience,
            "ad_strategy": strategy,
            "ad_intensity": intensity,
        })
        script = run("剧本", "script", {
            "product_understanding": understanding,
            "selling_points": selling,
            "audience_pain": audience,
            "ad_strategy": strategy,
            "ad_intensity": intensity,
            "video_form": form,
        })
        storyboard = run("分镜", "storyboard", {
            "product_understanding": understanding,
            "selling_points": selling,
            "audience_pain": audience,
            "ad_strategy": strategy,
            "ad_intensity": intensity,
            "video_form": form,
            "script": script,
        })
        assets = run("素材选择", "asset_selection", {
            "product_understanding": understanding,
            "selling_points": selling,
            "audience_pain": audience,
            "ad_strategy": strategy,
            "ad_intensity": intensity,
            "video_form": form,
            "script": script,
            "storyboard": storyboard,
        })

        merged: dict[str, Any] = {}
        for result in (
            understanding, selling, audience, strategy, intensity,
            form, script, storyboard, assets,
        ):
            merged.update(result)

        # Keep downstream CreativeEngine validation compatible while exposing
        # the full nine-stage result for persistence and later asset matching.
        merged["creative_stages"] = context
        if "shots" not in merged and storyboard.get("shots"):
            merged["shots"] = storyboard["shots"]
        if "script" not in merged:
            merged["script"] = script.get("script", "")
        if "ad_level" not in merged:
            merged["ad_level"] = intensity.get("ad_level", "标准广告")
        if "video_form" not in merged:
            merged["video_form"] = form.get("video_form", "")
        if "duration_seconds" not in merged:
            merged["duration_seconds"] = form.get("duration_seconds", 30)
        return merged

    def create_plans(self, product: dict[str, Any], constraints: dict[str, Any], count: int = 3) -> list[dict[str, Any]]:
        """Create several deliberately different creative plans for the same product.

        Each variant still runs through the same nine independently routed creative
        stages. The LLM is told to avoid repeating the previous variant's strategy,
        so this is not a fixed industry template and works across product categories.
        """
        count = max(1, min(5, int(count)))
        plans = []
        previous = []
        diversity_prompts = [
            "优先寻找最适合该商品的成熟电商广告打法，可以是对标翻新、卖点拆解、强场景展示等，但不要机械套模板。",
            "必须与前一方案明显不同。优先考虑真实人物、生活剧情、UGC、体验、对话或场景冲突等真人感打法；如果商品不适合，则自行选择另一种完全不同的形式。",
            "必须与前面方案明显不同。优先寻找更强记忆点、更原生平台感、更有节奏或创意表达的打法，例如音乐、说唱、反差、短剧、视觉实验等；如果商品不适合，则自行选择最有传播潜力的替代形式。",
            "必须与前面所有方案明显不同，寻找尚未使用的广告机制，不得只是换几句文案。",
            "必须与前面所有方案明显不同，寻找尚未使用的广告机制，不得只是换几句文案。",
        ]
        for i in range(count):
            variant_constraints = dict(constraints)
            variant_constraints["creative_variant_index"] = i + 1
            variant_constraints["creative_variant_count"] = count
            variant_constraints["creative_variant_instruction"] = diversity_prompts[i]
            variant_constraints["previous_variant_summaries"] = previous[-4:]
            raw = self.create_plan(product, variant_constraints)
            raw["_variant_index"] = i + 1
            raw["_variant_label"] = f"方案{i + 1}｜{raw.get('video_form', 'AI创意方案')}"
            previous.append({
                "index": i + 1,
                "video_form": raw.get("video_form", ""),
                "strategy": raw.get("strategy", ""),
                "hook": raw.get("hook", ""),
            })
            plans.append(raw)
        return plans

    def recent_usage(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.ledger.recent(limit)

    def transcribe_footage_audio(
        self, audio_path: Path, profile: ModelProfile | None = None
    ) -> dict[str, Any]:
        """调用独立的口播转写模型，并保留可用时间戳。"""
        from .transcription import transcribe_openai_compatible
        profile = profile or self.resolve_route("口播转写")
        if not profile.transcription_enabled:
            raise RuntimeError(f"当前“口播转写”模型「{profile.name}」未启用语音转写。")
        if not profile.api_key and profile.provider != "local_openai":
            raise RuntimeError(f"口播转写模型「{profile.name}」没有可用凭据。")
        endpoint = profile.base_url.rstrip("/") + "/audio/transcriptions"
        result = transcribe_openai_compatible(audio_path, endpoint, profile.api_key, profile.model)
        return {"text": result.text, "segments": [
            {"start": x.start, "end": x.end, "text": x.text} for x in result.segments
        ]}

    def analyze_footage(
        self,
        product: dict[str, Any],
        creative_plan: dict[str, Any],
        footage_manifest: list[dict[str, Any]],
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """让视觉模型真正观察实拍关键帧，再输出逐素材分析。"""
        profile = self.resolve_route("素材剪辑导演")
        if not profile.vision_enabled:
            raise RuntimeError(
                f"当前“素材剪辑导演”模型「{profile.name}」未启用视觉分析。"
                "请在模型设置中勾选“支持图片/视频帧分析”。"
            )
        public_manifest = [{
            "name": x["name"], "duration": x["duration"],
            "width": x["width"], "height": x["height"], "fps": x["fps"],
            "keyframes": [{"label": f["label"], "time": f["time"]}
                          for f in x.get("frames", [])],
        } for x in footage_manifest]
        images = [f["path"] for x in footage_manifest for f in x.get("frames", [])]
        payload = {
            "product": product,
            "creative_plan": creative_plan,
            "footage": public_manifest,
            "constraints": constraints or {},
            "required_output": {
                "clips": [{
                    "source": "素材文件名",
                    "score": "0..100",
                    "usable": "boolean",
                    "reason": "string",
                    "best_ranges": [{"start": "number", "duration": "number", "reason": "string"}],
                    "visual_tags": ["product_visible|person|scene|detail|demo|talking|blocked|blur|shake|duplicate|other"],
                    "selling_points": ["string"],
                    "speech_quality": "none|clear|filler|unclear"
                }],
                "global_summary": "string",
                "recommended_duration_seconds": "integer"
            }
        }
        prompt = (
            "你是实拍电商视频分析师。必须观察用户拍摄素材的关键帧，"
            "把画面事实与商品资料、广告方案对应起来，不得只根据文件名猜测。"
            "识别商品清晰度、人物、场景、演示、遮挡、抖动、重复、糊片、"
            "可用片段、卖点对应关系和口播质量；没看到的内容标记 unknown。"
            "只返回 JSON。\n\n" + json.dumps(payload, ensure_ascii=False, indent=2)
        )
        return self.complete_json(
            profile, prompt, function="实拍素材视觉分析", image_paths=images
        )

    def plan_footage(
        self,
        product: dict[str, Any],
        creative_plan: dict[str, Any],
        footage_clips: list[dict[str, Any]],
        constraints: dict[str, Any] | None = None,
        footage_analysis: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """素材剪辑导演：基于产品理解、创意方案与用户拍摄素材，规划剪辑方案。

        输入是产品资料、AI 创意方案（卖点/分镜/文案）和素材清单（只有文件名、
        时长、分辨率、帧率，不含本地绝对路径）。输出是 footage_plan 列表，
        每个镜头引用素材文件名并给出起始秒/时长/文案/构图等，供本地FFmpeg裁剪。
        规则：只能使用给定素材，不得编造素材文件或引用清单外的内容。
        """
        payload = {
            "product": product,
            "creative_plan": {
                "product_summary": creative_plan.get("product_summary", ""),
                "product_type": creative_plan.get("product_type", ""),
                "selling_points": creative_plan.get("selling_points", []),
                "target_audience": creative_plan.get("target_audience", []),
                "pain_points": creative_plan.get("pain_points", []),
                "strategy": creative_plan.get("strategy", ""),
                "hook": creative_plan.get("hook", ""),
                "script": creative_plan.get("script", ""),
                "shots": creative_plan.get("shots", []),
            },
            "footage_clips": footage_clips,
            "footage_analysis": footage_analysis or {},
            "footage_transcripts": creative_plan.get("footage_transcripts", []),
            "constraints": constraints or {},
            "required_output_schema": STAGE_SCHEMAS["footage_director"],
        }
        system = (
            "你是电商广告剪辑导演。用户已经把拍摄好的视频素材放进指定文件夹，"
            "你需要基于产品分析与创意方案，从这些素材中挑选片段组成一支广告成片。\n"
            "重要规则：\n"
            "1. 只能使用 footage_clips 清单中列出的素材文件，source 字段必须精确匹配文件名；"
            "禁止编造素材、禁止引用清单外的文件。\n"
            "2. start 是素材内起始秒，duration 是本镜头时长；start + duration 不能超过该素材总时长。\n"
            "3. 同一段素材可以按不同时间段使用多次，但要保证每个镜头内容合理、节奏顺畅。\n"
            "4. 每个镜头给出画面说明、口播/文案、字幕位置、构图、节奏、转场，供本地执行。\n"
            "5. 广告表达避免违反广告法的绝对化、虚假、无法证明的承诺。\n"
            "6. 输出必须是严格 JSON，不要输出 Markdown。"
        )
        prompt = (
            system
            + "\n\n输入：\n" + json.dumps(payload, ensure_ascii=False, indent=2)
        )
        result = self.complete_json(
            self.resolve_route("素材剪辑导演"),
            prompt,
            function="素材剪辑导演",
        )
        plan = result.get("footage_plan")
        if not isinstance(plan, list) or not plan:
            raise RuntimeError("素材剪辑导演没有返回有效的 footage_plan")
        return plan

    def usage_summary(self) -> dict[str, Any]:
        return self.ledger.summary()

    def test_connection(self, model_id: str) -> tuple[bool, str]:
        profile = self.get(model_id)
        if not profile.enabled:
            return False, "模型已禁用"
        if profile.provider == "openai_compatible" and not profile.api_key:
            return False, "缺少 API Key"
        if profile.provider not in {"openai_compatible", "local_openai"}:
            return False, f"不支持的提供方式：{profile.provider}"
        try:
            result = self.complete_json(profile, '{"ping":"请只返回 {\"ok\":true}"}', function="连接测试")
            return bool(result.get("ok", True)), "连接成功"
        except Exception as exc:
            return False, str(exc)

    def complete_json(self, profile: ModelProfile, prompt: str, function: str = "未标记功能", image_paths: list[str] | None = None) -> dict[str, Any]:
        if not profile.enabled:
            raise RuntimeError(f"模型「{profile.name}」已禁用。")
        if profile.provider not in {"openai_compatible", "local_openai"}:
            raise RuntimeError(f"暂不支持的模型提供方式：{profile.provider}")

        # Local OpenAI-compatible servers (Ollama/vLLM/LM Studio/etc.) normally
        # do not require a cloud API key. Cloud OpenAI-compatible providers do.
        if profile.provider == "openai_compatible" and not profile.api_key:
            raise RuntimeError(
                f"模型「{profile.name}」尚未配置 API Key。请打开“模型设置”，"
                "或改用本地 OpenAI 兼容模型服务。"
            )

        url = profile.base_url.rstrip("/") + "/chat/completions"
        user_content: Any = prompt
        if image_paths:
            if not profile.vision_enabled:
                raise RuntimeError(f"模型「{profile.name}」未启用视觉输入，不能分析视频关键帧。")
            parts: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
            for image_path in image_paths[:32]:
                p = Path(image_path)
                if not p.exists():
                    continue
                raw = base64.b64encode(p.read_bytes()).decode("ascii")
                parts.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{raw}", "detail": "low"},
                })
            user_content = parts
        payload = {
            "model": profile.model,
            "messages": [
                {"role": "system", "content": "你是电商广告创意总监，只输出合法 JSON。"},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.7,
            "response_format": {"type": "json_object"},
        }
        headers = {"Content-Type": "application/json"}
        if profile.api_key:
            headers["Authorization"] = f"Bearer {profile.api_key}"
        request = urllib.request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                body = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            self.ledger.record(
                function=function, model_id=profile.id, model_name=profile.name,
                provider=profile.provider, model=profile.model, status="failed",
                duration_ms=int((time.perf_counter() - started) * 1000), error=str(exc),
                project_id=self.current_project_id, category="model",
            )
            raise RuntimeError(f"模型「{profile.name}」调用失败：{exc}") from exc

        usage = body.get("usage") or {}
        prompt_tokens = int(usage.get("prompt_tokens", usage.get("input_tokens", 0)) or 0)
        completion_tokens = int(usage.get("completion_tokens", usage.get("output_tokens", 0)) or 0)
        total_tokens = int(usage.get("total_tokens", prompt_tokens + completion_tokens) or 0)
        estimated_cost = (
            prompt_tokens / 1000 * float(profile.input_price_rmb_per_1k)
            + completion_tokens / 1000 * float(profile.output_price_rmb_per_1k)
        )
        try:
            content = body["choices"][0]["message"]["content"]
            result = json.loads(content)
        except Exception as exc:
            self.ledger.record(
                function=function, model_id=profile.id, model_name=profile.name,
                provider=profile.provider, model=profile.model, status="failed",
                prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
                total_tokens=total_tokens, estimated_cost_rmb=estimated_cost,
                duration_ms=int((time.perf_counter() - started) * 1000), error=str(exc),
                project_id=self.current_project_id, category="model",
            )
            raise RuntimeError(f"模型「{profile.name}」返回的不是有效 JSON") from exc

        self.ledger.record(
            function=function, model_id=profile.id, model_name=profile.name,
            provider=profile.provider, model=profile.model, status="success",
            prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
            total_tokens=total_tokens, estimated_cost_rmb=estimated_cost,
            duration_ms=int((time.perf_counter() - started) * 1000),
            project_id=self.current_project_id, category="model",
        )
        return result


STAGE_SCHEMAS = {
    "product_understanding": {
        "product_summary": "string", "product_type": "string",
        "positioning": "string", "usage_scenes": ["string"]
    },
    "selling_points": {"selling_points": ["string"]},
    "audience_pain": {
        "target_audience": ["string"], "pain_points": ["string"]
    },
    "ad_strategy": {"strategy": "string", "hook": "string"},
    "ad_intensity": {
        "ad_level": "纯种草|轻广告|标准广告|强转化|极强转化"
    },
    "video_form": {"video_form": "string", "duration_seconds": "integer"},
    "script": {"script": "string"},
    "storyboard": {
        "shots": [{
            "index": "integer", "objective": "string", "visual": "string",
            "dialogue": "string", "duration_seconds": "integer",
            "actor_requirements": ["string"], "scene_requirements": ["string"],
            "product_asset_requirements": ["string"], "on_screen_text": ["string"],
            "cta_role": "string", "generation_prompt": "string"
        }]
    },
    "asset_selection": {
        "asset_selection": [{
            "shot_index": "integer", "asset_type": "actor|scene|product|other",
            "requirements": ["string"], "preferred_asset_ids": ["string"]
        }]
    },
    "footage_director": {
        "footage_plan": [{
            "index": "integer", "source": "string 素材文件名（必须是清单里的文件名）",
            "start": "number 素材内起始秒", "duration": "number 镜头时长秒",
            "objective": "string", "visual": "string", "script": "string",
            "composition": "string", "focus_x": "number 0..1", "focus_y": "number 0..1",
            "subtitle_position": "string", "subtitle_style": "string",
            "pacing": "string", "speed": "number 0.75..1.5",
            "bgm_intensity": "string", "bgm_volume": "number 0..0.35",
            "transition": "string"
        }]
    },
}


def build_stage_prompt(stage: str, data: dict[str, Any], constraints: dict[str, Any]) -> str:
    instructions = {
        "product_understanding": "只负责理解商品资料、商品类型、定位和使用场景；不得发明资料中没有的规格、功效或价格。",
        "selling_points": "只提炼真实可依据的核心卖点，并按广告价值排序；不确定的信息降低表述强度或标记待确认。",
        "audience_pain": "判断最值得触达的人群及其真实痛点，不得凭空制造医学、效果或用户数据结论。",
        "ad_strategy": "制定广告策略和开头钩子，明确为什么这样卖、先讲什么、如何建立转化路径。",
        "ad_intensity": "根据商品、受众、平台、策略和约束判断广告强度，只选择五档之一。",
        "video_form": "根据商品、受众、策略和广告强度决定最合适的视频形式及最终合理时长，不受固定模板限制。",
        "script": "根据前置阶段结果写完整可拍/可生成的广告剧本；不要重复做商品分析。",
        "storyboard": "把剧本拆成真正可执行的镜头；每镜头必须说明目标、画面、对白、时长、演员/场景/商品素材要求和生成提示。",
        "asset_selection": "根据分镜逐镜判断需要哪些演员、场景、商品素材，并优先返回可复用的本地资产ID；不要凭空创造不存在的ID。",
    }
    schema = STAGE_SCHEMAS[stage]
    return (
        CREATIVE_SYSTEM_PROMPT
        + f"\n\n当前阶段：{stage}\n任务：{instructions[stage]}"
        + "\n\n输入：\n" + json.dumps(data, ensure_ascii=False, indent=2)
        + "\n\n全局约束：\n" + json.dumps(constraints, ensure_ascii=False, indent=2)
        + "\n\n本阶段只输出以下JSON结构：\n"
        + json.dumps(schema, ensure_ascii=False, indent=2)
    )
