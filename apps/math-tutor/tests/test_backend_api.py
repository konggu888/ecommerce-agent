"""Integration checks for the actual FastAPI app and file-backed SQLite baseline."""
from fastapi.testclient import TestClient

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

    # A new initialization/connection must preserve the previously written value.
    initialize_database(database_path)

    assert read_metadata(database_path, "persistence_probe") == "survives-reopen"
