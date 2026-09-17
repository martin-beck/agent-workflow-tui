#!/usr/bin/env python3
"""Validate the deterministic synthetic TUI scenario corpus."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ALLOWED = {"enter", "r", "c", "m", "a", "s", "o", "q", "escape"}

def validate(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    scenarios = data.get("scenarios", [])
    errors = []
    if data.get("schema_version") != 1 or len(scenarios) < 15:
        errors.append("corpus must be schema version 1 with at least 15 scenarios")
    ids = [item.get("id") for item in scenarios]
    if len(ids) != len(set(ids)):
        errors.append("scenario ids must be unique")
    for item in scenarios:
        if not item.get("id") or not item.get("title") or not item.get("actions"):
            errors.append(f"incomplete scenario: {item.get('id')}")
        if any(action not in ALLOWED for action in item.get("actions", [])):
            errors.append(f"unknown action: {item.get('id')}")
        context = item.get("context", {})
        for key in ("project_id", "ar_id", "task_revision", "packet_digest", "session_id"):
            if key not in context:
                errors.append(f"{item.get('id')} missing context {key}")
    return errors

if __name__ == "__main__":
    problems = validate(Path(sys.argv[1] if len(sys.argv) > 1 else "scenarios/corpus.json"))
    if problems:
        print("\n".join(problems), file=sys.stderr)
        raise SystemExit(1)
    print("scenario corpus valid")
