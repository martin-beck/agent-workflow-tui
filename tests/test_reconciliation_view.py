from awtui.reconciliation import Reconciliation, render_conflict


def test_conflict_view_exposes_reopen_action_and_affected_ars():
    view = render_conflict(Reconciliation("AR-23", 2, ("AR-24",), ("evidence diverged",), "discussion-required"))
    assert "action: reopen" in view
    assert "affected ARs: AR-24" in view
    assert "evidence diverged" in view
