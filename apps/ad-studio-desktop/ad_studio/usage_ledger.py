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
    ) -> dict[str, Any]:
        item = {
            "id": uuid.uuid4().hex[:12],
            "time": datetime.now().isoformat(timespec="seconds"),
            "function": function,
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
        }
        rows = self._load()
        rows.append(item)
        self.path.write_text(json.dumps(rows[-2000:], ensure_ascii=False, indent=2), encoding="utf-8")
        return item

    def recent(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._load()[-max(1, int(limit)):][::-1]

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
