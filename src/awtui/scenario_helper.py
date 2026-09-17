"""Zero-argument interactive launcher for generated TUI scenarios."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from .live import build_application


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


def run_interactive(*, input_fn: Callable[[str], str] = input, output_fn: Callable[[str], None] = print, app_factory=build_application) -> list[str]:
    scenario = choose_scenario(load_scenarios(), input_fn, output_fn)
    events: list[str] = []
    app = app_factory(
        document=f"Scenario: {scenario['title']}\nAR: {scenario['context']['ar_id']} revision {scenario['context']['task_revision']}",
        points=f"Actions available: {', '.join(scenario['actions'])}",
        helper="Use the live footer controls. The session emits revision-bound events.",
        on_event=events.append,
    )
    app.run()
    output_fn("Scenario complete: " + scenario["id"])
    output_fn("Events: " + (" -> ".join(events) or "none"))
    return events


def main() -> int:
    run_interactive()
    return 0
