#!/usr/bin/env python3
"""Check generated scenario documentation and screenshot artifacts."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCREENSHOT_LINK = re.compile(r"^- \*\*Screenshot:\*\* \[open terminal capture\]\(([^)]+)\)$", re.MULTILINE)
SCENARIO_ID = re.compile(r"^- \*\*Scenario ID:\*\* `([^`]+)`$", re.MULTILINE)


def check(root: Path = ROOT) -> list[str]:
    corpus = json.loads((root / "scenarios/corpus.json").read_text(encoding="utf-8"))
    results = json.loads((root / "artifacts/scenario-results.json").read_text(encoding="utf-8"))
    docs_path = root / "docs/SCENARIOS.md"
    docs = docs_path.read_text(encoding="utf-8")
    expected_ids = [item["id"] for item in corpus["scenarios"]]
    result_by_id = {item["id"]: item for item in results.get("results", [])}
    errors: list[str] = []
    doc_ids = SCENARIO_ID.findall(docs)
    if doc_ids != expected_ids:
        errors.append("SCENARIOS.md scenario order/IDs do not match corpus")
    links = SCREENSHOT_LINK.findall(docs)
    expected_links = [f"screenshots/{item['id']}.svg" for item in corpus["scenarios"]]
    if links != expected_links:
        errors.append("SCENARIOS.md screenshot links do not match scenario IDs")
    if len(links) != len(expected_ids):
        errors.append("SCENARIOS.md does not contain exactly one screenshot per scenario")
    expected_files = {root / "docs" / link for link in expected_links}
    actual_files = set((root / "docs/screenshots").glob("*.svg"))
    if actual_files != expected_files:
        errors.append("docs/screenshots contains stale or missing SVG artifacts")
    for scenario_id, result in result_by_id.items():
        expected = root / result["screenshot"]
        if expected not in expected_files or not expected.is_file():
            errors.append(f"{scenario_id}: result screenshot is missing")
    if set(result_by_id) != set(expected_ids):
        errors.append("scenario-results IDs do not match corpus")
    if "../docs/" in docs or "file://" in docs:
        errors.append("SCENARIOS.md contains an invalid or non-portable link")
    return errors


if __name__ == "__main__":
    problems = check(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT)
    if problems:
        print("\n".join(problems), file=sys.stderr)
        raise SystemExit(1)
    print("scenario documentation and artifacts valid")
