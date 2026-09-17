"""Revision-bound session boundary for TUI adapters."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SessionBoundary:
    project_id: str
    ar_id: str
    task_revision: int
    packet_digest: str
    session_id: str
    next_sequence: int = 1

    @classmethod
    def from_context(cls, context: dict[str, Any]) -> "SessionBoundary":
        required = ("project_id", "ar_id", "task_revision", "packet_digest", "session_id")
        if any(key not in context for key in required):
            raise ValueError("incomplete AR context")
        return cls(*(context[key] for key in required))

    def accept(self, event: dict[str, Any]) -> "SessionBoundary":
        for key in ("project_id", "ar_id", "task_revision", "packet_digest", "session_id"):
            if event.get(key) != getattr(self, key):
                raise ValueError(f"event {key} does not match session")
        if event.get("sequence") != self.next_sequence:
            raise ValueError("event sequence is stale or out of order")
        return SessionBoundary(self.project_id, self.ar_id, self.task_revision, self.packet_digest, self.session_id, self.next_sequence + 1)

