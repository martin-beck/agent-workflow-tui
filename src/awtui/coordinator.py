"""Narrow Coordinator lifecycle adapter for accepted TUI events."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .boundary import SessionBoundary


class CoordinatorAdapter:
    def __init__(self, context: dict[str, Any], record_event: Callable[[dict[str, Any]], Any]):
        self.boundary = SessionBoundary.from_context(context)
        self._record_event = record_event

    def submit(self, event: dict[str, Any]) -> Any:
        self.boundary = self.boundary.accept(event)
        return self._record_event(event)

