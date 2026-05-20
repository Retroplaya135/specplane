from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, f"scripts/{name}", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class ToolkitTests(unittest.TestCase):
    def test_example_requirements_validate(self) -> None:
        result = run_script("validate_prd.py", "--prd", "specs/prd/EXAMPLE_MINIMAL_PRD.json", "--schema", "specs/prd/PRD_SCHEMA.json")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_invalid_requirements_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            invalid = Path(tmp) / "invalid.json"
            invalid.write_text(json.dumps({"prdVersion": "0.1.0"}), encoding="utf-8")
            result = run_script("validate_prd.py", "--prd", str(invalid), "--schema", "specs/prd/PRD_SCHEMA.json")
        self.assertNotEqual(result.returncode, 0)

    def test_contract_chain_validates(self) -> None:
        result = run_script("validate_contracts.py")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_scaffold_is_traceable_and_write_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "skeleton"
            result = run_script("scaffold_from_prd.py", "--prd", "specs/prd/EXAMPLE_MINIMAL_PRD.json", "--out", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            target = out / "README.md"
            original = target.read_text(encoding="utf-8")
            target.write_text("preserve me\n", encoding="utf-8")
            again = run_script("scaffold_from_prd.py", "--prd", "specs/prd/EXAMPLE_MINIMAL_PRD.json", "--out", str(out))
            self.assertEqual(again.returncode, 0, again.stderr)
            self.assertNotEqual(original, "preserve me\n")
            self.assertEqual(target.read_text(encoding="utf-8"), "preserve me\n")
            trace = run_script("check_spec_traceability.py", "--root", str(out))
            self.assertEqual(trace.returncode, 0, trace.stderr)

    def test_traceability_rejects_unlinked_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "packages/domain/src/example.ts"
            target.parent.mkdir(parents=True)
            target.write_text("export const value = 1;\n", encoding="utf-8")
            result = run_script("check_spec_traceability.py", "--root", tmp)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("example.ts", result.stderr)

    def test_backlog_contains_requirements_contracts_and_scaffolds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "backlog.csv"
            result = run_script("generate_issue_backlog.py", "--out", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            with out.open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
        kinds = {row["type"] for row in rows}
        self.assertTrue({"api_contract", "data_contract", "test_contract", "scaffold"}.issubset(kinds))
        self.assertIn("AC-001", {row["task_id"] for row in rows})


if __name__ == "__main__":
    unittest.main()
