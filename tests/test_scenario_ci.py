from pathlib import Path


def test_ci_replays_and_checks_generated_artifacts():
    workflow = (Path(__file__).parents[1] / ".github/workflows/scenarios.yml").read_text(encoding="utf-8")
    for command in ("validate_scenarios.py", "run_scenarios.py", "generate_scenario_docs.py", "git diff --exit-code"):
        assert command in workflow
