from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
import json
import os
import tempfile
import uuid


class UsageLedger:
    """Local, append-only-ish usage ledger for model calls.

    It records the model actually called, function/stage, status, token counts,
    duration and estimated cost. No cloud database is required.
    """

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.last_load_warning = ""

    def _load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            # Never silently treat a damaged ledger as empty: preserve the original
            # bytes before allowing a new ledger to be written.
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            backup = self.path.with_name(f"{self.path.name}.corrupt-{stamp}")
            try:
                self.path.replace(backup)
            except OSError as move_exc:
                raise RuntimeError(
                    f"成本账本无法读取，且无法安全保留损坏文件：{self.path} ({move_exc})"
                ) from exc
            self.last_load_warning = f"成本账本格式/读取异常，原文件已保留为：{backup}；原因：{exc}"
            return []
        if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            backup = self.path.with_name(f"{self.path.name}.corrupt-{stamp}")
            try:
                self.path.replace(backup)
            except OSError as exc:
                raise RuntimeError(
                    f"成本账本结构异常，且无法安全保留损坏文件：{self.path} ({exc})"
                ) from exc
            self.last_load_warning = f"成本账本结构异常，原文件已保留为：{backup}"
            return []
        return value

    def _save(self, rows: list[dict[str, Any]]) -> None:
        """Atomically replace the ledger so an interrupted write cannot truncate history."""
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as stream:
                temp_path = Path(stream.name)
                json.dump(rows, stream, ensure_ascii=False, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_path, self.path)
        finally:
            if temp_path is not None:
                try:
                    temp_path.unlink(missing_ok=True)
                except OSError:
                    pass

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
        }
        rows = self._load()
        rows.append(item)
        self._save(rows)
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


    def all_entries(self) -> list[dict[str, Any]]:
        """Return the complete local history newest-first; UI views must not silently truncate it."""
        return self._load()[::-1]

    def recent(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.all_entries()[:max(1, int(limit))]

    def project_summary(self, project_id: str) -> dict[str, Any]:
        rows = [x for x in self._load() if x.get("project_id") == project_id]
        success = [x for x in rows if x.get("status") == "success"]
        # A failed stage can still incur provider cost (for example, a model
        # returned billable tokens but malformed JSON). Include every recorded
        # non-zero estimate in cost totals; success/failure counts remain separate.
        estimated_cost = round(sum(float(x.get("estimated_cost_rmb", 0) or 0) for x in rows), 6)
        categories = sorted({x.get("category", "model") for x in rows if float(x.get("estimated_cost_rmb", 0) or 0) != 0})
        return {
            "project_id": project_id,
            "entries": len(rows),
            "success": len(success),
            "failed": len(rows) - len(success),
            "tokens": sum(int(x.get("total_tokens", 0) or 0) for x in rows),
            "estimated_cost_rmb": estimated_cost,
            # Kept for existing project/UI compatibility; it is an estimate,
            # not a verified provider invoice total.
            "actual_cost_rmb": estimated_cost,
            "by_category": {category: round(sum(float(x.get("estimated_cost_rmb", 0) or 0) for x in rows if x.get("category", "model") == category), 6) for category in categories},
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
