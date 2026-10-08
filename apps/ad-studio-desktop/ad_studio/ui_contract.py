"""桌面端 UI 操作契约检查。

目的：避免后端代码已经实现，但用户在界面上找不到/点不到对应操作。
该检查不替代人工视觉验收；它保证关键用户操作至少存在真实按钮绑定。
"""
from __future__ import annotations

import ast
from pathlib import Path


class UIContractError(RuntimeError):
    pass


def _button_commands(app_source: str) -> set[str]:
    tree = ast.parse(app_source)
    commands: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "Button":
            for kw in node.keywords:
                if kw.arg != "command":
                    continue
                value = kw.value
                if isinstance(value, ast.Name):
                    commands.add(value.id)
                elif isinstance(value, ast.Attribute):
                    commands.add(value.attr)
                elif isinstance(value, ast.Lambda):
                    commands.add("<lambda>")
    return commands


def verify_ui_action_contract(app_file: Path, required_actions: tuple[str, ...] | None = None) -> dict:
    """检查关键用户操作是否真实绑定到 Tkinter Button。

    这是 AI 执行前的硬闸门：失败时必须先修 UI，不能只修后端。
    """
    source = Path(app_file).read_text(encoding="utf-8")
    tree = ast.parse(source)
    methods = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    commands = _button_commands(source)
    required = required_actions or (
        "create", "load_project", "save", "generate_shot", "regen_shot",
        "postprocess_selected", "final_render", "model_settings",
        "system_status", "usage_view", "video_provider_settings",
        "asset_generation_settings", "footage_analysis_report",
        "footage_gap_tasks_report", "reanalyze_footage",
        "footage_reanalysis_history_report",
    )
    missing_methods = sorted(set(required) - methods)
    unbound = sorted(set(required) - commands)
    if missing_methods or unbound:
        raise UIContractError(
            "UI 操作契约失败："
            f"缺少方法={missing_methods or '无'}；"
            f"未绑定按钮={unbound or '无'}。"
            "必须先修复界面入口，不能仅认为后端代码完成。"
        )
    return {
        "ok": True,
        "required_actions": list(required),
        "button_bindings": sorted(commands),
        "method_count": len(methods),
        "method": "Tkinter Button command AST contract",
    }
