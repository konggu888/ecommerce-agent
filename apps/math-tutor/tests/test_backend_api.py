"""Integration checks for FastAPI, SQLite persistence, and schema migrations."""
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app import create_app
from backend.storage import initialize_database, read_metadata, write_metadata


def test_actual_fastapi_health_endpoint_uses_sqlite(tmp_path):
    database_path = tmp_path / "nested" / "math_tutor.sqlite3"
    app = create_app(database_path)

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "service": "math-tutor-api",
        "storage": "sqlite",
        "schema_version": "1",
    }
    assert database_path.is_file()


def test_sqlite_file_persists_across_reinitialization(tmp_path):
    database_path = tmp_path / "math_tutor.sqlite3"
    initialize_database(database_path)
    write_metadata(database_path, "persistence_probe", "survives-reopen")

    # Reinitialization must preserve both metadata and migration history.
    initialize_database(database_path)

    assert read_metadata(database_path, "persistence_probe") == "survives-reopen"
    import sqlite3

    with sqlite3.connect(database_path) as connection:
        versions = connection.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        ).fetchall()
    assert versions == [(1,)]


def test_schema_migration_is_idempotent_and_does_not_reset_custom_metadata(tmp_path):
    database_path = tmp_path / "math_tutor.sqlite3"
    initialize_database(database_path)
    write_metadata(database_path, "custom_setting", "keep-me")

    for _ in range(3):
        initialize_database(database_path)

    assert read_metadata(database_path, "custom_setting") == "keep-me"
    assert read_metadata(database_path, "schema_version") == "1"


def test_existing_metadata_database_is_adopted_without_losing_values(tmp_path):
    import sqlite3

    database_path = tmp_path / "existing.sqlite3"
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "CREATE TABLE app_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO app_meta(key, value) VALUES ('schema_version', '1')"
        )
        connection.execute(
            "INSERT INTO app_meta(key, value) VALUES ('legacy_setting', 'preserve')"
        )

    initialize_database(database_path)

    assert read_metadata(database_path, "legacy_setting") == "preserve"
    import sqlite3

    with sqlite3.connect(database_path) as connection:
        versions = connection.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        ).fetchall()
    assert versions == [(1,)]
