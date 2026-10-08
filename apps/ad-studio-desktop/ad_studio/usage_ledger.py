from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
import json
import uuid


class UsageLedger:
    """Local, append-only-ish usage ledger for model calls.

    It records the model actually called, function/stage, status, token counts,
    duration and estimated cost. No cloud database is required.
    """

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
            return value if isinstance(value, list) else []
        except Exception:
            return []

    def record(
        self,
        *,
        function: str,
        model_id: str,
        model_name: str,
        provider: str,
        model: str,
        status: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        estimated_cost_rmb: float = 0.0,
        duration_ms: int = 0,
        error: str = "",
        category: str = "model",
        project_id: str = "",
        shot_id: str = "",
        asset_kind: str = "",
    ) -> dict[str, Any]:
        item = {
            "id": uuid.uuid4().hex[:12],
            "time": datetime.now().isoformat(timespec="seconds"),
            "function": function,
            "category": category,
            "project_id": project_id,
            "shot_id": shot_id,
            "asset_kind": asset_kind,
            "model_id": model_id,
            "model_name": model_name,
            "provider": provider,
            "model": model,
            "status": status,
            "prompt_tokens": int(prompt_tokens or 0),
            "completion_tokens": int(completion_tokens or 0),
            "total_tokens": int(total_tokens or 0),
            "estimated_cost_rmb": round(float(estimated_cost_rmb or 0), 6),
            "duration_ms": int(duration_ms or 0),
            "error": error,
            "project_id": project_id,
            "shot_id": shot_id,
            "category": category,
            "quantity": float(quantity or 0),
            "unit_cost_rmb": round(float(unit_cost_rmb or 0), 6),
        }
        rows = self._load()
        rows.append(item)
        self.path.write_text(json.dumps(rows[-2000:], ensure_ascii=False, indent=2), encoding="utf-8")
        return item

    def record_asset(
        self,
        *,
        project_id: str,
        shot_id: str = "",
        asset_kind: str,
        provider: str,
        cost_rmb: float,
        status: str = "success",
        error: str = "",
        project_id: str = "",
        shot_id: str = "",
        category: str = "model",
        quantity: float = 1.0,
        unit_cost_rmb: float = 0.0,
    ) -> dict[str, Any]:
        return self.record(
            function=f"{asset_kind}素材生成",
            model_id="",
            model_name=provider,
            provider=provider,
            model="",
            status=status,
            estimated_cost_rmb=cost_rmb,
            category="asset",
            project_id=project_id,
            shot_id=shot_id,
            asset_kind=asset_kind,
            error=error,
        )

    def record_video(
        self,
        *,
        project_id: str,
        shot_id: str,
        provider: str,
        cost_rmb: float,
        status: str = "success",
        error: str = "",
    ) -> dict[str, Any]:
        return self.record(
            function="视频镜头生成",
            model_id="",
            model_name=provider,
            provider=provider,
            model="",
            status=status,
            estimated_cost_rmb=cost_rmb,
            category="video",
            project_id=project_id,
            shot_id=shot_id,
            error=error,
        )

    def project_summary(self, project_id: str) -> dict[str, Any]:
        rows = [x for x in self._load() if x.get("project_id") == project_id]
        success = [x for x in rows if x.get("status") == "success"]
        by_category: dict[str, float] = {}
        for row in success:
            key = str(row.get("category") or "other")
            by_category[key] = by_category.get(key, 0.0) + float(row.get("estimated_cost_rmb", 0) or 0)
        return {
            "project_id": project_id,
            "entries": len(rows),
            "actual_cost_rmb": round(sum(float(x.get("estimated_cost_rmb", 0) or 0) for x in success), 6),
            "by_category": {k: round(v, 6) for k, v in by_category.items()},
        }

    def recent(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._load()[-max(1, int(limit)):][::-1]

    def project_summary(self, project_id: str) -> dict[str, Any]:
        rows = [x for x in self._load() if x.get("project_id") == project_id]
        success = [x for x in rows if x.get("status") == "success"]
        return {
            "project_id": project_id,
            "entries": len(rows),
            "success": len(success),
            "failed": len(rows) - len(success),
            "tokens": sum(int(x.get("total_tokens", 0) or 0) for x in rows),
            "actual_cost_rmb": round(sum(float(x.get("estimated_cost_rmb", 0) or 0) for x in success), 6),
            "by_category": {category: round(sum(float(x.get("estimated_cost_rmb", 0) or 0) for x in success if x.get("category") == category), 6) for category in sorted({x.get("category", "model") for x in success})},
        }

    def summary(self) -> dict[str, Any]:
        rows = self._load()
        success = [x for x in rows if x.get("status") == "success"]
        return {
            "calls": len(rows),
            "success": len(success),
            "failed": len(rows) - len(success),
            "tokens": sum(int(x.get("total_tokens", 0) or 0) for x in rows),
            "estimated_cost_rmb": round(sum(float(x.get("estimated_cost_rmb", 0) or 0) for x in rows), 6),
        }
