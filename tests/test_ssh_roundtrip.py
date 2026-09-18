import json
from pathlib import Path

import pytest

from awtui import bridge
from tools import run_ssh_roundtrip


def test_roundtrip_harness_projects_a_revision_bound_response(monkeypatch):
    remote: dict[str, object] = {}

    def fake_run(command, *, input_text=None):
        del input_text
        if command[0] == "scp":
            source = Path(command[-2])
            remote[command[-1].split(":", 1)[1]] = json.loads(source.read_text(encoding="utf-8"))
            return ""
        if command[0] == "ssh" and "cat" in command:
            return json.dumps(remote[command[-1]])
        return ""

    monkeypatch.setattr(run_ssh_roundtrip, "_run", fake_run)
    result = run_ssh_roundtrip.run_roundtrip(
        host="ci-alias", port=22222, user="awui-ci", identity="/tmp/key",
        remote_dir="/tmp/awui-roundtrip", insecure=True,
    )
    assert result["status"] == "resolved"
    response = next(value for key, value in remote.items() if key.endswith("response.json"))
    assert response["ar_update"]["decision_status"] == "resolved"
    assert response["ar_update"]["specification_update"]["selected_candidate"] == "candidate-a"


@pytest.mark.parametrize("value", ("relative/path", "/tmp/bad path", "/tmp/x;touch-pwned"))
def test_roundtrip_harness_rejects_unsafe_remote_paths(value):
    with pytest.raises(ValueError, match="absolute"):
        run_ssh_roundtrip._remote_path(value)


def test_roundtrip_response_projection_keeps_revision_and_identity():
    request = {
        "kind": "coordinator-tui-request", "project_id": "p", "session_id": "AWTUI-TEST",
        "ar": {"ar_id": "AR-0001", "task_revision": 2},
        "interaction": {"decision_request_ref": "AWG-TEST"},
    }
    event = {"session_id": "AWTUI-TEST", "sequence": 1, "event_type": "select", "payload": {"disposition": "select"}}
    response = bridge.tui_to_coordinator_response(request, event)
    assert response["ar_id"] == "AR-0001"
    assert response["task_revision"] == 2
