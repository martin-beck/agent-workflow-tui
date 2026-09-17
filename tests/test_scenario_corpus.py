from pathlib import Path
from tools.validate_scenarios import validate


def test_synthetic_corpus_covers_at_least_fifteen_valid_workflows():
    path = Path(__file__).parents[1] / "scenarios/corpus.json"
    assert validate(path) == []


def test_corpus_covers_every_live_control():
    from awtui.live import RECORDED_CONTROLS
    import json
    data = json.loads((Path(__file__).parents[1] / "scenarios/corpus.json").read_text())
    covered = {event for scenario in data["scenarios"] for event in scenario["expected_events"]}
    assert set(RECORDED_CONTROLS.values()) <= covered
