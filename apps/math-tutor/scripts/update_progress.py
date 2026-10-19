"""Calculate and validate the fixed math-tutor progress snapshot.

Run `python apps/math-tutor/scripts/update_progress.py --write` after changing
task statuses/evidence. CI runs `--check` so stale progress numbers cannot pass.
Only ACCEPTED tasks with non-empty acceptance evidence count toward weighted
software completion; CI success and documentation work do not count by themselves.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
REGISTER_PATH = PROJECT / "docs" / "MATH_TASK_REGISTER.json"
DASHBOARD_PATH = PROJECT / "docs" / "PROGRESS_DASHBOARD.md"
EXPECTED_TASK_COUNT = 32
EXPECTED_WEIGHT = 100


def calculate(register: dict) -> dict:
    tasks = register.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("Task register must contain a tasks list")
    ids = [task.get("id") for task in tasks]
    expected_ids = [f"MATH-{n:03d}" for n in range(1, EXPECTED_TASK_COUNT + 1)]
    if ids != expected_ids:
        raise ValueError(f"Task IDs must remain the fixed sequence MATH-001..MATH-032; got {ids}")
    total_weight = sum(task.get("weight_percent", 0) for task in tasks)
    if len(tasks) != EXPECTED_TASK_COUNT or total_weight != EXPECTED_WEIGHT:
        raise ValueError(f"Fixed plan must be {EXPECTED_TASK_COUNT} tasks / {EXPECTED_WEIGHT}% weight; got {len(tasks)} / {total_weight}%")
    accepted = [task for task in tasks if task.get("status") == "ACCEPTED"]
    for task in accepted:
        if not task.get("acceptance_evidence"):
            raise ValueError(f"{task['id']} is ACCEPTED without acceptance evidence")
    counts = {}
    for task in tasks:
        status = task.get("status", "UNKNOWN")
        counts[status] = counts.get(status, 0) + 1
    accepted_weight = sum(task["weight_percent"] for task in accepted)
    return {
        "task_count": len(tasks),
        "total_weight_percent": total_weight,
        "accepted_count": len(accepted),
        "weighted_completion_percent": accepted_weight,
        "status_counts": counts,
    }


def update_dashboard(text: str, progress: dict) -> str:
    replacements = {
        r"(?m)^- 任务总数：.*$": f"- 任务总数：{progress['task_count']}。",
        r"(?m)^- 已验收：.*$": f"- 已验收：{progress['accepted_count']}/{progress['task_count']}。",
        r"(?m)^- 加权完成率：.*$": f"- 加权完成率：{progress['weighted_completion_percent']}%。",
    }
    for pattern, replacement in replacements.items():
        text, count = re.subn(pattern, replacement, text, count=1)
        if count != 1:
            raise ValueError(f"Dashboard must contain exactly one canonical progress line matching {pattern}")
    return text


def synchronize(write: bool) -> int:
    register_text = REGISTER_PATH.read_text(encoding="utf-8")
    dashboard_text = DASHBOARD_PATH.read_text(encoding="utf-8")
    register = json.loads(register_text)
    progress = calculate(register)
    snapshot = register.setdefault("last_verified_snapshot", {})
    expected_snapshot = {
        "accepted_count": progress["accepted_count"],
        "weighted_completion_percent": progress["weighted_completion_percent"],
        "calculated_task_count": progress["task_count"],
        "calculated_total_weight_percent": progress["total_weight_percent"],
        "status_counts": progress["status_counts"],
        "progress_calculated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    snapshot_mismatch = any(snapshot.get(k) != v for k, v in expected_snapshot.items() if k != "progress_calculated_at_utc")
    updated_dashboard = update_dashboard(dashboard_text, progress)
    dashboard_mismatch = updated_dashboard != dashboard_text

    if write:
        snapshot.update(expected_snapshot)
        REGISTER_PATH.write_text(json.dumps(register, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        DASHBOARD_PATH.write_text(updated_dashboard, encoding="utf-8")
        print(f"Updated progress: {progress['accepted_count']}/{progress['task_count']} accepted; weighted completion {progress['weighted_completion_percent']}%.")
        print(f"Status counts: {json.dumps(progress['status_counts'], ensure_ascii=False, sort_keys=True)}")
        return 0

    if snapshot_mismatch or dashboard_mismatch:
        print("Progress snapshot/dashboard is stale. Run: python apps/math-tutor/scripts/update_progress.py --write")
        print(f"Calculated: {progress['accepted_count']}/{progress['task_count']} accepted; weighted completion {progress['weighted_completion_percent']}%.")
        print(f"Status counts: {json.dumps(progress['status_counts'], ensure_ascii=False, sort_keys=True)}")
        return 1
    print(f"Progress consistent: {progress['accepted_count']}/{progress['task_count']} accepted; weighted completion {progress['weighted_completion_percent']}%.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="Recalculate and write the JSON snapshot and dashboard numbers")
    mode.add_argument("--check", action="store_true", help="Check calculated progress matches the stored snapshot and dashboard")
    args = parser.parse_args()
    raise SystemExit(synchronize(write=args.write))
