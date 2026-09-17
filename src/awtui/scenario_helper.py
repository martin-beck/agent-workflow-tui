"""Zero-argument interactive launcher for generated TUI scenarios."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from .live import build_application, run_application


def load_scenarios(path: Path | None = None) -> list[dict]:
    path = path or Path(__file__).parents[2] / "scenarios/corpus.json"
    return json.loads(path.read_text(encoding="utf-8"))["scenarios"]


def choose_scenario(scenarios: list[dict], input_fn: Callable[[str], str] = input, output_fn: Callable[[str], None] = print) -> dict:
    output_fn("Available TUI scenarios:")
    for index, scenario in enumerate(scenarios, 1):
        output_fn(f"  {index}. {scenario['title']} [{scenario['id']}]")
    while True:
        choice = input_fn("Select a scenario number: ").strip()
        try:
            index = int(choice)
            if 1 <= index <= len(scenarios):
                return scenarios[index - 1]
        except ValueError:
            pass
        output_fn(f"Please enter a number from 1 to {len(scenarios)}.")


def demo_decisions(scenario: dict) -> list[dict]:
    """Create three anchored, synthetic decisions for a scenario demo."""
    title = scenario["title"]
    return [{
        "point_id": f"{scenario['id']}-decision-{index}",
        "anchor": f"{document}:L{index * 10}",
        "question": f"{title}: decision {index}",
        "proposals": [
            {"label": "Conservative", "rationale": "Minimize change", "confidence": .8, "tradeoffs": "slower delivery"},
            {"label": "Expedite", "rationale": "Shorten feedback loop", "confidence": .6, "tradeoffs": "higher review load"},
        ],
        "helper": "Synthetic downstream impact for live demonstration.",
        "implications": "Review the highlighted document anchor before deciding.",
        "evidence_gap": "Demo evidence is intentionally synthetic.",
    } for index, document in enumerate(("design", "workplan", "design"), 1)]


def run_interactive(*, input_fn: Callable[[str], str] = input, output_fn: Callable[[str], None] = print, app_factory=build_application) -> list[str]:
    scenario = choose_scenario(load_scenarios(), input_fn, output_fn)
    events: list[str] = []
    app = app_factory(
        document=f"Scenario: {scenario['title']}\nAR: {scenario['context']['ar_id']} revision {scenario['context']['task_revision']}",
        design_document=f"DESIGN DOCUMENT\nScenario: {scenario['title']}\nHighlighted anchors: design:L10, design:L30",
        workplan=f"WORKPLAN\nScenario: {scenario['title']}\nHighlighted anchors: workplan:L20",
        decisions=demo_decisions(scenario),
        points=f"Actions available: {', '.join(scenario['actions'])}",
        helper="Use the live footer controls. The session emits revision-bound events.",
        on_event=events.append,
    )
    run_application(app, output_fn=output_fn)
    output_fn("Scenario complete: " + scenario["id"])
    output_fn("Events: " + (" -> ".join(events) or "none"))
    return events


def main() -> int:
    run_interactive()
    return 0
