#!/usr/bin/env python3
"""Check implementation-looking files for explicit spec traceability."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

WATCH_EXTS = {".ts", ".tsx", ".js", ".jsx", ".sql"}
WATCH_ROOTS = {"apps", "packages", "database", "tests"}
IGNORE_DIRS = {".git", ".next", "node_modules", ".claude", ".codex", "templates", "__pycache__"}
TRACE_RE = re.compile(r"traceability\s*:\s*(prd|specs?|dataObject|userFlow|feature|api|ui|state|test)", re.IGNORECASE)


def implementation_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in WATCH_EXTS:
            continue
        rel_parts = path.relative_to(root).parts
        if any(part in IGNORE_DIRS for part in rel_parts):
            continue
        if path.name == "next-env.d.ts":
            continue
        if rel_parts and rel_parts[0] not in WATCH_ROOTS:
            continue
        files.append(path)
    return files


def check_traceability(root: Path) -> list[str]:
    violations: list[str] = []
    for path in implementation_files(root):
        text = path.read_text(errors="ignore", encoding="utf-8")[:3000]
        if not TRACE_RE.search(text):
            violations.append(str(path))
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args(argv)

    violations = check_traceability(Path(args.root))
    if violations:
        print("Files missing traceability marker:", file=sys.stderr)
        for violation in violations:
            print(f"- {violation}", file=sys.stderr)
        return 1

    print("Traceability check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
