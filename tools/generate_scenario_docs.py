#!/usr/bin/env python3
"""Generate accessible Markdown workflows from corpus and replay results.

Recordings use the asciinema v2 cast format.  ``run_scenarios.py`` captures
the rendered prompt-toolkit terminal stream directly, so generation remains
deterministic in CI even when the optional ``asciinema`` executable is not
installed; the resulting ``.cast`` files can be opened by asciinema-player or
uploaded with ``asciinema upload``.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]

def generate(root: Path = ROOT) -> str:
    corpus = json.loads((root / "scenarios/corpus.json").read_text(encoding="utf-8"))
    results = json.loads((root / "artifacts/scenario-results.json").read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in results["results"]}
    scenario_ids = [item["id"] for item in corpus["scenarios"]]
    if set(by_id) != set(scenario_ids):
        missing = sorted(set(scenario_ids) - set(by_id))
        extra = sorted(set(by_id) - set(scenario_ids))
        raise ValueError(f"scenario results do not match corpus (missing={missing}, extra={extra})")
    if results.get("scenario_count") != len(scenario_ids):
        raise ValueError("scenario result count does not match corpus")
    lines = ["# TUI scenario workflows", "", "These workflows are generated from `scenarios/corpus.json` and replayed through the actual prompt-toolkit TUI. Each case has a deterministic SVG pane snapshot, an asciinema v2 terminal animation, and an explicit event trace.", "", "Play a recording locally with `asciinema play docs/recordings/<scenario-id>.cast`.", "", f"**Generated scenarios:** {len(corpus['scenarios'])}", ""]
    for scenario in corpus["scenarios"]:
        result = by_id[scenario["id"]]
        screenshot = Path(result["screenshot"])
        if screenshot.parts[:1] != ("docs",) or screenshot.parts[1:2] != ("screenshots",):
            raise ValueError(f"{scenario['id']}: screenshot must be under docs/screenshots")
        screenshot_link = screenshot.relative_to("docs").as_posix()
        recording = Path(result.get("recording", ""))
        if recording.parts[:2] != ("docs", "recordings") or recording.suffix != ".cast":
            raise ValueError(f"{scenario['id']}: recording must be under docs/recordings")
        recording_link = recording.relative_to("docs").as_posix()
        lines.extend([f"## {scenario['title']}", "", f"- **Scenario ID:** `{scenario['id']}`", f"- **AR context:** `{scenario['context']['ar_id']}` revision `{scenario['context']['task_revision']}`", f"- **Input actions:** `{', '.join(scenario['actions'])}`", f"- **Emitted events:** `{', '.join(result['events']) or 'none'}`", f"- **Screenshot:** [open terminal capture]({screenshot_link})", f"- **Live recording:** [play asciinema recording]({recording_link})", "", "This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.", ""])
    output = "\n".join(lines)
    (root / "docs/SCENARIOS.md").write_text(output, encoding="utf-8")
    return output

if __name__ == "__main__":
    generate()
