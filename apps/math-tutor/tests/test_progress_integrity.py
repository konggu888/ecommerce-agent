"""CI guardrails for the fixed math-tutor plan and visible progress figures."""
import json
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
REGISTER_PATH = PROJECT / "docs" / "MATH_TASK_REGISTER.json"
DASHBOARD_PATH = PROJECT / "docs" / "PROGRESS_DASHBOARD.md"
sys.path.insert(0, str(PROJECT / "scripts"))
from update_progress import calculate


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
    assert re.search(rf"加权完成率：{accepted_weight}%", dashboard)


def test_calculator_recomputes_weighted_progress_from_task_states():
    register = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))
    tasks = register["tasks"]
    tasks[0]["status"] = "ACCEPTED"
    tasks[0]["acceptance_evidence"] = [{"type": "test", "detail": "synthetic unit-test evidence"}]

    result = calculate(register)

    assert result["task_count"] == 32
    assert result["total_weight_percent"] == 100
    assert result["accepted_count"] == 1
    assert result["weighted_completion_percent"] == tasks[0]["weight_percent"]


def test_calculator_rejects_accepted_task_without_evidence():
    register = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))
    register["tasks"][0]["status"] = "ACCEPTED"
    register["tasks"][0]["acceptance_evidence"] = []

    try:
        calculate(register)
    except ValueError as error:
        assert "without acceptance evidence" in str(error)
    else:
        raise AssertionError("Calculator must reject ACCEPTED tasks without evidence")


def test_calculated_snapshot_fields_match_task_register():
    register = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))
    progress = calculate(register)
    snapshot = register["last_verified_snapshot"]

    assert snapshot["calculated_task_count"] == progress["task_count"]
    assert snapshot["calculated_total_weight_percent"] == progress["total_weight_percent"]
    assert snapshot["status_counts"] == progress["status_counts"]
