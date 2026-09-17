#!/usr/bin/env python3
"""Generate accessible Markdown workflows from corpus and replay results."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]

def generate(root: Path = ROOT) -> str:
    corpus = json.loads((root / "scenarios/corpus.json").read_text(encoding="utf-8"))
    results = json.loads((root / "artifacts/scenario-results.json").read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in results["results"]}
    lines = ["# TUI scenario workflows", "", "These workflows are generated from `scenarios/corpus.json` and replayed through the live control mapping. Each case has a deterministic SVG screenshot and an explicit event trace.", "", f"**Generated scenarios:** {len(corpus['scenarios'])}", ""]
    for scenario in corpus["scenarios"]:
        result = by_id[scenario["id"]]
        lines.extend([f"## {scenario['title']}", "", f"- **Scenario ID:** `{scenario['id']}`", f"- **AR context:** `{scenario['context']['ar_id']}` revision `{scenario['context']['task_revision']}`", f"- **Input actions:** `{', '.join(scenario['actions'])}`", f"- **Emitted events:** `{', '.join(result['events']) or 'none'}`", f"- **Screenshot:** [open terminal capture](../{result['screenshot']})", "", "This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.", ""])
    output = "\n".join(lines)
    (root / "docs/SCENARIOS.md").write_text(output, encoding="utf-8")
    return output

if __name__ == "__main__":
    generate()
