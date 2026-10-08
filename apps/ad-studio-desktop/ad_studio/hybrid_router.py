"""实拍素材缺口的补拍 / AI补镜头决策。

本模块只负责确定性路由，不直接生成视频、不调用 Provider。
商品事实、商品外观、真实操作、真人口播等证据缺口默认必须补拍；
通用辅助画面在真实视频 Provider 已配置且预算足够时才允许进入 AI 补镜头。
"""

from __future__ import annotations

from typing import Iterable


_PRODUCT_EVIDENCE_TERMS = (
    "商品", "产品", "特写", "细节", "演示", "操作", "使用", "开箱",
    "材质", "接口", "结构", "功能", "外观", "包装", "规格", "参数",
    "实物", "证明", "真人", "口播", "说话", "讲解",
)

_HUMAN_REALITY_TERMS = (
    "真人", "人物出镜", "口播", "说话", "讲解", "采访", "手部操作",
)


def _text(task: dict) -> str:
    return " ".join(
        str(task.get(k, "") or "")
        for k in ("need", "reason", "why", "related_selling_point", "shoot_or_generate")
    ).lower()


def is_product_evidence_gap(task: dict) -> bool:
    """判断缺口是否涉及不能用生成画面冒充的商品/真人事实证据。"""
    text = _text(task)
    return any(term.lower() in text for term in _PRODUCT_EVIDENCE_TERMS)


def is_human_reality_gap(task: dict) -> bool:
    text = _text(task)
    return any(term.lower() in text for term in _HUMAN_REALITY_TERMS)


def route_footage_gap_tasks(
    tasks: Iterable[dict] | None,
    *,
    generation_connected: bool,
    budget_remaining_rmb: float = 0.0,
    cost_per_ai_shot_rmb: float = 0.0,
) -> dict:
    """为每个缺口给出下一步：继续补拍、AI补镜头或人工确认。

    规则：
    1. 商品/真人事实证据永远不允许 AI 补镜头冒充。
    2. 通用视觉缺口只有真实视频 Provider 已配置且预算足够时才允许 AI。
    3. Provider 未配置或预算不足时，不假装能生成，转为需要人工补素材。
    """
    remaining = max(0.0, float(budget_remaining_rmb or 0.0))
    rate = max(0.0, float(cost_per_ai_shot_rmb or 0.0))
    output = []
    counts = {"继续补拍": 0, "AI补镜头": 0, "需要人工确认": 0}
    for raw in tasks or []:
        if not isinstance(raw, dict):
            continue
        task = dict(raw)
        evidence = is_product_evidence_gap(task)
        human = is_human_reality_gap(task)
        if evidence or human:
            task["recommended_resolution"] = "继续补拍"
            task["generation_allowed"] = False
            task["estimated_cost_rmb"] = 0.0
            task["resolution_reason"] = (
                "该缺口涉及商品事实、真实外观/功能/操作或真人表达，"
                "必须保留真实证据，不能用 AI 生成画面冒充。"
            )
            counts["继续补拍"] += 1
        elif generation_connected and (rate <= 0.0 or remaining >= rate):
            task["recommended_resolution"] = "AI补镜头"
            task["generation_allowed"] = True
            task["estimated_cost_rmb"] = round(rate, 4)
            task["resolution_reason"] = (
                "属于通用辅助画面；视频生成 Provider 已配置且当前预算允许，"
                "可以进入 AI 补镜头生产。"
            )
            counts["AI补镜头"] += 1
            remaining = max(0.0, remaining - rate)
        else:
            task["recommended_resolution"] = "需要人工确认"
            task["generation_allowed"] = False
            task["estimated_cost_rmb"] = 0.0
            if not generation_connected:
                task["resolution_reason"] = "当前没有已配置的视频生成 Provider，不能自动进入 AI 补镜头。"
            else:
                task["resolution_reason"] = (
                    f"视频生成 Provider 已配置，但剩余预算 ¥{remaining:.2f} "
                    f"不足预计单镜头 ¥{rate:.2f}，不能自动突破预算。"
                )
            counts["需要人工确认"] += 1
        output.append(task)
    estimated = round(sum(float(x.get("estimated_cost_rmb", 0) or 0) for x in output), 4)
    return {
        "task_count": len(output),
        "tasks": output,
        "counts": counts,
        "generation_connected": bool(generation_connected),
        "budget_remaining_rmb": round(remaining, 4),
        "estimated_additional_cost_rmb": estimated,
        "method": "实拍缺口混合路由：商品/真人证据优先补拍，通用画面按 Provider + 预算进入 AI 补镜头",
    }


def execute_ai_gap_generation(
    tasks: Iterable[dict] | None,
    *,
    generator,
    budget_remaining_rmb: float = 0.0,
    cost_per_ai_shot_rmb: float = 0.0,
) -> dict:
    """在混合路由结果之后执行获准的 AI 补镜头，并再次做预算闸门。

    generator(task) 必须真正完成视频生成并返回生成文件路径；失败时不会把缺口标记为已生成。
    商品/真人证据任务即使被误传进来也会被强制拦截。
    """
    remaining = max(0.0, float(budget_remaining_rmb or 0.0))
    rate = max(0.0, float(cost_per_ai_shot_rmb or 0.0))
    output = []
    generated = 0
    failed = 0
    blocked = 0

    for raw in tasks or []:
        if not isinstance(raw, dict):
            continue
        task = dict(raw)
        if is_product_evidence_gap(task) or is_human_reality_gap(task):
            task["generation_allowed"] = False
            task["status"] = "已拦截：真实证据必须补拍"
            blocked += 1
            output.append(task)
            continue
        if task.get("recommended_resolution") != "AI补镜头" or not task.get("generation_allowed"):
            task["status"] = task.get("status") or "未进入AI生成"
            output.append(task)
            continue
        if rate > 0 and remaining < rate:
            task["generation_allowed"] = False
            task["status"] = "已拦截：预算不足"
            task["resolution_reason"] = (
                f"执行前预算复核失败：剩余 ¥{remaining:.2f}，"
                f"本镜头预计 ¥{rate:.2f}。"
            )
            blocked += 1
            output.append(task)
            continue
        try:
            generated_path = generator(task)
            if not generated_path:
                raise RuntimeError("生成器未返回视频文件路径")
            task["generated_path"] = str(generated_path)
            task["status"] = "AI补镜头已生成，待人工复核"
            task["review_status"] = "待复核"
            task["accepted_into_storyboard"] = False
            task["estimated_cost_rmb"] = rate
            if rate > 0:
                remaining = max(0.0, remaining - rate)
            generated += 1
        except Exception as exc:
            task["status"] = "AI补镜头生成失败"
            task["generation_error"] = str(exc)
            task["accepted_into_storyboard"] = False
            failed += 1
        output.append(task)

    return {
        "task_count": len(output),
        "tasks": output,
        "generated": generated,
        "failed": failed,
        "blocked": blocked,
        "budget_remaining_rmb": round(remaining, 4),
        "estimated_additional_cost_rmb": round(
            generated * rate, 4
        ),
        "method": "执行前二次预算闸门 + 真实证据拦截 + 生成后人工复核",
    }
