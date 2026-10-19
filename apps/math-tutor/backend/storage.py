"""Minimal SQLite baseline storage used to verify file-backed persistence.

This is infrastructure validation, not the learner-progress schema.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_VERSION = "1"


def initialize_database(database_path: str | Path) -> None:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS app_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "INSERT INTO app_meta(key, value) VALUES ('schema_version', ?) "
            "ON CONFLICT(key) DO NOTHING",
            (SCHEMA_VERSION,),
        )


def read_metadata(database_path: str | Path, key: str) -> str | None:
    with sqlite3.connect(database_path) as connection:
        row = connection.execute(
            "SELECT value FROM app_meta WHERE key = ?", (key,)
        ).fetchone()
    return row[0] if row else None


def write_metadata(database_path: str | Path, key: str, value: str) -> None:
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "INSERT INTO app_meta(key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
