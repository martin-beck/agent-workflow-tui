import json
from pathlib import Path


def test_lifecycle_contract_is_revision_bound():
    value = json.loads((Path(__file__).parents[1] / "specifications/tui-lifecycle.json").read_text())
    assert value["spec_id"] == "AWT-SPEC-TUI-AR-LIFECYCLE"
    assert "persistence -> coordinator-event" in value["transitions"]
    assert any("revision" in item for item in value["invariants"])

