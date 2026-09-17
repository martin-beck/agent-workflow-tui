import json
import subprocess
import sys
from pathlib import Path


def test_lifecycle_contract_is_revision_bound():
    value = json.loads((Path(__file__).parents[1] / "specifications/tui-lifecycle.json").read_text())
    assert value["spec_id"] == "AWT-SPEC-TUI-AR-LIFECYCLE"
    assert "persistence -> coordinator-event" in value["transitions"]
    assert any("revision" in item for item in value["invariants"])


def test_lifecycle_checker_passes():
    root = Path(__file__).parents[1]
    result = subprocess.run([sys.executable, str(root / "tools/check_lifecycle.py")], cwd=root)
    assert result.returncode == 0


def test_lifecycle_checker_rejects_skipped_gate(tmp_path):
    root = Path(__file__).parents[1]
    value = json.loads((root / "specifications/tui-lifecycle.json").read_text())
    value["transitions"].remove("formal-review -> discussion")
    fixture = tmp_path / "invalid.json"
    fixture.write_text(json.dumps(value))
    result = subprocess.run([sys.executable, str(root / "tools/check_lifecycle.py"), str(fixture)], cwd=root)
    assert result.returncode != 0
