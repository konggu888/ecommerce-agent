"""CI guardrails for the fixed math-tutor plan and visible progress figures."""
import json
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
REGISTER_PATH = PROJECT / "docs" / "MATH_TASK_REGISTER.json"
DASHBOARD_PATH = PROJECT / "docs" / "PROGRESS_DASHBOARD.md"


def test_task_register_fixed_scope_and_weights():
    register = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))
    tasks = register["tasks"]

    assert register["fixed_task_count"] == 32
    assert len(tasks) == 32
    assert [task["id"] for task in tasks] == [
        f"MATH-{number:03d}" for number in range(1, 33)
    ]
    assert sum(task["weight_percent"] for task in tasks) == 100
    assert register["total_weight_percent"] == 100


def test_only_accepted_tasks_count_toward_weighted_progress():
    register = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))
    tasks = register["tasks"]
    accepted = [task for task in tasks if task["status"] == "ACCEPTED"]
    accepted_weight = sum(task["weight_percent"] for task in accepted)
    accepted_count = len(accepted)

    assert all(task.get("acceptance_evidence") for task in accepted)
    assert register["last_verified_snapshot"]["accepted_count"] == accepted_count
    assert (
        register["last_verified_snapshot"]["weighted_completion_percent"]
        == accepted_weight
    )


def test_dashboard_progress_matches_machine_readable_register():
    register = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))
    dashboard = DASHBOARD_PATH.read_text(encoding="utf-8")
    tasks = register["tasks"]
    accepted = [task for task in tasks if task["status"] == "ACCEPTED"]
    accepted_weight = sum(task["weight_percent"] for task in accepted)

    assert re.search(rf"任务总数：{len(tasks)}\b", dashboard)
    assert re.search(rf"已验收：{len(accepted)}/{len(tasks)}\b", dashboard)
    assert re.search(rf"加权完成率：{accepted_weight}%\b", dashboard)
