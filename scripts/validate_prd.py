#!/usr/bin/env python3
"""Validate a SaaS PRD against the repository PRD contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import jsonschema
except Exception:  # pragma: no cover - exercised in environments without deps
    jsonschema = None


class ValidationError(ValueError):
    """Raised when PRD validation fails."""


def _load_json(path: Path) -> Any:
    if not path.exists():
        raise ValidationError(f"File not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON in {path}: {exc}") from exc


def _fallback_validate(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Small schema subset for local smoke checks when jsonschema is absent."""

    errors: list[str] = []
    expected_type = schema.get("type")

    if expected_type == "object":
        if not isinstance(instance, dict):
            return [f"{path}: expected object"]
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required field '{key}'")
        properties = schema.get("properties", {})
        for key, subschema in properties.items():
            if key in instance:
                errors.extend(_fallback_validate(instance[key], subschema, f"{path}.{key}"))
    elif expected_type == "array":
        if not isinstance(instance, list):
            return [f"{path}: expected array"]
        min_items = schema.get("minItems")
        if min_items is not None and len(instance) < min_items:
            errors.append(f"{path}: expected at least {min_items} item(s)")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                errors.extend(_fallback_validate(item, _resolve_ref(item_schema, schema), f"{path}[{index}]"))
    elif expected_type == "string" and not isinstance(instance, str):
        errors.append(f"{path}: expected string")

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: expected one of {schema['enum']}, got {instance!r}")

    return errors


def _resolve_ref(schema: dict[str, Any], root_schema: dict[str, Any]) -> dict[str, Any]:
    ref = schema.get("$ref")
    if not ref:
        return schema
    prefix = "#/$defs/"
    if ref.startswith(prefix):
        return root_schema.get("$defs", {}).get(ref.removeprefix(prefix), schema)
    return schema


def _validate_with_fallback(prd: dict[str, Any], schema: dict[str, Any]) -> None:
    errors = _fallback_validate(prd, schema)
    if errors:
        raise ValidationError("; ".join(errors))


def validate_prd(prd_path: Path, schema_path: Path) -> None:
    prd = _load_json(prd_path)
    schema = _load_json(schema_path)

    if not isinstance(prd, dict):
        raise ValidationError("PRD root must be a JSON object")
    if not isinstance(schema, dict):
        raise ValidationError("PRD schema root must be a JSON object")

    if jsonschema:
        validator_cls = jsonschema.validators.validator_for(schema)
        validator_cls.check_schema(schema)
        validator = validator_cls(schema)
        errors = sorted(validator.iter_errors(prd), key=lambda error: list(error.path))
        if errors:
            formatted = []
            for error in errors:
                location = "$" + "".join(f".{part}" for part in error.path)
                formatted.append(f"{location}: {error.message}")
            raise ValidationError("; ".join(formatted))
    else:
        _validate_with_fallback(prd, schema)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prd", default="specs/prd/product.prd.json")
    parser.add_argument("--schema", default="specs/prd/PRD_SCHEMA.json")
    args = parser.parse_args(argv)

    try:
        validate_prd(Path(args.prd), Path(args.schema))
    except ValidationError as exc:
        print(f"PRD validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"PRD validated: {args.prd}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
