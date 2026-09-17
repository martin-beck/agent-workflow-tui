"""Coordinator/TUI bridge: explicit trigger and AR persistence projection."""
from __future__ import annotations

from typing import Any

BRIDGE_VERSION = "1.0"


def interaction_state(*, request_id: str, decision_class: str, status: str = "pending", deadline: str | None = None) -> dict[str, Any]:
    """Return the Coordinator-owned AR metadata that requests human input."""
    if not request_id.startswith("AWG-"):
        raise ValueError("decision_request_ref must be an AWG request id")
    if status not in {"pending", "in_progress", "resolved", "superseded"}:
        raise ValueError("invalid decision status")
    value: dict[str, Any] = {"schema_version": BRIDGE_VERSION, "interaction_required": status in {"pending", "in_progress"}, "decision_status": status, "decision_request_ref": request_id, "decision_class": decision_class}
    if deadline is not None:
        value["oracle_deadline"] = deadline
    return value


def apply_tui_response(ar: dict[str, Any], event: dict[str, Any], *, response_event_ref: str) -> dict[str, Any]:
    """Project an accepted TUI event into an AR metadata update.

    The returned copy is suitable for persistence in the AR front-matter. It
    never marks implementation complete; it records only human disposition,
    selected proposal, and the resulting description/specification text.
    """
    if event.get("event_type") not in {"select", "add-proposal", "clarify", "reject", "reopen", "reconciled"}:
        raise ValueError("event is not a decision response")
    payload = event.get("payload") or {}
    updated = dict(ar)
    bridge = dict(ar.get("interaction", {}))
    disposition = payload.get("disposition", event["event_type"])
    bridge.update({"schema_version": BRIDGE_VERSION, "decision_status": "resolved" if disposition in {"select", "selected", "reconciled"} else "pending", "interaction_required": disposition not in {"select", "selected", "reconciled"}, "last_response_event": response_event_ref})
    updated["interaction"] = bridge
    updated["decision"] = {"request_id": payload.get("request_id", bridge.get("decision_request_ref")), "disposition": disposition, "selected_candidate": payload.get("selected_candidate"), "selected": payload.get("selected"), "user_proposal": payload.get("user_proposal")}
    if "description" in payload:
        updated["description"] = payload["description"]
    if "specification" in payload:
        updated["specification"] = payload["specification"]
    return updated
