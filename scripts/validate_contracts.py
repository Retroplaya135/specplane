#!/usr/bin/env python3
"""Validate the contract templates that authorize scaffold generation."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from validate_prd import ValidationError as PrdValidationError
from validate_prd import validate_prd

try:
    import yaml
except Exception:  # pragma: no cover - fallback for dependency-light smoke checks
    yaml = None


class ContractError(ValueError):
    """Raised when the contract chain is missing or malformed."""


TEMPLATE_PATHS = {
    "prd": "specs/prd/EXAMPLE_MINIMAL_PRD.json",
    "prd_schema": "specs/prd/PRD_SCHEMA.json",
    "feature": "specs/features/FEATURE_SPEC_TEMPLATE.md",
    "flows": "specs/flows/USER_FLOWS_TEMPLATE.yaml",
    "data": "specs/data/DATA_MODEL_TEMPLATE.yaml",
    "roles": "specs/roles/RBAC_RLS_TEMPLATE.yaml",
    "authorization": "specs/security/AUTHORIZATION_MATRIX_TEMPLATE.yaml",
    "data_classification": "specs/security/DATA_CLASSIFICATION_TEMPLATE.yaml",
    "api": "specs/api/API_SPEC_TEMPLATE.yaml",
    "ui": "specs/ui/COMPONENT_TREE_TEMPLATE.yaml",
    "state": "specs/state/STATE_FLOW_TEMPLATE.yaml",
    "auth": "specs/auth/AUTH_FLOW_TEMPLATE.yaml",
    "billing": "specs/billing/BILLING_FLOW_TEMPLATE.yaml",
    "tests": "specs/tests/TEST_MATRIX_TEMPLATE.yaml",
    "edge_cases": "specs/edge_cases/EDGE_CASE_REGISTER.yaml",
    "scaffold_plan": "specs/scaffold/SCAFFOLD_PLAN_TEMPLATE.yaml",
    "file_manifest": "specs/scaffold/FILE_MANIFEST_TEMPLATE.yaml",
    "module_boundaries": "specs/scaffold/MODULE_BOUNDARIES_TEMPLATE.yaml",
    "module_registry": "manifests/module_registry.yaml",
    "tech_stack": "manifests/tech_stack.yaml",
    "quality_gates": "manifests/quality_gates.yaml",
}

REQUIRED_KEYS = {
    "flows": ["version", "flows", "rules"],
    "data": ["version", "entities", "rules"],
    "roles": ["version", "roles", "rlsPolicies", "rules"],
    "authorization": ["version", "permissions", "rules"],
    "data_classification": ["version", "classifications", "entityMappings", "rules"],
    "api": ["version", "endpoints", "schemas", "rules"],
    "ui": ["version", "routes", "components", "rules"],
    "state": ["version", "flows", "rules"],
    "auth": ["version", "flows", "rules"],
    "billing": ["version", "flows", "idempotency", "rules"],
    "tests": ["version", "tests", "rules"],
    "edge_cases": ["version", "edgeCases", "rules"],
    "scaffold_plan": ["version", "plan", "validation"],
    "file_manifest": ["version", "directories", "files", "rules"],
    "module_boundaries": ["version", "modules", "rules"],
    "module_registry": ["version", "modules"],
    "tech_stack": ["version"],
    "quality_gates": ["version", "gates", "budgets"],
}


def _read(path: Path) -> str:
    if not path.is_file():
        raise ContractError(f"Missing contract file: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ContractError(f"Empty contract file: {path}")
    return text


def load_yaml(path: Path) -> Any:
    text = _read(path)
    if yaml is None:
        return {"__raw__": text}
    try:
        return yaml.safe_load(text)
    except Exception as exc:
        raise ContractError(f"Invalid YAML in {path}: {exc}") from exc


def _has_key(value: Any, key: str) -> bool:
    if isinstance(value, dict) and "__raw__" not in value:
        return key in value
    raw = value.get("__raw__", "") if isinstance(value, dict) else str(value)
    return re.search(rf"^{re.escape(key)}\s*:", raw, flags=re.MULTILINE) is not None


def _ids(value: Any) -> list[str]:
    found: list[str] = []

    def walk(item: Any) -> None:
        if isinstance(item, dict):
            if isinstance(item.get("id"), str):
                found.append(item["id"])
            for nested in item.values():
                walk(nested)
        elif isinstance(item, list):
            for nested in item:
                walk(nested)

    if isinstance(value, dict) and "__raw__" not in value:
        walk(value)
        return found
    raw = value.get("__raw__", "") if isinstance(value, dict) else str(value)
    return re.findall(r"^\s*(?:-\s+)?id:\s*([A-Za-z0-9_.:-]+)", raw, flags=re.MULTILINE)


def _source_ref_count(value: Any) -> int:
    if isinstance(value, dict) and "__raw__" not in value:
        count = 0

        def walk(item: Any) -> None:
            nonlocal count
            if isinstance(item, dict):
                if "sourceRefs" in item or "traceability" in item:
                    count += 1
                for nested in item.values():
                    walk(nested)
            elif isinstance(item, list):
                for nested in item:
                    walk(nested)

        walk(value)
        return count
    raw = value.get("__raw__", "") if isinstance(value, dict) else str(value)
    return len(re.findall(r"^\s*(sourceRefs|traceability)\s*:", raw, flags=re.MULTILINE))


def _validate_feature(path: Path) -> None:
    text = _read(path)
    required = [
        "Feature ID",
        "Linked PRD requirements",
        "Owner module",
        "Risk level",
        "Files allowed for implementation",
        "Files forbidden for implementation",
        "Deferred cases",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    if missing:
        raise ContractError(f"{path}: missing required sections: {missing}")


def _validate_yaml(name: str, path: Path) -> None:
    value = load_yaml(path)
    missing = [key for key in REQUIRED_KEYS[name] if not _has_key(value, key)]
    if missing:
        raise ContractError(f"{path}: missing required top-level keys: {missing}")
    if name not in {"module_registry", "tech_stack", "quality_gates"}:
        if not _ids(value):
            raise ContractError(f"{path}: no stable IDs found")
        if _source_ref_count(value) == 0:
            raise ContractError(f"{path}: no sourceRefs or traceability markers found")
    if name == "file_manifest" and isinstance(value, dict) and "__raw__" not in value:
        for entry in value.get("files", []):
            required = {"path", "ownerModule", "traceability", "allowedChange"}
            missing_fields = sorted(required - set(entry))
            if missing_fields:
                raise ContractError(f"{path}: file entry missing {missing_fields}: {entry}")


def validate_contracts(root: Path = Path(".")) -> None:
    paths = {name: root / relative for name, relative in TEMPLATE_PATHS.items()}
    try:
        validate_prd(paths["prd"], paths["prd_schema"])
    except PrdValidationError as exc:
        raise ContractError(str(exc)) from exc
    _validate_feature(paths["feature"])
    for name in REQUIRED_KEYS:
        _validate_yaml(name, paths[name])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repository root containing specs/, manifests/, and templates/.")
    args = parser.parse_args(argv)
    try:
        validate_contracts(Path(args.root))
    except ContractError as exc:
        print(f"Contract validation failed: {exc}", file=sys.stderr)
        return 1
    print("Contract chain validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
