"""Prompt-toolkit live application shell; contracts remain toolkit-neutral."""
from __future__ import annotations

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout, VSplit
from prompt_toolkit.widgets import Frame, TextArea


def build_application(*, document: str = "Awaiting AR context", points: str = "No discussion points") -> Application:
    left = TextArea(text=document, read_only=True, scrollbar=True)
    right = TextArea(text=points, read_only=True, scrollbar=True)
    footer = TextArea(text="q: quit  ↑/↓: navigate  enter: select", read_only=True, height=1)
    bindings = KeyBindings()

    @bindings.add("q")
    @bindings.add("escape")
    def quit_app(event) -> None:
        event.app.exit(result=0)

    body = HSplit([VSplit([Frame(left, title="AR document"), Frame(right, title="Discussion points")]), footer])
    application = Application(layout=Layout(body), key_bindings=bindings, full_screen=True)
    application.awtui_panes = (left, right)
    return application


def main() -> int:
    return int(build_application().run())
