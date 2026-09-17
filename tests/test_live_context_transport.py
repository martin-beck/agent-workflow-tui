from awtui.live import build_application_from_context


def _context():
    return {
        "project_id": "demo",
        "ar_id": "AR-0049",
        "task_revision": 1,
        "packet_digest": "sha256:" + "a" * 64,
        "session_id": "live-49",
        "documents": {"design": "# Design\n\nBoundary phrase", "workplan": "# Workplan\n\nRollout phrase"},
    }


def _decisions():
    return [{"point_id": "p", "anchor": "design:L2", "highlight": "Boundary phrase", "question": "Choose", "proposals": [{"label": "A"}, {"label": "B"}]}]


def test_context_adapter_emits_revision_bound_acknowledged_event():
    events = []
    app = build_application_from_context(_context(), decisions=_decisions(), record_event=events.append)
    binding = next(binding for binding in app.key_bindings.bindings if str(binding.keys[0]) == "Keys.ControlM")

    class Event:
        app = None

    binding.handler(Event())
    assert events[0]["project_id"] == "demo"
    assert events[0]["ar_id"] == "AR-0049"
    assert events[0]["sequence"] == 1
    assert events[0]["event_type"] == "select"
    assert app.awtui_last_acknowledgement.accepted is True


def test_rejected_context_event_does_not_commit_response():
    app = build_application_from_context(_context(), decisions=_decisions(), record_event=lambda _event: False)

    class Event:
        app = None

    binding = next(binding for binding in app.key_bindings.bindings if str(binding.keys[0]) == "Keys.ControlM")
    binding.handler(Event())
    assert app.awtui_state.responses == {}
    assert "Event not accepted" in app.awtui_panes[2].text
