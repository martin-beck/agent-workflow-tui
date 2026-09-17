from awtui.awg import request_digest, request_to_tui, tui_response_event
from awtui.discussion import DecisionResponse


def request():
    return {
        "schema_version": "0.2",
        "request_id": "AWG-EXAMPLE-001",
        "trigger": "decision",
        "decision_class": "design",
        "context": {
            "task_ref": "AR-0005", "task_revision": 3,
            "objective": "Choose a bounded migration path",
            "constraints": ["preserve rollback"],
            "quality_refs": ["AWQ-PRIVACY-001"],
            "evidence_refs": ["evidence:formal-001"],
        },
        "specification": {},
        "formal_check": {"status": "pass"},
        "candidates": [{
            "candidate_id": "C-INCREMENTAL", "action": "Migrate incrementally",
            "rank": 1, "confidence": .8, "rationale": "Limits blast radius",
            "tradeoffs": ["slower"], "impact": "medium", "reversibility": "easy",
        }],
    }


def test_guidance_request_maps_to_revision_bound_tui_inputs():
    context, decisions = request_to_tui(request(), project_id="demo", session_id="session-1")
    assert context["ar_id"] == "AR-0005"
    assert context["task_revision"] == 3
    assert context["request_id"] == "AWG-EXAMPLE-001"
    assert context["packet_digest"] == request_digest(request())
    assert decisions[0]["proposals"][0]["candidate_id"] == "C-INCREMENTAL"
    assert decisions[0]["proposals"][0]["label"] == "Migrate incrementally"


def test_tui_response_returns_candidate_identity_and_request_binding():
    event = tui_response_event(
        request(),
        DecisionResponse("AWG-EXAMPLE-001", "select", "Migrate incrementally"),
        project_id="demo", session_id="session-1", sequence=1,
    )
    assert event["ar_id"] == "AR-0005"
    assert event["task_revision"] == 3
    assert event["payload"]["request_id"] == "AWG-EXAMPLE-001"
    assert event["payload"]["selected_candidate"] == "C-INCREMENTAL"
    assert event["event_type"] == "select"
