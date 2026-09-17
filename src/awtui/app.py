"""Minimal dependency-free terminal shell for the Agent Workflow TUI.

The shell owns terminal lifetime and bounded input only. Discussion semantics
and AR mutations are delegated to later adapters.
"""
from __future__ import annotations

import curses
from typing import Callable

from .discussion import DiscussionPacket


def draw_shell(screen, *, title: str = "Agent Workflow TUI") -> None:
    height, width = screen.getmaxyx()
    screen.erase()
    screen.addnstr(0, 0, title, max(0, width - 1), curses.A_BOLD)
    if height > 2:
        screen.addnstr(height - 1, 0, "q: quit", max(0, width - 1))
    screen.refresh()


def draw_packet(screen, packet: DiscussionPacket, *, index: int = 0) -> None:
    """Render synchronized document and discussion-point panes."""
    height, width = screen.getmaxyx()
    split = max(1, width // 2)
    active = packet.active(index)
    screen.erase()
    screen.addnstr(0, 0, f"{packet.document}  {active.anchor}", max(0, split - 1), curses.A_BOLD)
    screen.addnstr(0, split, "discussion points", max(0, width - split - 1), curses.A_BOLD)
    screen.addnstr(1, 0, active.question, max(0, split - 1))
    for row, point in enumerate(packet.points[: max(0, height - 3)], start=2):
        marker = "> " if point is active else "  "
        flags = " [unresolved]" if point.unresolved else ""
        attribute = curses.A_REVERSE if point is active else 0
        screen.addnstr(row, split, f"{marker}{point.point_id}{flags}", max(0, width - split - 1), attribute)
    screen.refresh()


def run_screen(screen, *, input_fn: Callable[[], int] | None = None, max_steps: int = 1024) -> int:
    """Run the bounded shell; return zero on a normal quit."""
    input_fn = input_fn or screen.getch
    screen.keypad(True)
    steps = 0
    while steps < max_steps:
        draw_shell(screen)
        key = input_fn()
        if key in (ord("q"), ord("Q"), 27):
            return 0
        steps += 1
    return 2


def main() -> int:
    return int(curses.wrapper(run_screen))


if __name__ == "__main__":
    raise SystemExit(main())
