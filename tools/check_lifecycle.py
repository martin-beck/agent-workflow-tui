#!/usr/bin/env python3
"""Fail-closed checker for the public AR/TUI lifecycle contract."""
import json
import sys
from pathlib import Path


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).parents[1] / "specifications/tui-lifecycle.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    required = {"context -> packet-review", "packet-review -> formal-review", "formal-review -> discussion", "discussion -> response", "response -> persistence", "persistence -> coordinator-event", "coordinator-event -> quality-check"}
    if value.get("spec_id") != "AWT-SPEC-TUI-AR-LIFECYCLE" or not required.issubset(value.get("transitions", [])):
        print("AWT-LIFECYCLE-FAIL: incomplete lifecycle", file=sys.stderr)
        return 1
    if not {"context -> discussion", "packet-review -> persistence", "discussion -> reconciled"}.issubset(value.get("forbidden_transitions", [])):
        print("AWT-LIFECYCLE-FAIL: missing forbidden transitions", file=sys.stderr)
        return 1
    if len(value.get("invariants", [])) < 5:
        print("AWT-LIFECYCLE-FAIL: insufficient invariants", file=sys.stderr)
        return 1
    print("AWT-LIFECYCLE-PASS: revision-bound interaction contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
