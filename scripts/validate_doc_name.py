#!/usr/bin/env python3
"""Validate the mandatory Spec-Driven SaaS document filename format."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


class DocNameError(ValueError):
    """Raised when a document filename violates the required convention."""


FILENAME_RE = re.compile(
    r"^(?P<prefix>[a-z0-9][a-z0-9_-]*)_"
    r"(?P<doc_type>[a-z][a-z0-9-]*)_"
    r"(?P<date>\d{2}-\d{2}-\d{4})_"
    r"(?P<hour>0[1-9]|1[0-2])_"
    r"(?P<ampm>AM|PM)_"
    r"v(?P<version>[1-9]\d*)_"
    r"s(?P<stage>\d+)_"
    r"p(?P<phase>\d+)_"
    r"st(?P<step>\d+)_"
    r"itr(?P<iteration>\d+)\.md$"
)


@dataclass(frozen=True)
class ParsedDocName:
    project_name: str
    doc_name: str
    doc_type: str
    date: str
    hour: int
    ampm: str
    version: int
    stage: int
    phase: int
    step: int
    iteration: int


def _split_prefix(prefix: str, project_name: str | None) -> tuple[str, str]:
    if project_name:
        expected = f"{project_name}_"
        if not prefix.startswith(expected):
            raise DocNameError(f"prefix must start with project name '{project_name}_'")
        doc_name = prefix[len(expected) :]
        if not doc_name:
            raise DocNameError("doc_name is empty")
        return project_name, doc_name

    parts = prefix.split("_", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise DocNameError("filename prefix must include project_name and doc_name")
    return parts[0], parts[1]


def parse_doc_name(path_or_name: str | Path, project_name: str | None = None) -> ParsedDocName:
    name = Path(path_or_name).name
    match = FILENAME_RE.match(name)
    if not match:
        raise DocNameError(
            "filename must match "
            "<project_name>_<doc_name>_<doc_type>_<dd-mm-yyyy>_<hour>_<AM/PM>_"
            "v<version>_s<stage>_p<phase>_st<step>_itr<iteration>.md"
        )

    groups = match.groupdict()
    try:
        datetime.strptime(groups["date"], "%d-%m-%Y")
    except ValueError as exc:
        raise DocNameError(f"invalid date '{groups['date']}'") from exc

    parsed_project, doc_name = _split_prefix(groups["prefix"], project_name)
    return ParsedDocName(
        project_name=parsed_project,
        doc_name=doc_name,
        doc_type=groups["doc_type"],
        date=groups["date"],
        hour=int(groups["hour"]),
        ampm=groups["ampm"],
        version=int(groups["version"]),
        stage=int(groups["stage"]),
        phase=int(groups["phase"]),
        step=int(groups["step"]),
        iteration=int(groups["iteration"]),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", help="Markdown filenames or paths to validate.")
    parser.add_argument("--project-name", help="Optional project name used to disambiguate doc_name parsing.")
    parser.add_argument("--json", action="store_true", help="Emit parsed filename metadata as JSON.")
    args = parser.parse_args(argv)

    parsed: list[ParsedDocName] = []
    errors: list[str] = []
    for path in args.paths:
        try:
            parsed.append(parse_doc_name(path, project_name=args.project_name))
        except DocNameError as exc:
            errors.append(f"{path}: {exc}")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps([asdict(item) for item in parsed], indent=2))
    else:
        for path in args.paths:
            print(f"Document filename validated: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
