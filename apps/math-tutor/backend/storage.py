"""Versioned SQLite schema initialization for the Math Tutor API.

This migration runner currently establishes only the infrastructure metadata
schema. Learner/course business tables belong to their dedicated roadmap tasks.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Callable

SCHEMA_VERSION = "1"

Migration = tuple[int, Callable[[sqlite3.Connection], None]]


def _migration_1(connection: sqlite3.Connection) -> None:
    """Create the initial app metadata table."""
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


MIGRATIONS: tuple[Migration, ...] = (
    (1, _migration_1),
)


def initialize_database(database_path: str | Path) -> None:
    """Create the database and apply every not-yet-recorded migration atomically."""
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        applied = {
            row[0]
            for row in connection.execute(
                "SELECT version FROM schema_migrations"
            ).fetchall()
        }
        for version, migration in MIGRATIONS:
            if version in applied:
                continue
            migration(connection)
            connection.execute(
                "INSERT INTO schema_migrations(version) VALUES (?)",
                (version,),
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
