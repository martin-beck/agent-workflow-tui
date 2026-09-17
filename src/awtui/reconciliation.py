"""Conflict and post-discussion reconciliation projection."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Reconciliation:
    ar_id: str
    task_revision: int
    affected_ars: tuple[str, ...]
    contradictions: tuple[str, ...] = ()
    disposition: str = "reconciled"

    def __post_init__(self):
        if not self.affected_ars:
            raise ValueError("reconciliation must identify affected ARs")
        if self.disposition not in {"reconciled", "reopen", "discussion-required"}:
            raise ValueError("invalid reconciliation disposition")
        if self.contradictions and self.disposition == "reconciled":
            raise ValueError("contradictions require reopen or discussion")

    def event_type(self) -> str:
        return "reopen" if self.disposition in {"reopen", "discussion-required"} else "reconciled"

