"""AI 补镜头实际执行桥接：把混合路由接到真实视频/图片 Provider，并记录费用。

安全边界：
- 只执行路由明确允许的任务。
- 商品事实/真实操作/真人身份等证据缺口永远不生成冒充素材。
- 生成结果默认“待复核”，不会自动进入最终分镜。
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .asset_generation import AssetGenerator
from .capability import CapabilityRouter
from .providers import GenericVideoProvider, GenerationRequest
from .usage_ledger import UsageLedger
from .hybrid_router import execute_ai_gap_generation, is_product_evidence_gap


def _video_config(root: Path) -> dict[str, Any]:
    path = root / "video-provider.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if isinstance(data, dict):
        value = data.get("video_provider", data)
        return value if isinstance(value, dict) else {}
    return {}


def _video_provider(root: Path) -> GenericVideoProvider:
    cfg = _video_config(root)
    return GenericVideoProvider(
        endpoint=str(cfg.get("endpoint") or ""),
        api_key=str(cfg.get("api_key") or ""),
        model=str(cfg.get("model") or ""),
        timeout=int(cfg.get("timeout", 300) or 300),
        headers=cfg.get("headers") or {},
        status_endpoint=str(cfg.get("status_endpoint") or ""),
        poll_interval=float(cfg.get("poll_interval", 3.0) or 3.0),
        task_id_field=str(cfg.get("task_id_field") or "id"),
        status_field=str(cfg.get("status_field") or "status"),
        cost_per_shot_rmb=float(cfg.get("cost_per_shot_rmb", 0.72) or 0.72),
        provider_name=str(cfg.get("name") or cfg.get("provider") or "视频生成 Provider"),
        require_key=bool(cfg.get("require_key", True)),
        embed_reference_assets=bool(cfg.get("embed_reference_assets", False)),
    )


def _prompt(task: dict[str, Any]) -> str:
    parts = [
        str(task.get("prompt") or ""),
        str(task.get("need") or ""),
        str(task.get("reason") or ""),
        str(task.get("related_selling_point") or ""),
    ]
    return "；".join(x.strip() for x in parts if x.strip()) or "生成与当前口播节奏匹配的通用辅助画面。"


def _output_path(output_root: Path, task: dict[str, Any], suffix: str) -> Path:
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(task.get("task_id") or "gap"))
    output_root.mkdir(parents=True, exist_ok=True)
    return output_root / f"hybrid-{safe}-{int(time.time() * 1000)}{suffix}"


def execute_configured_video_gap_generation(
    tasks,
    *,
    config_root: Path,
    output_root: Path,
    project_id: str = "",
    budget_remaining_rmb: float = 0.0,
    ledger: UsageLedger | None = None,
) -> dict[str, Any]:
    """用配置中的真实视频 Provider 执行已获准缺口，并写入 UsageLedger。"""
    root = Path(config_root)
    provider = _video_provider(root)
    capability = CapabilityRouter(root)

    decision = capability.decide_video()
    if decision.target == "unavailable":
        return {
            "task_count": len([x for x in tasks or [] if isinstance(x, dict)]),
            "tasks": [dict(x, status="未执行：视频生成能力不可用") for x in tasks or [] if isinstance(x, dict)],
            "generated": 0,
            "failed": 0,
            "blocked": 0,
            "budget_remaining_rmb": round(max(0.0, float(budget_remaining_rmb or 0.0)), 4),
            "provider": "不可用",
        }

    # CapabilityRouter 负责判断本地/云端能力；GenericVideoProvider 统一承载 REST 协议。
    if decision.target == "local" and not provider.endpoint:
        return {
            "task_count": 0,
            "tasks": [],
            "generated": 0,
            "failed": 0,
            "blocked": 0,
            "budget_remaining_rmb": round(max(0.0, float(budget_remaining_rmb or 0.0)), 4),
            "provider": "本地视频服务未配置 REST 端点",
        }

    rate = max(0.0, float(provider.cost_per_shot_rmb or 0.0))
    ledger = ledger or UsageLedger(root / "usage-ledger.json")

    def generate(task: dict[str, Any]) -> Path:
        if is_product_evidence_gap(task):
            raise RuntimeError("安全拦截：商品事实/真实操作证据不能由 AI 生成冒充。")
        duration = float(task.get("duration") or task.get("duration_seconds") or 3.0)
        refs = [str(x) for x in (task.get("reference_asset_paths") or []) if str(x).strip()]
        output = _output_path(Path(output_root), task, ".mp4")
        request = GenerationRequest(
            prompt=_prompt(task),
            output=output,
            duration=max(1.0, duration),
            reference_assets=[str(x) for x in (task.get("reference_assets") or [])],
            reference_asset_paths=refs,
        )
        started = time.monotonic()
        try:
            result = provider.generate(request)
        except Exception as exc:
            ledger.record_video(
                project_id=project_id,
                shot_id=str(task.get("task_id") or ""),
                provider=provider.provider_name,
                cost_rmb=rate,
                status="failed",
                error=str(exc),
            )
            raise
        ledger.record_video(
            project_id=project_id,
            shot_id=str(task.get("task_id") or ""),
            provider=provider.provider_name,
            cost_rmb=rate,
            status="success",
        )
        task["provider"] = provider.provider_name
        task["provider_target"] = decision.target
        task["generation_duration_ms"] = int((time.monotonic() - started) * 1000)
        task["source_type"] = "ai_generated_video"
        task["evidence_safe"] = False
        return result

    result = execute_ai_gap_generation(
        tasks,
        generator=generate,
        budget_remaining_rmb=budget_remaining_rmb,
        cost_per_ai_shot_rmb=rate,
    )
    result["provider"] = provider.provider_name
    result["provider_target"] = decision.target
    result["capability_reason"] = decision.reason
    return result


def execute_configured_image_gap_generation(
    tasks,
    *,
    config_root: Path,
    library_root: Path,
    project_id: str = "",
    budget_remaining_rmb: float = 0.0,
    ledger: UsageLedger | None = None,
) -> dict[str, Any]:
    """执行明确标记为图片的辅助素材；仍然禁止商品事实证据冒充。"""
    root = Path(config_root)
    generator = AssetGenerator(root / "asset-generation.json", Path(library_root), CapabilityRouter(root))
    ledger = ledger or UsageLedger(root / "usage-ledger.json")
    prepared = []
    for raw in tasks or []:
        if not isinstance(raw, dict):
            continue
        task = dict(raw)
        task["recommended_resolution"] = task.get("recommended_resolution") or "AI补辅助画面"
        task["generation_allowed"] = bool(task.get("generation_allowed"))
        task["generation_kind"] = "image"
        prepared.append(task)

    remaining = max(0.0, float(budget_remaining_rmb or 0.0))
    generated = failed = blocked = 0
    out = []
    for task in prepared:
        if not task.get("generation_allowed"):
            task["status"] = task.get("status") or "未进入AI生成"
            out.append(task)
            continue
        if is_product_evidence_gap(task):
            task["generation_allowed"] = False
            task["status"] = "已拦截：真实商品证据不能用生成图片冒充"
            blocked += 1
            out.append(task)
            continue
        cost = max(0.0, generator.price(str(task.get("asset_kind") or "辅助画面")))
        if cost > 0 and remaining < cost:
            task["generation_allowed"] = False
            task["status"] = "已拦截：预算不足"
            blocked += 1
            out.append(task)
            continue
        try:
            kind = str(task.get("asset_kind") or "辅助画面")
            result = generator.generate(
                kind,
                str(task.get("name") or task.get("task_id") or "AI辅助画面"),
                _prompt(task),
                tags=["混合路由", "待复核"],
                request_id=str(task.get("task_id") or ""),
            )
            task["generated_path"] = str(result.asset.path or "")
            task["provider"] = result.provider
            task["source_type"] = "ai_generated_image"
            task["evidence_safe"] = False
            task["review_status"] = "待复核"
            task["accepted_into_storyboard"] = False
            task["status"] = "AI辅助图片已生成，待人工复核"
            task["estimated_cost_rmb"] = result.cost_rmb
            remaining = max(0.0, remaining - result.cost_rmb)
            ledger.record_asset(
                project_id=project_id,
                shot_id=str(task.get("task_id") or ""),
                asset_kind=kind,
                provider=result.provider,
                cost_rmb=result.cost_rmb,
                status="success",
            )
            generated += 1
        except Exception as exc:
            task["status"] = "AI辅助图片生成失败"
            task["generation_error"] = str(exc)
            task["accepted_into_storyboard"] = False
            ledger.record_asset(
                project_id=project_id,
                shot_id=str(task.get("task_id") or ""),
                asset_kind=str(task.get("asset_kind") or "辅助画面"),
                provider="图片生成服务",
                cost_rmb=cost,
                status="failed",
                error=str(exc),
            )
            failed += 1
        out.append(task)

    return {
        "task_count": len(out),
        "tasks": out,
        "generated": generated,
        "failed": failed,
        "blocked": blocked,
        "budget_remaining_rmb": round(remaining, 4),
        "provider": "图片生成服务",
        "method": "真实 Provider + 费用账本 + 待复核闸门",
    }
