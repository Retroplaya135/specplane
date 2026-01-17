#!/usr/bin/env python3
"""Generate declared directories and traceable placeholders after validation."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from validate_contracts import ContractError, load_yaml, validate_contracts


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "item"


def _pascal(value: str) -> str:
    return "".join(part.title() for part in re.split(r"[_-]+", value) if part)


def _write_once(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    path.write_text(content, encoding="utf-8")


def _traceability(path: str, refs: list[str]) -> str:
    joined = ", ".join(refs) if refs else "spec:unknown"
    if Path(path).suffix in {".ts", ".tsx", ".js", ".jsx"}:
        return f"// Traceability: {joined}\n"
    if Path(path).suffix == ".sql":
        return f"-- Traceability: {joined}\n"
    return f"Traceability: {joined}\n\n"


def _file_content(entry: dict[str, Any], product: str) -> str:
    path = entry["path"]
    refs = entry.get("traceability") or entry.get("sourceRefs") or []
    if isinstance(refs, str):
        refs = [refs]
    purpose = entry.get("purpose") or entry.get("kind") or "scaffold placeholder"
    trace = _traceability(path, list(refs))
    if path.endswith(".md"):
        title = Path(path).stem.replace("-", " ").replace("_", " ").title()
        return f"# {title}\n\n{trace}Generated for {product}. {purpose}. Business logic is intentionally absent.\n"
    if path.endswith((".ts", ".tsx")):
        return f"{trace}// Purpose: {purpose}\n// Business logic requires an approved feature contract.\nexport {{}};\n"
    if path.endswith(".sql"):
        return f"{trace}-- Purpose: {purpose}\n-- A reviewed data contract and tests are required before implementation.\n"
    return f"{trace}Generated for {product}. {purpose}.\n"


def generate(prd_path: Path, manifest_path: Path, out: Path, root: Path) -> None:
    validate_contracts(root)
    prd = json.loads(prd_path.read_text(encoding="utf-8"))
    manifest = load_yaml(manifest_path)
    if not isinstance(manifest, dict) or "__raw__" in manifest:
        raise ContractError("Scaffold generation requires PyYAML and a mapping file manifest.")

    out.mkdir(parents=True, exist_ok=True)
    for entry in manifest.get("directories", []):
        if isinstance(entry, dict) and isinstance(entry.get("path"), str):
            (out / entry["path"]).mkdir(parents=True, exist_ok=True)

    product = prd["product"]["name"]
    _write_once(out / "README.md", f"# {product} Implementation Skeleton\n\nTraceability: prd:product\n\nGenerated from {prd_path}. Business logic is intentionally absent.\n")
    _write_once(out / "TRACEABILITY.md", "# Traceability Matrix\n\nTraceability: prd:acceptanceCriteria, specs/tests\n\nEvery implementation file must link to an approved contract.\n")

    for entry in manifest.get("files", []):
        if isinstance(entry, dict) and isinstance(entry.get("path"), str):
            _write_once(out / entry["path"], _file_content(entry, product))

    for obj in prd.get("dataObjects", []):
        name = _slug(obj["name"]).replace("-", "_")
        _write_once(
            out / f"packages/domain/src/{name}.ts",
            f"// Traceability: dataObject {obj['id']}\nexport interface {_pascal(name)} {{\n  id: string;\n}}\n",
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prd", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--file-manifest", default="specs/scaffold/FILE_MANIFEST_TEMPLATE.yaml")
    args = parser.parse_args(argv)
    root = Path(args.root)
    try:
        generate(root / args.prd, root / args.file_manifest, Path(args.out), root)
    except Exception as exc:
        print(f"Scaffold generation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Skeleton generated at {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
