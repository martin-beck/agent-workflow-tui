#!/usr/bin/env python3
"""Fail-closed checker for the revision-bound transport atomicity contract."""
from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    path = Path(__file__).parents[1] / "specifications/tui-transport-atomicity.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "Boundary validation occurs before delivery or persistence.",
        "A rejected delivery leaves the next sequence unchanged.",
        "A persistence exception leaves the next sequence unchanged.",
        "A successful delivery or persistence advances the sequence exactly once.",
    }
    if (
        value.get("spec_id") != "AWT-SPEC-TUI-TRANSPORT-ATOMICITY"
        or value.get("version") != 1
        or not required.issubset(value.get("invariants", []))
    ):
        raise SystemExit("AWT-TRANSPORT-FAIL: incomplete atomicity contract")
    print("AWT-TRANSPORT-PASS: rejected events are non-mutating")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
