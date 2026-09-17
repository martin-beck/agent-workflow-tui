from awtui.journal import resume, save
from awtui.reconciliation import Reconciliation


def test_recovery_rejects_stale_resume_and_requires_targeted_reopen(tmp_path):
    path = tmp_path / "journal.json"
    session = {"project_id": "p", "ar_id": "AR-17", "task_revision": 1, "packet_digest": "d", "responses": {}, "unresolved": ["p1"], "future_requests": []}
    save(path, session)
    try:
        resume(path, project_id="p", ar_id="AR-17", task_revision=2, packet_digest="d")
    except ValueError as exc:
        assert "stale" in str(exc)
    else:
        raise AssertionError("stale resume accepted")
    assert Reconciliation("AR-17", 1, ("AR-18",), ("conflict",), "discussion-required").event_type() == "reopen"
