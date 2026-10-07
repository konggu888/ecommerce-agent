#!/usr/bin/env python3
"""Enforce documentation synchronization for AI 商品广告工厂 desktop changes."""

from __future__ import annotations
import argparse
import subprocess

REQUIRED = {
    "help": "apps/ad-studio-desktop/HELP.md",
    "logic": "apps/ad-studio-desktop/PROJECT_LOGIC.md",
}
CODE_PREFIX = "apps/ad-studio-desktop/"
DOC_EXTENSIONS = (".md", ".txt")

def git_files(base: str, head: str) -> list[str]:
    p = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        text=True, capture_output=True, check=True,
    )
    return [x.strip() for x in p.stdout.splitlines() if x.strip()]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="HEAD~1")
    ap.add_argument("--head", default="HEAD")
    args = ap.parse_args()

    files = git_files(args.base, args.head)
    desktop_code = [
        f for f in files
        if f.startswith(CODE_PREFIX) and not f.endswith(DOC_EXTENSIONS)
    ]
    if not desktop_code:
        print("DOC-SYNC: no desktop code change detected; OK")
        return 0

    missing = [path for path in REQUIRED.values() if path not in files]
    if missing:
        print("DOC-SYNC: FAILED")
        print("Desktop code changed, but required documentation was not changed:")
        for path in missing:
            print(f"  - {path}")
        print("Every AI/code change must update HELP.md and PROJECT_LOGIC.md in the same change.")
        return 1

    print("DOC-SYNC: OK")
    for f in desktop_code:
        print(f"  - {f}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
