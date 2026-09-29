#!/usr/bin/env python3
"""
Disaster recovery data importer for ecommerce-agent.

Usage:
  python restore_database.py --dsn "postgresql://USER:PASSWORD@HOST:5432/postgres" --backup-dir ../

Requires: psycopg (psycopg3)

This program intentionally contains no credentials.
Schema must be restored first from database-schema.json and the
project migration/schema materials. It then imports all JSON table
snapshots under database-data/.
"""

import argparse
import json
from pathlib import Path
import psycopg
from psycopg import sql

def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dsn", required=True)
    ap.add_argument("--backup-dir", default="..")
    args = ap.parse_args()

    root = Path(args.backup_dir).resolve()
    data_dir = root / "database-data"
    if not data_dir.exists():
        raise SystemExit(f"database-data not found: {data_dir}")

    files = sorted(data_dir.glob("*.json"))
    if not files:
        raise SystemExit("No database-data/*.json files found.")

    with psycopg.connect(args.dsn) as conn:
        with conn.cursor() as cur:
            for path in files:
                payload = load_json(path)
                table = payload["table"]
                if not table.startswith("public."):
                    raise SystemExit(f"Refusing non-public table: {table}")

                schema, name = table.split(".", 1)
                rows = payload.get("rows", [])
                expected = payload.get("row_count", len(rows))
                if expected != len(rows):
                    raise SystemExit(f"{table}: row_count mismatch in backup file")

                if not rows:
                    continue

                columns = list(rows[0].keys())
                statement = sql.SQL(
                    "INSERT INTO {}.{} ({}) VALUES ({}) ON CONFLICT DO NOTHING"
                ).format(
                    sql.Identifier(schema),
                    sql.Identifier(name),
                    sql.SQL(",").join(map(sql.Identifier, columns)),
                    sql.SQL(",").join(sql.Placeholder() for _ in columns),
                )

                values = [[row.get(c) for c in columns] for row in rows]
                cur.executemany(statement, values)
                print(f"restored {table}: {len(rows)} rows")

        conn.commit()

    print("Data restore finished. Run restore_checklist.md before production use.")

if __name__ == "__main__":
    main()
