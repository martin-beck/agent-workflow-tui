"""Revision-bound transport envelopes for live TUI sessions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SessionEnvelope:
    project_id: str
    ar_id: str
    task_revision: int
    packet_digest: str
    session_id: str
    sequence: int
    event_type: str

    def as_event(self, **payload: Any) -> dict[str, Any]:
        value = self.__dict__.copy()
        value.update(payload)
        return value


@dataclass(frozen=True)
class EventAcknowledgement:
    session_id: str
    sequence: int
    accepted: bool
    reason: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {"session_id": self.session_id, "sequence": self.sequence, "accepted": self.accepted, "reason": self.reason}
