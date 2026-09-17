import json
from pathlib import Path
from tools.run_scenarios import generate


def test_scenario_runner_replays_every_input_and_writes_screenshots(tmp_path):
    root = Path(__file__).parents[1]
    result = generate(root)
    assert result["scenario_count"] == 15
    assert all((root / item["screenshot"]).is_file() for item in result["results"])
    assert json.loads((root / "artifacts/scenario-results.json").read_text())["scenario_count"] == 15
