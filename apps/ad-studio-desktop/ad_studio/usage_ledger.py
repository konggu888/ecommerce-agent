from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
import json
import uuid
from urllib.parse import urlsplit, urlunsplit


def sanitize_endpoint(value: Any) -> str:
    """Persist endpoint provenance without URL credentials, query parameters, or fragments."""
    raw = str(value or "").strip()
    if not raw:
        return ""
    try:
        parts = urlsplit(raw)
        if not parts.scheme or not parts.hostname:
            return "自定义 endpoint（无法安全解析）"
        host = parts.hostname
        if parts.port:
            host = f"{host}:{parts.port}"
        return urlunsplit((parts.scheme, host, parts.path.rstrip("/"), "", ""))
    except Exception:
        return "自定义 endpoint（无法安全解析）"


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
        quantity: float = 1.0,
        unit_cost_rmb: float = 0.0,
        cost_status: str = "unknown",
        usage_status: str = "unknown",
        endpoint: str = "",
    ) -> dict[str, Any]:
        item = {
            "id": uuid.uuid4().hex[:12],
            "time": datetime.now().isoformat(timespec="seconds"),
            "function": function,
            "category": category,
            "project_id": project_id,
            "shot_id": shot_id,
            "asset_kind": asset_kind,
            "quantity": float(quantity or 1.0),
            "unit_cost_rmb": round(float(unit_cost_rmb or 0), 6),
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
            "cost_status": str(cost_status or "unknown"),
            "usage_status": str(usage_status or "unknown"),
            "endpoint": sanitize_endpoint(endpoint),
        }
        rows = self._load()
        rows.append(item)
        self._write_rows_atomically(rows)
        return item

    def record_many(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Append several ledger rows with one atomic file replacement."""
        if not records:
            return []
        rows = self._load()
        items = []
        for values in records:
            item = {
                "id": uuid.uuid4().hex[:12],
                "time": datetime.now().isoformat(timespec="seconds"),
                "function": str(values.get("function", "")),
                "category": str(values.get("category", "other") or "other"),
                "project_id": str(values.get("project_id", "") or ""),
                "shot_id": str(values.get("shot_id", "") or ""),
                "asset_kind": str(values.get("asset_kind", "") or ""),
                "quantity": float(values.get("quantity", 1.0) or 1.0),
                "unit_cost_rmb": round(float(values.get("unit_cost_rmb", 0) or 0), 6),
                "model_id": str(values.get("model_id", "") or ""),
                "model_name": str(values.get("model_name", "") or ""),
                "provider": str(values.get("provider", "") or ""),
                "model": str(values.get("model", "") or ""),
                "status": str(values.get("status", "success") or "success"),
                "prompt_tokens": int(values.get("prompt_tokens", 0) or 0),
                "completion_tokens": int(values.get("completion_tokens", 0) or 0),
                "total_tokens": int(values.get("total_tokens", 0) or 0),
                "estimated_cost_rmb": round(float(values.get("estimated_cost_rmb", 0) or 0), 6),
                "duration_ms": int(values.get("duration_ms", 0) or 0),
                "error": str(values.get("error", "") or ""),
                "cost_status": str(values.get("cost_status", "unknown") or "unknown"),
                "usage_status": str(values.get("usage_status", "unknown") or "unknown"),
                "endpoint": sanitize_endpoint(values.get("endpoint", "")),
            }
            items.append(item)
        rows.extend(items)
        self._write_rows_atomically(rows)
        return items

    def _write_rows_atomically(self, rows: list[dict[str, Any]]) -> None:
        """Persist the complete cost history via atomic replacement; never truncate older charges."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_name(f".{self.path.name}.{uuid.uuid4().hex}.tmp")
        try:
            temp_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
            temp_path.replace(self.path)
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise

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
            quantity=1,
            unit_cost_rmb=cost_rmb,
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
            quantity=1,
            unit_cost_rmb=cost_rmb,
            error=error,
        )

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

    def shot_actual_cost(self, project_id: str, shot_id: str) -> float | None:
        """Return success-only actual cost for a shot, or None when no ledger history exists."""
        rows = [
            row for row in self._load()
            if row.get("project_id") == project_id
            and row.get("shot_id") == shot_id
            and row.get("status") == "success"
        ]
        if not rows:
            return None
        return round(sum(float(row.get("estimated_cost_rmb", 0) or 0) for row in rows), 6)

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
