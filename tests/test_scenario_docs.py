from pathlib import Path
from tools.generate_scenario_docs import generate
from tools.check_scenario_docs import check


def test_generated_docs_cover_every_scenario_and_screenshot():
    root = Path(__file__).parents[1]
    text = generate(root)
    assert text.count("## ") == 15
    assert "open terminal capture" in text
    assert "privacy-safe" in text
    assert "(screenshots/basic-select.svg)" in text
    assert check(root) == []
