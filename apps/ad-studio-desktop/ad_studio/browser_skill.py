from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any


def _find_agent_browser() -> str | None:
    configured = os.environ.get("AD_STUDIO_BROWSER_SKILL", "").strip()
    if configured:
        return configured
    return shutil.which("agent-browser")


def _run(command: list[str], timeout: int) -> str:
    proc = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "agent-browser执行失败").strip())
    return proc.stdout.strip()


def _extract_json(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    try:
        value = json.loads(raw)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass
    for line in reversed(raw.splitlines()):
        try:
            value = json.loads(line.strip())
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise RuntimeError("浏览器Skill没有返回可解析的商品JSON")


def fetch_with_browser_skill(url: str, timeout: int = 20) -> dict[str, Any]:
    binary = _find_agent_browser()
    if not binary:
        return {
            "ok": False,
            "error": "未检测到 agent-browser。桌面版可配置 AD_STUDIO_BROWSER_SKILL 指向浏览器Skill命令。"
        }

    session = "adstudio-product-parser"
    _run([binary, "--session", session, "open", url], timeout)
    _run([binary, "--session", session, "wait", "--load", "networkidle"], timeout)

    script = r'''
JSON.stringify((() => {
  const meta = (name) => document.querySelector('meta[property="' + name + '"]')?.content
    || document.querySelector('meta[name="' + name + '"]')?.content || "";
  const text = document.body?.innerText || "";
  const priceNode = document.querySelector(
    '[class*="price"], [id*="price"], [data-price], meta[property="product:price:amount"]'
  );
  return {
    name: meta("og:title") || meta("twitter:title") || document.title || "",
    description: meta("og:description") || meta("description") || text.slice(0, 3000),
    price: meta("product:price:amount") || meta("price") || priceNode?.textContent?.trim() || "",
    images: Array.from(document.images).map(i => i.currentSrc || i.src).filter(Boolean).slice(0, 20)
  };
})())
'''
    raw = _run([binary, "--session", session, "eval", "--stdin"], timeout)
    result = _extract_json(raw)
    result["ok"] = True
    return result
