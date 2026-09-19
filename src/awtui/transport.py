"""Revision-bound transport envelopes for live TUI sessions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .boundary import SessionBoundary


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


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be positive")

    def attempts(self):
        """Yield bounded attempt numbers; callers must stop on rejection/staleness."""
        return range(1, self.max_attempts + 1)

    @staticmethod
    def fail_closed(ack: EventAcknowledgement) -> bool:
        """Only accepted acknowledgements permit continuation."""
        return not ack.accepted


class LiveSessionTransport:
    """Coordinate boundary validation, bounded delivery, and acknowledgements."""

    def __init__(self, context: dict[str, Any], deliver, policy: RetryPolicy | None = None):
        self.boundary = SessionBoundary.from_context(context)
        self.deliver = deliver
        self.policy = policy or RetryPolicy()

    def submit(self, event_type: str, **payload: Any) -> EventAcknowledgement:
        sequence = self.boundary.next_sequence
        envelope = SessionEnvelope(self.boundary.project_id, self.boundary.ar_id, self.boundary.task_revision, self.boundary.packet_digest, self.boundary.session_id, sequence, event_type)
        # Keep the wire shape identical to ``schemas/tui-event.schema.json``:
        # revision/session identity is envelope metadata and all decision
        # details are contained in one payload object.  Earlier versions
        # leaked point_id/selected at the top level, which passed the local
        # boundary checks but could not be projected by the Coordinator.
        event = envelope.as_event(payload=dict(payload))
        try:
            # Validate against the current boundary, but do not commit the
            # sequence until the receiver has acknowledged delivery. A
            # rejected/dropped event must not consume a sequence number: the
            # caller must be able to retry the same revision-bound event.
            candidate_boundary = self.boundary.accept(event)
        except ValueError as exc:
            return EventAcknowledgement(envelope.session_id, sequence, False, str(exc))
        for _attempt in self.policy.attempts():
            try:
                result = self.deliver(event)
                if result is not False:
                    self.boundary = candidate_boundary
                    return EventAcknowledgement(envelope.session_id, sequence, True)
            except Exception as exc:  # transport failures are retried, never fabricated as success
                reason = str(exc)
        return EventAcknowledgement(envelope.session_id, sequence, False, locals().get("reason", "delivery rejected"))
