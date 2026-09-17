"""Minimal dependency-free terminal shell for the Agent Workflow TUI.

The shell owns terminal lifetime and bounded input only. Discussion semantics
and AR mutations are delegated to later adapters.
"""
from __future__ import annotations

import curses
from typing import Callable


def draw_shell(screen, *, title: str = "Agent Workflow TUI") -> None:
    height, width = screen.getmaxyx()
    screen.erase()
    screen.addnstr(0, 0, title, max(0, width - 1), curses.A_BOLD)
    if height > 2:
        screen.addnstr(height - 1, 0, "q: quit", max(0, width - 1))
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

