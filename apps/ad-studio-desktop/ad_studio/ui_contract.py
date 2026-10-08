"""桌面端 UI 操作契约检查。

目的：避免后端代码已经实现，但用户在界面上找不到/点不到对应操作。
该检查不替代人工视觉验收；它保证关键用户操作至少存在真实按钮绑定。
"""
from __future__ import annotations

import ast
from pathlib import Path


class UIContractError(RuntimeError):
    pass


def ui_action(func):
    """标记一个用户可执行功能；被标记的方法必须拥有真实 UI 入口。"""
    setattr(func, "__ui_action__", True)
    return func


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
    if required_actions is not None:
        required = tuple(required_actions)
    else:
        required = tuple(sorted(
            node.name for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and any(isinstance(d, ast.Name) and d.id == "ui_action" for d in node.decorator_list)
        ))
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
