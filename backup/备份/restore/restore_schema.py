#!/usr/bin/env python3
"""
Rebuilds the custom public schema from backup/备份/database-schema.json.

It is intentionally conservative:
- only public schema objects are rebuilt;
- managed Supabase auth/storage schemas are not overwritten;
- existing objects are skipped where possible;
- constraints, indexes and policies are applied after tables exist.

Requires: psycopg (psycopg3)
"""

import argparse
import json
from pathlib import Path
import psycopg
from psycopg import sql

def ident_table(schema, name):
    return sql.SQL("{}.{}").format(sql.Identifier(schema), sql.Identifier(name))

def column_type(c):
    dtype = c.get("udt_name") or c.get("data_type") or "text"
    if dtype in ("varchar", "character varying") and c.get("character_maximum_length"):
        return sql.SQL("{}({})").format(sql.SQL("varchar"), sql.Literal(c["character_maximum_length"]))
    if dtype in ("numeric", "decimal"):
        p, s = c.get("numeric_precision"), c.get("numeric_scale")
        if p is not None and s is not None:
            return sql.SQL("numeric({}, {})").format(sql.Literal(p), sql.Literal(s))
        if p is not None:
            return sql.SQL("numeric({})").format(sql.Literal(p))
    if dtype == "USER-DEFINED":
        return sql.SQL(c.get("udt_name", "text"))
    return sql.SQL(dtype)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dsn", required=True)
    ap.add_argument("--schema-file", default="../database-schema.json")
    args = ap.parse_args()

    snap = json.loads(Path(args.schema_file).read_text(encoding="utf-8"))
    s = snap.get("snapshot", snap)
    columns = s.get("columns", [])
    constraints = s.get("constraints", [])
    indexes = s.get("indexes", [])
    policies = s.get("policies", [])
    rls = s.get("rls", [])

    tables = {}
    for c in columns:
        if c.get("table_schema") != "public":
            continue
        tables.setdefault(c["table_name"], []).append(c)

    with psycopg.connect(args.dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS public")

            for name, cols in sorted(tables.items()):
                defs = []
                for c in sorted(cols, key=lambda x: x.get("ordinal_position", 0)):
                    d = sql.SQL("{} {}").format(
                        sql.Identifier(c["column_name"]),
                        column_type(c)
                    )
                    default = c.get("column_default")
                    if default:
                        d += sql.SQL(" DEFAULT ") + sql.SQL(default)
                    if c.get("is_nullable") == "NO":
                        d += sql.SQL(" NOT NULL")
                    defs.append(d)

                stmt = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
                    ident_table("public", name),
                    sql.SQL(", ").join(defs)
                )
                cur.execute(stmt)
                print("table:", name)

            for c in constraints:
                if c.get("schema") not in (None, "public") and c.get("table_schema") not in (None, "public"):
                    continue
                table = c.get("table") or c.get("table_name")
                definition = c.get("definition")
                name = c.get("name")
                if not table or not definition or not name:
                    continue
                try:
                    cur.execute(
                        sql.SQL("ALTER TABLE {} ADD CONSTRAINT {} {}").format(
                            ident_table("public", table),
                            sql.Identifier(name),
                            sql.SQL(definition)
                        )
                    )
                except psycopg.errors.DuplicateObject:
                    conn.rollback()
                except psycopg.errors.DuplicateTable:
                    conn.rollback()
                except Exception as e:
                    conn.rollback()
                    print("constraint skipped:", name, str(e))

            for i in indexes:
                definition = i.get("definition")
                if not definition or i.get("schema") != "public":
                    continue
                try:
                    cur.execute(sql.SQL(definition))
                except psycopg.errors.DuplicateObject:
                    conn.rollback()
                except Exception as e:
                    conn.rollback()
                    print("index skipped:", i.get("name"), str(e))

            for item in rls:
                table = item.get("table") or item.get("table_name")
                enabled = item.get("rls_enabled")
                if table and enabled is not None:
                    try:
                        cur.execute(sql.SQL("ALTER TABLE {} {} ROW LEVEL SECURITY").format(
                            ident_table("public", table),
                            sql.SQL("ENABLE" if enabled else "DISABLE")
                        ))
                    except Exception as e:
                        conn.rollback()
                        print("RLS skipped:", table, str(e))

            for p in policies:
                table = p.get("table") or p.get("table_name")
                name = p.get("name") or p.get("policy_name")
                using = p.get("using")
                check = p.get("check")
                command = p.get("command") or p.get("cmd") or "r"
                roles = p.get("roles") or ["public"]
                if not table or not name:
                    continue
                cmdmap = {"r":"SELECT","a":"INSERT","w":"UPDATE","d":"DELETE","*":"ALL",
                          "SELECT":"SELECT","INSERT":"INSERT","UPDATE":"UPDATE","DELETE":"DELETE","ALL":"ALL"}
                ccmd = cmdmap.get(command, command)
                try:
                    pieces = [
                        sql.SQL("CREATE POLICY {} ON {}").format(
                            sql.Identifier(name), ident_table("public", table)
                        ),
                        sql.SQL("FOR ") + sql.SQL(ccmd),
                        sql.SQL("TO ") + sql.SQL(", ").join(sql.Identifier(r) for r in roles)
                    ]
                    if using:
                        pieces.append(sql.SQL("USING ({})").format(sql.SQL(using)))
                    if check:
                        pieces.append(sql.SQL("WITH CHECK ({})").format(sql.SQL(check)))
                    cur.execute(sql.SQL(" ").join(pieces))
                except psycopg.errors.DuplicateObject:
                    conn.rollback()
                except Exception as e:
                    conn.rollback()
                    print("policy skipped:", name, str(e))

        conn.commit()

    print("Schema rebuild attempt finished. Run restore_checklist.md.")

if __name__ == "__main__":
    main()
