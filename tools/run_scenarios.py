#!/usr/bin/env python3
"""Replay synthetic workflows and generate deterministic screenshot artifacts."""
from __future__ import annotations
import argparse
import html
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from awtui.live import dispatch_recorded_input

ROOT = Path(__file__).parents[1]

def screenshot(scenario: dict, events: list[str]) -> str:
    lines = [f"{scenario['title']} ({scenario['id']})", f"AR: {scenario['context']['ar_id']}  revision: {scenario['context']['task_revision']}", "", "INPUT: " + " ".join(scenario["actions"]), "EVENTS: " + (" -> ".join(events) or "none"), "", "Human-in-the-loop decision session complete"]
    text = "\n".join(lines)
    rows = "".join(f'<text x="24" y="{42 + i * 24}">{html.escape(line)}</text>' for i, line in enumerate(lines))
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="240" role="img" aria-label="{html.escape(scenario["title"])}"><rect width="100%" height="100%" fill="#101820"/><g fill="#d7f9ff" font-family="monospace" font-size="16">{rows}</g></svg>\n'

def generate(root: Path = ROOT) -> dict:
    corpus = json.loads((root / "scenarios/corpus.json").read_text(encoding="utf-8"))
    screenshot_dir = root / "docs/screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for scenario in corpus["scenarios"]:
        events: list[str] = []
        dispatch_recorded_input("".join("\n" if a == "enter" else "\x1b" if a == "escape" else a for a in scenario["actions"]), events.append)
        if events != scenario["expected_events"]:
            raise ValueError(f"{scenario['id']}: expected {scenario['expected_events']}, got {events}")
        filename = f"{scenario['id']}.svg"
        (screenshot_dir / filename).write_text(screenshot(scenario, events), encoding="utf-8")
        results.append({"id": scenario["id"], "title": scenario["title"], "events": events, "screenshot": f"docs/screenshots/{filename}"})
    manifest = {"schema_version": 1, "scenario_count": len(results), "results": results}
    (root / "artifacts").mkdir(exist_ok=True)
    (root / "artifacts/scenario-results.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="regenerate in memory and fail if tracked artifacts differ")
    args = parser.parse_args()
    if args.check:
        before = {p: p.read_text(encoding="utf-8") for p in list((ROOT / "docs/screenshots").glob("*.svg")) + [ROOT / "artifacts/scenario-results.json"] if p.exists()}
        generate(ROOT)
        after = {p: p.read_text(encoding="utf-8") for p in before}
        return 0 if before == after else 1
    print(json.dumps(generate(ROOT), indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
