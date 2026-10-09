"""Workflow-mode policy primitives for the desktop production pipeline.

This module defines the permission/confirmation contract only. It does not claim
that a complete mode-selection UI or every workflow pause point is integrated.
"""
from __future__ import annotations

from dataclasses import dataclass


AUTO = "ai_auto"
SEMI_AUTO = "ai_semi_auto"
USER_CONTROLLED = "user_controlled_ai_assisted"
WORKFLOW_MODES = (AUTO, SEMI_AUTO, USER_CONTROLLED)

# Actions that must never silently cross an explicit user-consent boundary.
ALWAYS_CONFIRM = frozenset({
    "cloud_generation",
    "budget_overrun",
    "publish_or_real_platform_write",
    "delete_original_asset",
})

# Actions where semi-automatic mode asks the user to approve the plan first.
SEMI_CONFIRM = frozenset({
    "approve_creative_plan",
    "approve_storyboard",
    "final_delivery",
    "generate_all_variants",
})

# In user-controlled mode, AI may recommend but cannot decide these actions.
USER_DECISION = frozenset({
    "choose_creative_plan",
    "choose_shots",
    "approve_storyboard",
    "final_delivery",
    "generate_all_variants",
})


@dataclass(frozen=True)
class ModeDecision:
    mode: str
    action: str
    allowed: bool
    requires_confirmation: bool
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "action": self.action,
            "allowed": self.allowed,
            "requires_confirmation": self.requires_confirmation,
            "reason": self.reason,
        }


def normalize_mode(mode: str | None) -> str:
    """Unknown or missing values fail safe to semi-automatic mode."""
    candidate = str(mode or "").strip()
    return candidate if candidate in WORKFLOW_MODES else SEMI_AUTO


def decide_action(mode: str | None, action: str, *, user_approved: bool = False) -> ModeDecision:
    """Return whether an action may proceed under the selected operating mode.

    Explicit consent gates apply in all modes. AI-generated shots still need the
    separate storyboard review enforced by the production safety gate.
    """
    selected = normalize_mode(mode)
    name = str(action or "").strip()
    if name in ALWAYS_CONFIRM and not user_approved:
        return ModeDecision(selected, name, False, True,
                            "该操作需要用户明确确认，工作模式不能绕过授权边界。")
    if selected == USER_CONTROLLED and name in USER_DECISION and not user_approved:
        return ModeDecision(selected, name, False, True,
                            "当前为用户控制模式，AI只能提出建议，需用户确认后执行。")
    if selected == SEMI_AUTO and name in SEMI_CONFIRM and not user_approved:
        return ModeDecision(selected, name, False, True,
                            "当前为半自动模式，需在关键节点由用户确认后继续。")
    return ModeDecision(selected, name, True, False,
                        "允许执行；仍须遵守独立的事实、安全、预算和镜头复核闸门。")


def preserve_workflow_state(previous_plan: dict[str, object], next_plan: dict[str, object]) -> dict[str, object]:
    """Carry project-wide mode and per-variant approvals across plan activation."""
    for key in ("workflow_mode", "workflow_approvals"):
        if key in previous_plan:
            next_plan[key] = previous_plan[key]
    return next_plan


def set_project_workflow_mode(project, mode: str) -> str:
    """Persist the mode in the project's existing creative_plan payload."""
    selected = normalize_mode(mode)
    if not isinstance(project.creative_plan, dict):
        project.creative_plan = {}
    project.creative_plan["workflow_mode"] = selected
    return selected


def get_project_workflow_mode(project) -> str:
    plan = getattr(project, "creative_plan", None)
    if not isinstance(plan, dict):
        return SEMI_AUTO
    return normalize_mode(plan.get("workflow_mode"))
