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
from .footage import normalize_footage_analysis, rank_footage_analysis, audit_footage_coverage
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
            axis = AD_VARIANT_AXES[i % len(AD_VARIANT_AXES)]
            variant_constraints["creative_variant_axis"] = axis
            variant_constraints["creative_variant_instruction"] = diversity_prompts[i] + " 当前测试轴：" + axis["name"] + "；" + axis["instruction"]
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
                    "speech_quality": "none|clear|filler|unclear",
                    "duplicate_group": "string；同一拍摄动作/卖点的重复镜头使用相同分组名，无重复则为空字符串",
                    "duplicate_confidence": "0..1；判断重复镜头的置信度",
                    "take_rank": "integer；同组镜头的推荐优先级，1为最佳",
                    "best_take": "boolean；是否为该重复组最值得保留的版本",
                    "keep_reason": "string；为什么这一版比同组其他版本更值得保留",
                    "selection_score": "number；本地综合素材优先级分数，仅用于排序",
                    "material_rank": "integer；整个可用素材池的优先级，1为最高"
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
            "必须把重复拍摄的同类镜头放入 duplicate_group，并在同组内比较清晰度、构图、商品展示完整度、动作完成度、口播质量和广告价值，给出 take_rank、best_take、duplicate_confidence 与 keep_reason。没有重复镜头时 duplicate_group 为空。"
            "只返回 JSON。\n\n" + json.dumps(payload, ensure_ascii=False, indent=2)
        )
        return rank_footage_analysis(self.complete_json(
            profile, prompt, function="实拍素材视觉分析", image_paths=images
        ))

    def plan_footage(
        self,
        product: dict[str, Any],
        creative_plan: dict[str, Any],
        footage_clips: list[dict[str, Any]],
        constraints: dict[str, Any] | None = None,
        footage_analysis: dict[str, Any] | None = None,
        footage_coverage: dict[str, Any] | None = None,
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
                "task_type": creative_plan.get("task_type", ""),
                "task_rules": creative_plan.get("task_rules", {}),
                "task_policy": creative_plan.get("task_policy", {}),
            },
            "footage_clips": footage_clips,
            "footage_analysis": footage_analysis or {},
            "footage_coverage": footage_coverage or {},
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
            "4. 如果转写结果中出现寒暄、重复、口头禅、停顿或与卖点无关的废话，必须删除；用 ranges 指定多个保留区间，只保留有价值的表达。\n"
            "5. ranges 使用素材原始时间轴的 [start,end]，多个区间按时间顺序排列；没有废话时使用单个区间。\n"
            "6. 不能为了删废话破坏一句话的完整语义；时间戳不够精确时，只在 segment 边界做安全裁剪。\n"
            "7. 每个镜头给出画面说明、口播/文案、字幕位置、构图、节奏、转场，供本地执行。\n"            "8. footage_analysis 中如果多个素材属于同一 duplicate_group，优先使用 best_take=true、take_rank 更高的版本；除非低排名版本包含主版本没有的独特有效片段，否则不要重复使用同组低排名素材。\n"
            "9. material_rank 越小代表整个素材池越值得优先使用；先考虑高排名素材，再根据镜头目标和卖点覆盖做最终取舍，不要机械按排名剪辑。\n"
            "10. footage_coverage 是最终覆盖审计：开场优先使用 opening_candidate；每个 covered=true 的重要卖点至少覆盖一次；唯一能覆盖重要卖点的低排名素材可以优先于纯排名更高但重复的信息。缺失项只能记录，禁止编造不存在的画面。\n"
            "11. 广告表达避免违反广告法的绝对化、虚假、无法证明的承诺。\n"
            "12. 输出必须是严格 JSON，不要输出 Markdown。\n"
             "13. 必须严格服从 task_type。电商短视频：开场快速进入商品/痛点，卖点优先，节奏紧凑，结尾保留明确转化信息；商品主图视频：商品本体、细节、功能演示和购买决策信息优先，不用剧情性镜头替代商品证据；广告投放视频：优先强钩子、单一核心卖点、清晰 CTA，并保证不同创意方案之间具有可测试的差异。\n"
             "14. task_type 不同，镜头排序、素材取舍和时长都必须不同；不要因为素材排名高就违反任务目标。AI 可在 30-60 秒范围内按信息密度决定最终时长，但商品主图视频应避免无意义延长，广告投放视频应优先保证前几秒钩子。\n"
             "15. 如果任务要求的关键画面在实拍素材中缺失，只能在 footage_coverage/footage_gaps 中标记缺口，禁止虚构；商品证据缺失优先标记待补拍。\n"
             "16. 必须遵守 task_policy 的 min_seconds/max_seconds/sequence；sequence 是镜头结构优先级，不要求素材恰好一一对应，但最终剪辑必须尽量覆盖。"
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

AD_VARIANT_AXES = [
    {"id": "hook", "name": "钩子角度", "instruction": "改变前3秒的注意力机制，不只是换同义词。"},
    {"id": "selling_point", "name": "核心卖点", "instruction": "选择不同的第一核心卖点或卖点组合。"},
    {"id": "proof", "name": "证明方式", "instruction": "改变证明方式：实拍演示、对比、体验、场景证据等。"},
    {"id": "cta", "name": "转化动作", "instruction": "改变结尾行动机制和转化理由。"},
]
def audit_creative_factual_consistency(product: dict[str, Any], variants: list[dict[str, Any]], forbidden_terms: list[str] | None = None) -> dict[str, Any]:
    """投放前事实/质量审计：只基于用户提供的商品资料和创意字段，不推断未提供的商品事实。"""
    product = product if isinstance(product, dict) else {}
    forbidden_terms = [str(x).strip() for x in (forbidden_terms or []) if str(x).strip()]
    def norm(v):
        if isinstance(v,(list,tuple)): return " ".join(norm(x) for x in v)
        if isinstance(v,dict): return " ".join(f"{k} {norm(x)}" for k,x in v.items())
        return str(v or "").strip()
    source_text = norm(product)
    allowed_points = [norm(x) for x in product.get("selling_points",[]) if norm(x)] if isinstance(product.get("selling_points",[]),list) else []
    findings=[]
    for i,v in enumerate(variants,1):
        text = norm(v)
        unsupported=[p for p in [norm(x) for x in v.get("selling_points",[])] if p and allowed_points and p not in allowed_points]
        banned=[term for term in forbidden_terms if term and term in text]
        absolute=[w for w in ("第一","唯一","顶级","最好","绝对","百分百","100%","全网最低","国家级","永久") if w in text]
        missing_source=not bool(source_text)
        findings.append({
            "variant_index":i,
            "product_fact_status":"缺少商品资料，无法完成事实核验" if missing_source else ("待人工核验" if unsupported else "资料范围内未发现明显冲突"),
            "unsupported_selling_points":unsupported,
            "forbidden_term_hits":banned,
            "absolute_or_high_risk_claims":absolute,
            "product_subject_obscured":"待画面复核",
            "visual_fact_match":"待成片/分镜画面复核",
            "subtitle_product_consistency":"待字幕与商品资料复核",
        })
    return {
        "enabled":bool(variants),
        "method":"投放前商品事实与创意质量确定性审计",
        "data_boundary":"只依据已提供商品资料、创意字段和用户维护的禁用词；未知事实标记为待核验，不自行补全。",
        "summary":{"variants":len(findings),"variants_with_risk":sum(bool(x["unsupported_selling_points"] or x["forbidden_term_hits"] or x["absolute_or_high_risk_claims"]) for x in findings)},
        "variants":findings,
    }



def audit_storyboard_fact_consistency(product: dict[str, Any], variants: list[dict[str, Any]]) -> dict[str, Any]:
    """投放前分镜/商品事实审计；视觉属性没有真实视觉证据时必须待复核。"""
    product = product if isinstance(product, dict) else {}
    facts = product.get("selling_points", []) if isinstance(product.get("selling_points", []), list) else []
    fact_text = " ".join(str(x) for x in facts)
    results = []
    for i, variant in enumerate(variants, 1):
        shots = variant.get("shots", []) if isinstance(variant, dict) else []
        if not isinstance(shots, list):
            shots = []
        shot_results = []
        for n, shot in enumerate(shots, 1):
            if not isinstance(shot, dict):
                shot = {"description": str(shot)}
            desc = " ".join(str(shot.get(k, "")) for k in ("description", "visual", "action", "product_focus", "subtitle", "voiceover"))
            related = [str(x) for x in facts if str(x) and str(x) in desc]
            shot_results.append({
                "shot_index": n,
                "product_focus": shot.get("product_focus") or "待视觉复核",
                "covered_facts": related,
                "fact_status": "有商品资料对应" if related else ("待复核" if fact_text else "缺少商品资料"),
                "obscured": "待视觉复核",
                "appearance_fidelity": "待视觉复核",
                "function_fidelity": "待视觉复核",
                "subtitle_visual_consistency": "待复核",
            })
        results.append({"variant_index": i, "shots": shot_results, "shot_count": len(shot_results)})
    return {
        "enabled": bool(variants),
        "method": "投放前分镜与商品事实确定性审计",
        "data_boundary": "文字层只做已提供商品资料的对应检查；商品外观、遮挡、功能演示和字幕画面一致性必须由实际分镜/成片视觉复核确认。",
        "variants": results,
    }

def audit_visual_fact_consistency(product: dict[str, Any], footage_analysis: dict[str, Any], variant_footage_plans: dict[str, Any] | None = None) -> dict[str, Any]:
    """基于已经由视觉模型观察过的关键帧结果，检查实际采用素材的视觉事实风险。"""
    analysis = rank_footage_analysis(footage_analysis or {})
    clips = {str(x.get("source","")): x for x in analysis.get("clips", []) if isinstance(x, dict)}
    plans = variant_footage_plans if isinstance(variant_footage_plans, dict) else {}
    results=[]
    for key, items in plans.items():
        if not isinstance(items, list):
            continue
        used=[]
        for item in items:
            if not isinstance(item, dict):
                continue
            source=str(item.get("source",""))
            clip=clips.get(source,{})
            tags={str(x) for x in (clip.get("visual_tags") or [])}
            risks=[]
            if clip.get("usable") is False: risks.append("素材已被视觉分析判定为不可用")
            if "blocked" in tags: risks.append("商品可能被遮挡")
            if "blur" in tags: risks.append("画面可能模糊")
            if "shake" in tags: risks.append("画面可能抖动")
            covered=[str(x) for x in (clip.get("selling_points") or []) if str(x)]
            used.append({
                "source":source,
                "visual_tags":sorted(tags),
                "covered_selling_points":covered,
                "risk_status":"需复核" if risks else "视觉分析通过初筛",
                "risks":risks,
                "reason":str(clip.get("reason","")),
                "best_take":bool(clip.get("best_take")),
            })
        results.append({"variant_index":str(key),"shots":used})
    return {
        "enabled":bool(results),
        "method":"基于关键帧视觉模型结果的实际素材事实复核",
        "data_boundary":"模型已实际观察关键帧后，系统只把其视觉标签、可用性、卖点对应和遮挡/模糊/抖动结果映射到最终采用素材；没有被视觉模型观察到的内容不会被宣称已核验。",
        "variants":results,
    }


def audit_ad_variant_set(plans: list[dict[str, Any]], task_type: str) -> dict[str, Any]:
    """不调用新模型，确定性检查广告方案是否形成真正可测试的创意差异。"""
    if task_type != "广告投放视频" or len(plans) <= 1:
        return {
            "enabled": False, "variant_count": len(plans), "diversity_score": 0,
            "test_design_score": 0, "method": "非广告多版本不启用A/B审计",
        }

    def norm(value):
        if isinstance(value, (list, tuple)):
            return "｜".join(norm(x) for x in value if x)
        if isinstance(value, dict):
            return "｜".join(f"{k}:{norm(v)}" for k, v in sorted(value.items()) if v)
        return str(value or "").strip()

    # 这些字段代表创意机制，而不是投放平台。它们用于判断“到底改了什么”。
    mechanism_keys = ["hook", "strategy", "selling_points", "video_form", "proof", "cta"]
    surface_keys = ["script"]
    signatures = ["|".join(norm(p.get(k, "")) for k in mechanism_keys + surface_keys) for p in plans]
    unique = len(set(signatures))
    pair_count = max(1, len(plans) * (len(plans) - 1) // 2)
    diff_count = 0
    mechanism_diff_count = 0
    pairs = []
    for i in range(len(plans)):
        for j in range(i + 1, len(plans)):
            mechanism_diffs = [k for k in mechanism_keys if norm(plans[i].get(k, "")) != norm(plans[j].get(k, ""))]
            surface_diffs = [k for k in surface_keys if norm(plans[i].get(k, "")) != norm(plans[j].get(k, ""))]
            if mechanism_diffs or surface_diffs:
                diff_count += 1
            if mechanism_diffs:
                mechanism_diff_count += 1
            if not mechanism_diffs and surface_diffs:
                quality = "仅表层差异"
            elif len(mechanism_diffs) == 1:
                quality = "单一机制差异（适合做明确对照）"
            elif len(mechanism_diffs) >= 2:
                quality = "多机制差异（结果归因会更困难）"
            else:
                quality = "没有明显差异"
            pairs.append({
                "a": i + 1, "b": j + 1,
                "different_fields": mechanism_diffs + surface_diffs,
                "mechanism_differences": mechanism_diffs,
                "surface_differences": surface_diffs,
                "test_quality": quality,
            })

    diversity_score = round(100 * diff_count / pair_count)
    mechanism_score = round(100 * mechanism_diff_count / pair_count)
    single_axis_pairs = sum(1 for p in pairs if len(p["mechanism_differences"]) == 1)
    no_mechanism_pairs = sum(1 for p in pairs if not p["mechanism_differences"])
    if mechanism_score == 100 and single_axis_pairs == pair_count:
        design_status = "强：每组对照都只有一个核心机制变化"
        test_design_score = 100
    elif mechanism_score == 100:
        design_status = "可测：每组都有核心机制差异，但部分同时改变多个机制"
        test_design_score = 75
    elif no_mechanism_pairs:
        design_status = "需调整：存在没有核心机制差异的版本对照"
        test_design_score = max(0, mechanism_score - 20)
    else:
        design_status = "可测但不够干净：部分版本对照只改变表层或多个机制"
        test_design_score = max(0, mechanism_score - 10)

    return {
        "enabled": True,
        "variant_count": len(plans),
        "unique_signatures": unique,
        "diversity_score": diversity_score,
        "mechanism_score": mechanism_score,
        "test_design_score": test_design_score,
        "design_status": design_status,
        "pairs": pairs,
        "method": "核心机制字段与表层字段分离的确定性创意实验设计审计",
    }


def build_creative_test_plan(plans: list[dict[str, Any]], audit: dict[str, Any] | None = None) -> dict[str, Any]:
    """把投放前创意差异转换成“测试目的→版本设计→观察结果”的确定性方案。"""
    audit = audit if isinstance(audit, dict) else audit_ad_variant_set(plans, "广告投放视频")
    def norm(value):
        if isinstance(value, (list, tuple)): return "、".join(norm(x) for x in value if x)
        if isinstance(value, dict): return "、".join(f"{k}:{norm(v)}" for k, v in value.items() if v)
        return str(value or "").strip()
    axis_names={"hook":"开场钩子","strategy":"核心广告策略","selling_points":"核心卖点","video_form":"视频形式","proof":"证明方式","cta":"行动引导"}
    out=[]
    for i,p in enumerate(plans,1):
        axis=p.get("variant_test_axis") or {}
        aid=str(axis.get("id") or "").strip() if isinstance(axis,dict) else ""
        aname=str(axis.get("name") or "").strip() if isinstance(axis,dict) else ""
        mechanism=axis_names.get(aid,aname or "未明确")
        out.append({
            "variant_index":i,
            "test_purpose":f"验证“{mechanism}”变化是否值得继续扩大测试" if mechanism!="未明确" else "验证当前创意机制是否形成了可解释的差异",
            "primary_test_axis":{"id":aid,"name":aname or mechanism,"instruction":str(axis.get("instruction") or "").strip() if isinstance(axis,dict) else ""},
            "version_design":{k:norm(p.get(k)) for k in ("hook","strategy","selling_points","video_form","proof","cta")},
            "observation_targets":["用户是否对该创意机制产生更强的真实反馈","用户反馈是否集中在本轮测试的核心机制，而不是其他同时变化的元素","下一轮是否值得继续扩大、缩小或替换该测试轴"],
            "result_status":"待真实投放数据",
        })
    next_round=[]
    pairs=audit.get("pairs",[]) if isinstance(audit,dict) else []
    if any(len(p.get("mechanism_differences",[]))>1 for p in pairs): next_round.append("优先拆开同时变化的核心机制，让下一轮尽量一次只验证一个主要变量。")
    if any(not p.get("mechanism_differences") and p.get("surface_differences") for p in pairs): next_round.append("存在只有表层表达变化的版本对照；下一轮应改变真正的创意机制，而不是只换文案或包装。")
    if any(not p.get("mechanism_differences") and not p.get("surface_differences") for p in pairs): next_round.append("存在几乎没有结构差异的版本；下一轮应重新设计测试轴。")
    if not next_round: next_round.append("当前版本已经形成明确的机制对照；下一轮优先沿真实结果最需要验证的机制继续做窄范围对照。")
    return {"enabled":bool(audit.get("enabled")),"method":"投放前确定性创意测试方案：测试目的→版本设计→需要观察的真实结果","data_boundary":"不生成结果、不猜测平台、不产生平台转化指标等虚假数据","variants":out,"next_round_recommendations":next_round}


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
            "transition": "string",
            "ranges": "[[start,end],...]；如需删除口播废话/重复段，必须使用多个保留区间",
            "duplicate_group": "string；重复镜头组名", "duplicate_confidence": "0..1", "take_rank": "integer；1为最佳", "best_take": "boolean", "keep_reason": "string", "selection_score": "number", "material_rank": "integer"
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