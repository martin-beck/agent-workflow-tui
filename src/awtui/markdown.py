"""Terminal Markdown rendering shared by live panes and scenario demos."""
from __future__ import annotations

from io import StringIO

from rich.console import Console
from rich.markdown import Markdown


def render_markdown(document: str, *, width: int = 80) -> str:
    if not isinstance(document, str):
        raise TypeError("Markdown document must be text")
    # Some Coordinator payloads carry a legacy all-caps document tag before
    # the actual Markdown.  It is metadata, not document content, and must
    # never leak into the rendered pane.
    document = document.lstrip("\ufeff\n")
    if document.splitlines() and document.splitlines()[0].strip() in {"WORKPLAN", "DESIGN"}:
        document = "\n".join(document.splitlines()[1:]).lstrip("\n")
    stream = StringIO()
    console = Console(file=stream, force_terminal=False, color_system=None, width=max(20, width), record=False)
    console.print(Markdown(document))
    return stream.getvalue().rstrip()
