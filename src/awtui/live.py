"""Prompt-toolkit live application shell; contracts remain toolkit-neutral."""
from __future__ import annotations

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout, VSplit
from prompt_toolkit.widgets import Frame, TextArea


def build_application(*, document: str = "Awaiting AR context", points: str = "No discussion points", helper: str = "Select a point for implications and evidence", on_event=None) -> Application:
    left = TextArea(text=document, read_only=True, scrollbar=True)
    right = TextArea(text=points, read_only=True, scrollbar=True)
    helper_view = TextArea(text=helper, read_only=True, scrollbar=True)
    footer = TextArea(text="q: quit  enter: select  r: reject  c: clarify  a: add  s: save  o: reopen", read_only=True, height=1)
    bindings = KeyBindings()

    @bindings.add("q")
    @bindings.add("escape")
    def quit_app(event) -> None:
        event.app.exit(result=0)

    def emit(event, event_type: str) -> None:
        if on_event is not None:
            on_event(event_type)

    for key, event_type in (("enter", "select"), ("r", "reject"), ("c", "clarify"), ("a", "add-proposal"), ("s", "safe-exit"), ("o", "reopen")):
        @bindings.add(key)
        def control(event, event_type=event_type) -> None:
            emit(event, event_type)

    body = HSplit([VSplit([Frame(left, title="AR document"), Frame(right, title="Discussion points")]), Frame(helper_view, title="Proposal / implications"), footer])
    application = Application(layout=Layout(body), key_bindings=bindings, full_screen=True)
    application.awtui_panes = (left, right, helper_view)
    return application


def main() -> int:
    return int(build_application().run())
