"""AWG discussion packet projection used by the terminal renderer."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Proposal:
    label: str
    rationale: str
    confidence: float
    tradeoffs: str


@dataclass(frozen=True)
class PacketPoint:
    point_id: str
    anchor: str
    question: str
    proposals: tuple[Proposal, ...]
    implications: str
    evidence_gap: str = ""
    unresolved: bool = True

    def __post_init__(self):
        if not self.point_id or not self.anchor or len(self.proposals) < 2:
            raise ValueError("packet points require identity, anchor, and two proposals")
        if any(not 0 <= p.confidence <= 1 for p in self.proposals):
            raise ValueError("proposal confidence must be between zero and one")


@dataclass(frozen=True)
class DiscussionPacket:
    ar_id: str
    task_revision: int
    points: tuple[PacketPoint, ...]
    document: str = "design"

    def __post_init__(self):
        if not self.points or len({p.point_id for p in self.points}) != len(self.points):
            raise ValueError("packet requires unique discussion points")

    def active(self, index: int = 0) -> PacketPoint:
        return self.points[max(0, min(index, len(self.points) - 1))]

