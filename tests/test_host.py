import os

import pytest

from awtui.host import (
    attach_session,
    append_event,
    detect_launch_mode,
    handoff_message,
    launch_argv,
    write_session_file,
)


def request():
    return {"schema_version": "1.0", "kind": "coordinator-tui-request", "project_id": "demo",
            "session_id": "s-1", "ar": {"ar_id": "AR-0005", "task_revision": 3, "status": "open",
            "description": "d", "specification": {}}, "interaction": {"interaction_required": True,
            "decision_request_ref": "AWG-1", "decision_status": "pending", "trigger": "decision"},
            "guidance_request": {"schema_version": "0.2", "request_id": "AWG-1", "context": {},
            "formal_check": {}, "candidates": []}}


def test_mode_detection_is_deterministic_and_bounded():
    assert detect_launch_mode(environ={"TMUX": "1"}, stdin_tty=False, stdout_tty=False) == "tmux"
    assert detect_launch_mode(environ={}, stdin_tty=True, stdout_tty=True) == "tty"
    assert detect_launch_mode(environ={"AWTUI_LAUNCH_MODE": "inline"}, stdin_tty=False, stdout_tty=False) == "inline"
    assert detect_launch_mode(environ={}, stdin_tty=False, stdout_tty=False) == "manual"
    assert launch_argv("manual", "/tmp/x") is None
    assert launch_argv("tmux", "/tmp/x")[:2] == ["tmux", "new-window"]
    assert "HUMAN DECISION REQUIRED" in handoff_message("manual", "/tmp/x", summary="2 decisions")
    assert "awtui-live --session-file /tmp/x" in handoff_message(
        "manual", "/tmp/x", summary="2 decisions"
    )


def test_private_session_file_can_be_attached(tmp_path):
    path = write_session_file(request(), tmp_path)
    if os.name != "nt":
        assert os.stat(path).st_mode & 0o077 == 0
    assert attach_session(path)["session_id"] == "s-1"


def test_session_file_is_not_overwritten_or_attached_if_public(tmp_path):
    path = write_session_file(request(), tmp_path)
    with pytest.raises(FileExistsError):
        write_session_file(request(), tmp_path)
    path.chmod(0o644)
    with pytest.raises(ValueError, match="accessible"):
        attach_session(path)


def test_unsafe_request_is_rejected(tmp_path):
    bad = request()
    bad["session_id"] = "../escape"
    with pytest.raises(ValueError, match="filename"):
        write_session_file(bad, tmp_path)


def test_event_journal_is_private_bounded_and_append_only(tmp_path):
    path = tmp_path / "session.events.jsonl"
    append_event(path, {"session_id": "s-1", "sequence": 1, "event_type": "select"})
    append_event(path, {"session_id": "s-1", "sequence": 2, "event_type": "reconciled"})
    assert path.read_text().count("session_id") == 2
    if os.name != "nt":
        assert os.stat(path).st_mode & 0o077 == 0
