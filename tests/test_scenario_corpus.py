from pathlib import Path
from tools.validate_scenarios import validate


def test_synthetic_corpus_covers_at_least_fifteen_valid_workflows():
    path = Path(__file__).parents[1] / "scenarios/corpus.json"
    assert validate(path) == []
