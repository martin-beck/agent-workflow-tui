from awtui.journal import render_history


def test_render_history_exposes_resume_state_and_future_requests():
    text = render_history({"ar_id": "AR-22", "task_revision": 4, "responses": {"p1": "select"}, "unresolved": ["p2"], "future_requests": ["AR-30"]})
    assert "Journal AR-22 revision 4" in text
    assert "answered: 1" in text
    assert "unresolved: p2" in text
    assert "future ARs: AR-30" in text
