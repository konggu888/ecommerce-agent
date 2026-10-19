"""Minimal FastAPI entry point for MATH-002 stack verification."""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI

from .storage import initialize_database, read_metadata


def create_app(database_path: str | Path | None = None) -> FastAPI:
    if database_path is None:
        configured_path = os.environ.get("MATH_TUTOR_DB_PATH")
        database_path = configured_path or (Path(__file__).resolve().parents[1] / "data" / "math_tutor.sqlite3")
    path = Path(database_path)
    initialize_database(path)

    app = FastAPI(title="Math Tutor API", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str | bool]:
        return {
            "ok": True,
            "service": "math-tutor-api",
            "storage": "sqlite",
            "schema_version": read_metadata(path, "schema_version") or "unknown",
        }

    return app


app = create_app()
