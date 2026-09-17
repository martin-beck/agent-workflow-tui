from awtui.bridge import apply_tui_response, interaction_state


def test_interaction_state_is_explicit_and_pending():
    value = interaction_state(request_id="AWG-DECIDE-1", decision_class="implementation-choice")
    assert value["interaction_required"] is True
    assert value["decision_status"] == "pending"


def test_response_projects_selection_and_ar_text():
    ar = {"id": "AR-0001", "interaction": interaction_state(request_id="AWG-DECIDE-1", decision_class="design")}
    event = {"event_type": "select", "payload": {"disposition": "selected", "request_id": "AWG-DECIDE-1", "selected_candidate": "C-A", "selected": "Use A", "description": "Chosen design", "specification": {"mode": "A"}}}
    result = apply_tui_response(ar, event, response_event_ref="evt-1")
    assert result["interaction"]["interaction_required"] is False
    assert result["decision"]["selected_candidate"] == "C-A"
    assert result["description"] == "Chosen design"


def test_invalid_event_rejected():
    try:
        apply_tui_response({}, {"event_type": "acknowledge"}, response_event_ref="evt")
    except ValueError:
        return
    raise AssertionError("invalid event accepted")
