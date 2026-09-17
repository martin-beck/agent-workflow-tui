"""AWG decision adapter preserving explicit oracle authority."""
from __future__ import annotations

from typing import Any

from .discussion import DecisionResponse


def decision_event(response: DecisionResponse, *, project_id: str, ar_id: str, task_revision: int, packet_digest: str, session_id: str, sequence: int) -> dict[str, Any]:
    """Project a TUI response into an AWG-owned event envelope."""
    payload: dict[str, Any] = {"point_id": response.point_id, "disposition": response.disposition, "selected": response.selected}
    if response.user_proposal is not None:
        payload["user_proposal"] = {"label": response.user_proposal.label, "evaluated": response.user_proposal_evaluated}
    return {"project_id": project_id, "ar_id": ar_id, "task_revision": task_revision, "packet_digest": packet_digest, "session_id": session_id, "sequence": sequence, "event_type": response.disposition, "payload": payload}

