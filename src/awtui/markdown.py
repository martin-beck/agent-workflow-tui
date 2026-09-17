"""Terminal Markdown rendering shared by live panes and scenario demos."""
from __future__ import annotations

from io import StringIO

from rich.console import Console
from rich.markdown import Markdown


def render_markdown(document: str, *, width: int = 80) -> str:
    if not isinstance(document, str):
        raise TypeError("Markdown document must be text")
    stream = StringIO()
    console = Console(file=stream, force_terminal=False, color_system=None, width=max(20, width), record=False)
    console.print(Markdown(document))
    return stream.getvalue().rstrip()
