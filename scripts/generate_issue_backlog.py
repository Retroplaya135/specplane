#!/usr/bin/env python3
"""Generate a CSV backlog from requirements and the validated contract set."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from validate_contracts import load_yaml, validate_contracts

FIELDS = ["task_id", "title", "type", "source", "owner", "risk", "traceability"]


def _append(rows: list[dict[str, str]], task_id: str, title: str, kind: str, source: str, owner: str = "", risk: str = "") -> None:
    rows.append({
        "task_id": task_id,
        "title": title,
        "type": kind,
        "source": source,
        "owner": owner,
        "risk": risk,
        "traceability": task_id,
    })


def _items(path: Path, key: str) -> list[dict[str, Any]]:
    value = load_yaml(path)
    if not isinstance(value, dict) or "__raw__" in value:
        return []
    items = value.get(key, [])
    return [item for item in items if isinstance(item, dict) and isinstance(item.get("id"), str)]


def generate(prd_path: Path, out: Path, root: Path) -> None:
    validate_contracts(root)
    prd = json.loads(prd_path.read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    for item in prd.get("acceptanceCriteria", []):
        _append(rows, item["id"], item["statement"], item.get("testType", "implementation"), "prd:acceptanceCriteria")
    for item in prd.get("edgeCases", []):
        _append(rows, item["id"], item["case"], "edge_case", "prd:edgeCases", risk=item.get("category", ""))
    for item in _items(root / "specs/api/API_SPEC_TEMPLATE.yaml", "endpoints"):
        _append(rows, f"API-{item['id']}", f"Define and verify API contract {item['id']}", "api_contract", "specs/api/API_SPEC_TEMPLATE.yaml", item.get("ownerModule", ""), item.get("riskLevel", ""))
    for item in _items(root / "specs/data/DATA_MODEL_TEMPLATE.yaml", "entities"):
        _append(rows, f"DATA-{item['id']}", f"Define and verify data contract {item['id']}", "data_contract", "specs/data/DATA_MODEL_TEMPLATE.yaml", item.get("ownerModule", ""), item.get("riskLevel", ""))
    for item in _items(root / "specs/tests/TEST_MATRIX_TEMPLATE.yaml", "tests"):
        _append(rows, item["id"], f"Implement test contract {item['id']}", "test_contract", "specs/tests/TEST_MATRIX_TEMPLATE.yaml", item.get("ownerModule", ""), item.get("riskLevel", ""))
    for item in _items(root / "specs/scaffold/FILE_MANIFEST_TEMPLATE.yaml", "files"):
        _append(rows, f"SCAF-{item['id']}", f"Generate scaffold file {item['path']}", "scaffold", "specs/scaffold/FILE_MANIFEST_TEMPLATE.yaml", item.get("ownerModule", ""), item.get("riskLevel", ""))
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prd", default="specs/prd/EXAMPLE_MINIMAL_PRD.json")
    parser.add_argument("--out", default="generated/backlog.csv")
    parser.add_argument("--root", default=".")
    args = parser.parse_args(argv)
    root = Path(args.root)
    generate(root / args.prd, Path(args.out), root)
    print(f"Backlog written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
