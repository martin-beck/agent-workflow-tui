#!/usr/bin/env python3
"""Replay synthetic workflows and generate deterministic screenshot artifacts."""
from __future__ import annotations
import argparse
import html
import json
import re
import sys
from pathlib import Path
ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from awtui.live import dispatch_recorded_input
from tools.validate_scenarios import validate

_ACTION_KEYS = {
    "enter": "\n",
    "escape": "\x1b",
    "r": "r",
    "c": "c",
    "m": "m",
    "a": "a",
    "s": "s",
    "o": "o",
    "q": "q",
}
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

def screenshot(scenario: dict, events: list[str]) -> str:
    title = f"{scenario['title']} ({scenario['id']})"
    event_trace = " -> ".join(events) or "none"
    lines = [title, f"AR: {scenario['context']['ar_id']}  revision: {scenario['context']['task_revision']}", "", "INPUT: " + " ".join(scenario["actions"]), "EVENTS: " + event_trace, "", "Human-in-the-loop decision session complete"]
    text = "\n".join(lines)
    rows = "".join(f'<text x="24" y="{42 + i * 24}">{html.escape(line)}</text>' for i, line in enumerate(lines))
    description = f"Synthetic TUI workflow. Input actions: {' '.join(scenario['actions'])}. Emitted events: {event_trace}."
    # Keep the SVG useful to screen readers as well as visual documentation.
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="240" '
        f'role="img" aria-labelledby="title-{html.escape(scenario["id"])} desc-{html.escape(scenario["id"])}">'
        f'<title id="title-{html.escape(scenario["id"])}">{html.escape(title)}</title>'
        f'<desc id="desc-{html.escape(scenario["id"])}">{html.escape(description)}</desc>'
        '<rect width="100%" height="100%" fill="#101820"/>'
        f'<g fill="#d7f9ff" font-family="monospace" font-size="16">{rows}</g></svg>\n'
    )


def _encoded_input(actions: list[str]) -> str:
    """Encode corpus action names into the exact keys used by live replay."""
    try:
        return "".join(_ACTION_KEYS[action] for action in actions)
    except KeyError as error:
        raise ValueError(f"unknown scenario action: {error.args[0]}") from error


def _artifacts(root: Path = ROOT) -> dict[Path, str]:
    corpus_path = root / "scenarios/corpus.json"
    problems = validate(corpus_path)
    if problems:
        raise ValueError("invalid scenario corpus:\n" + "\n".join(problems))
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    results = []
    screenshots = {}
    for scenario in corpus["scenarios"]:
        scenario_id = scenario["id"]
        if not _SAFE_ID.fullmatch(scenario_id):
            raise ValueError(f"unsafe scenario id for artifact path: {scenario_id!r}")
        events: list[str] = []
        dispatch_recorded_input(_encoded_input(scenario["actions"]), events.append)
        if events != scenario["expected_events"]:
            raise ValueError(f"{scenario_id}: expected {scenario['expected_events']}, got {events}")
        filename = f"{scenario_id}.svg"
        screenshots[Path("docs/screenshots") / filename] = screenshot(scenario, events)
        results.append({"id": scenario_id, "title": scenario["title"], "events": events, "screenshot": f"docs/screenshots/{filename}"})
    manifest = {"schema_version": 1, "scenario_count": len(results), "results": results}
    artifacts = dict(screenshots)
    artifacts[Path("artifacts/scenario-results.json")] = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    return artifacts


def _current_artifacts(root: Path) -> dict[Path, str]:
    paths = list((root / "docs/screenshots").glob("*.svg")) + [root / "artifacts/scenario-results.json"]
    return {path.relative_to(root): path.read_text(encoding="utf-8") for path in paths if path.exists()}

def generate(root: Path = ROOT) -> dict:
    artifacts = _artifacts(root)
    screenshot_dir = root / "docs/screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    artifact_dir = root / "artifacts"
    artifact_dir.mkdir(exist_ok=True)
    expected_paths = set(artifacts)
    # Remove only stale generated screenshots after all replay checks pass.
    for path in screenshot_dir.glob("*.svg"):
        if path.relative_to(root) not in expected_paths:
            path.unlink()
    for relative, content in artifacts.items():
        target = root / relative
        temporary = target.with_name(target.name + ".tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(target)
    return json.loads(artifacts[Path("artifacts/scenario-results.json")])

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="regenerate in memory and fail if tracked artifacts differ")
    args = parser.parse_args()
    if args.check:
        expected = _artifacts(ROOT)
        return 0 if _current_artifacts(ROOT) == expected else 1
    print(json.dumps(generate(ROOT), indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
