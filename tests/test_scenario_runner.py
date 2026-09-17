import json
from pathlib import Path
import shutil
import pytest
from tools.run_scenarios import _artifacts, _current_artifacts, generate, screenshot


def test_scenario_runner_replays_every_input_and_writes_screenshots(tmp_path):
    root = Path(__file__).parents[1]
    result = generate(root)
    expected_count = len(json.loads((root / "scenarios/corpus.json").read_text())["scenarios"])
    assert result["scenario_count"] == expected_count
    assert all((root / item["screenshot"]).is_file() for item in result["results"])
    assert json.loads((root / "artifacts/scenario-results.json").read_text())["scenario_count"] == expected_count


def test_screenshot_has_accessible_deterministic_metadata():
    scenario = {
        "id": "accessible-case",
        "title": "Accessible case",
        "context": {"ar_id": "AR-1", "task_revision": 1},
        "actions": ["enter"],
    }
    value = screenshot(scenario, ["select"])
    assert '<title id="title-accessible-case">Accessible case (accessible-case)</title>' in value
    assert '<desc id="desc-accessible-case">' in value
    assert 'aria-labelledby="title-accessible-case desc-accessible-case"' in value


def test_artifact_check_detects_missing_and_extra_screenshots(tmp_path):
    root = tmp_path / "repo"
    (root / "scenarios").mkdir(parents=True)
    shutil.copy(Path(__file__).parents[1] / "scenarios/corpus.json", root / "scenarios/corpus.json")
    generate(root)
    expected = _artifacts(root)
    screenshot_path = root / "docs/screenshots/basic-select.svg"
    screenshot_path.unlink()
    assert _current_artifacts(root) != expected
    screenshot_path.write_text(expected[Path("docs/screenshots/basic-select.svg")], encoding="utf-8")
    (root / "docs/screenshots/stale.svg").write_text("stale\n", encoding="utf-8")
    assert _current_artifacts(root) != expected


def test_runner_rejects_invalid_corpus_before_writing_outputs(tmp_path):
    root = tmp_path / "repo"
    (root / "scenarios").mkdir(parents=True)
    corpus = json.loads((Path(__file__).parents[1] / "scenarios/corpus.json").read_text(encoding="utf-8"))
    corpus["scenarios"][0]["actions"] = ["not-a-key"]
    (root / "scenarios/corpus.json").write_text(json.dumps(corpus), encoding="utf-8")
    with pytest.raises(ValueError, match="invalid scenario corpus"):
        generate(root)
    assert not (root / "docs").exists()


def test_runner_rejects_unsafe_scenario_id_before_writing_outputs(tmp_path):
    root = tmp_path / "repo"
    (root / "scenarios").mkdir(parents=True)
    corpus = json.loads((Path(__file__).parents[1] / "scenarios/corpus.json").read_text(encoding="utf-8"))
    corpus["scenarios"][0]["id"] = "../outside"
    (root / "scenarios/corpus.json").write_text(json.dumps(corpus), encoding="utf-8")
    with pytest.raises(ValueError, match="unsafe scenario id"):
        generate(root)
    assert not (root / "docs").exists()
