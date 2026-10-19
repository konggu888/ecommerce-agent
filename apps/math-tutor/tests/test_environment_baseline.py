"""MATH-002 environment smoke tests; these validate tool availability, not product behavior."""
import sqlite3

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_fastapi_test_client_round_trip() -> None:
    app = FastAPI()

    @app.get("/health")
    def health() -> dict[str, bool]:
        return {"ok": True}

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_sqlite_persistence_round_trip() -> None:
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE smoke (id INTEGER PRIMARY KEY, value TEXT NOT NULL)")
    connection.execute("INSERT INTO smoke(value) VALUES (?)", ("ok",))
    connection.commit()

    row = connection.execute("SELECT value FROM smoke WHERE id = 1").fetchone()
    connection.close()

    assert row == ("ok",)
