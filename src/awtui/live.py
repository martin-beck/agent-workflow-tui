"""Prompt-toolkit live application shell; contracts remain toolkit-neutral."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout, VSplit
from prompt_toolkit.widgets import Frame, TextArea


RECORDED_CONTROLS = {"\n": "select", "\r": "select", "r": "reject", "c": "clarify", "m": "request-more-evidence", "a": "add-proposal", "s": "safe-exit", "o": "reopen"}


@dataclass(frozen=True)
class LiveDecision:
    """A renderable decision row from an AR discussion packet.

    The live shell deliberately accepts plain mappings too (the Coordinator
    adapter can pass decoded JSON), while this type documents the small view
    model needed by the renderer.
    """

    point_id: str
    anchor: str
    question: str
    proposals: tuple[Mapping[str, Any], ...] = ()
    helper: str = ""


def _decision(value: LiveDecision | Mapping[str, Any]) -> LiveDecision:
    if isinstance(value, LiveDecision):
        return value
    proposals = tuple(value.get("proposals", ()))
    return LiveDecision(
        point_id=str(value.get("point_id", value.get("id", "decision"))),
        anchor=str(value.get("anchor", "document")),
        question=str(value.get("question", "")),
        proposals=proposals,
        helper=str(value.get("helper", value.get("implications", ""))),
    )


class LiveViewState:
    """Small, testable state machine for live document and decision focus."""

    def __init__(self, *, workplan: str, design_document: str,
                 decisions: Sequence[LiveDecision | Mapping[str, Any]],
                 document_pane: TextArea, points_pane: TextArea,
                 helper_pane: TextArea, on_event=None):
        self.workplan = workplan
        self.design_document = design_document
        self.decisions = tuple(_decision(item) for item in decisions)
        self.document_pane = document_pane
        self.points_pane = points_pane
        self.helper_pane = helper_pane
        self.on_event = on_event
        self.document_mode = "design"
        self.decision_index = 0
        self.proposal_index = 0
        self.refresh()

    @property
    def active(self) -> LiveDecision | None:
        return self.decisions[self.decision_index] if self.decisions else None

    def refresh(self) -> None:
        self.document_pane.text = self.design_document if self.document_mode == "design" else self.workplan
        if not self.decisions:
            return
        point = self.active
        rows = []
        for index, decision in enumerate(self.decisions):
            marker = "▶" if index == self.decision_index else " "
            rows.append(f"{marker} {decision.point_id}  [{decision.anchor}]  {decision.question}")
        self.points_pane.text = "\n".join(rows)
        proposal = point.proposals[self.proposal_index] if point.proposals else {}
        label = proposal.get("label", proposal.get("id", "")) if isinstance(proposal, Mapping) else str(proposal)
        rationale = proposal.get("rationale", "") if isinstance(proposal, Mapping) else ""
        tradeoffs = proposal.get("tradeoffs", "") if isinstance(proposal, Mapping) else ""
        confidence = proposal.get("confidence", "") if isinstance(proposal, Mapping) else ""
        self.helper_pane.text = "\n".join(filter(None, (
            f"Decision: {point.question}",
            f"Anchor: {point.anchor}",
            f"Proposal {self.proposal_index + 1}/{len(point.proposals)}: {label}" if point.proposals else "No proposal selected",
            f"Rationale: {rationale}" if rationale else "",
            f"Trade-offs: {tradeoffs}" if tradeoffs else "",
            f"Confidence: {confidence}" if confidence != "" else "",
            point.helper,
        )))

    def move(self, delta: int) -> None:
        if self.decisions:
            self.decision_index = (self.decision_index + delta) % len(self.decisions)
            self.proposal_index = 0
            self.refresh()

    def switch_document(self, mode: str | None = None) -> None:
        self.document_mode = mode or ("workplan" if self.document_mode == "design" else "design")
        self.refresh()

    def next_proposal(self, delta: int) -> None:
        if self.active and self.active.proposals:
            self.proposal_index = (self.proposal_index + delta) % len(self.active.proposals)
            self.refresh()

    def emit(self, event_type: str) -> None:
        if self.on_event is not None:
            self.on_event(event_type)


def dispatch_recorded_input(keys: str, on_event) -> list[str]:
    """Replay bounded terminal keystrokes through the same public event names."""
    emitted = []
    for key in keys:
        if key in RECORDED_CONTROLS:
            event_type = RECORDED_CONTROLS[key]
            emitted.append(event_type)
            on_event(event_type)
        elif key in {"q", "\x1b"}:
            break
    return emitted


def build_application(*, document: str = "Awaiting AR context", points: str = "No discussion points", helper: str = "Select a point for implications and evidence", on_event=None, workplan: str | None = None, design_document: str | None = None, decisions: Sequence[LiveDecision | Mapping[str, Any]] = ()) -> Application:
    """Build the live full-screen client with real focus and document state.

    ``document``/``points`` remain supported for lightweight callers. Live
    Coordinator clients should provide both documents and structured
    ``decisions`` so navigation is anchored to the exact AR packet.
    """
    design_text = design_document if design_document is not None else document
    plan_text = workplan if workplan is not None else "Workplan unavailable for this AR"
    left = TextArea(text=design_text, read_only=True, scrollbar=True)
    right = TextArea(text=points, read_only=True, scrollbar=True)
    helper_view = TextArea(text=helper, read_only=True, scrollbar=True)
    footer = TextArea(text="q: quit  tab/w/d: workplan/design  ↑/↓: decision  ←/→: proposal  enter: select  r: reject  c: clarify  m: evidence  a: add  s: save  o: reopen", read_only=True, height=1)
    bindings = KeyBindings()

    @bindings.add("q")
    @bindings.add("escape")
    def quit_app(event) -> None:
        event.app.exit(result=0)

    def emit(event, event_type: str) -> None:
        if on_event is not None:
            on_event(event_type)

    state = LiveViewState(
        workplan=plan_text,
        design_document=design_text,
        decisions=decisions,
        document_pane=left,
        points_pane=right,
        helper_pane=helper_view,
        on_event=on_event,
    )

    # These bindings are eager because TextArea has its own cursor navigation;
    # the AR discussion list, rather than the text cursor, is the live focus.
    @bindings.add("up", eager=True)
    def previous_decision(event) -> None:
        state.move(-1)

    @bindings.add("down", eager=True)
    def next_decision(event) -> None:
        state.move(1)

    @bindings.add("left", eager=True)
    def previous_proposal(event) -> None:
        state.next_proposal(-1)

    @bindings.add("right", eager=True)
    def next_proposal(event) -> None:
        state.next_proposal(1)

    @bindings.add("tab", eager=True)
    def toggle_document(event) -> None:
        state.switch_document()

    @bindings.add("w", eager=True)
    def show_workplan(event) -> None:
        state.switch_document("workplan")

    @bindings.add("d", eager=True)
    def show_design(event) -> None:
        state.switch_document("design")

    for key, event_type in (("enter", "select"), ("r", "reject"), ("c", "clarify"), ("m", "request-more-evidence"), ("a", "add-proposal"), ("s", "safe-exit"), ("o", "reopen")):
        @bindings.add(key)
        def control(event, event_type=event_type) -> None:
            emit(event, event_type)

    body = HSplit([VSplit([Frame(left, title="AR document"), Frame(right, title="Discussion points")]), Frame(helper_view, title="Proposal / implications"), footer])
    # Ask prompt-toolkit to clear its final frame while it restores raw mode
    # and the alternate screen.  This prevents the last rendered frame from
    # being left in the user's shell after q/Escape, SIGINT, an exception, or
    # a resize-triggered redraw.
    application = Application(
        layout=Layout(body), key_bindings=bindings, full_screen=True,
        erase_when_done=True,
    )
    application.awtui_panes = (left, right, helper_view)
    application.awtui_footer = footer
    application.awtui_state = state
    return application


def run_application(application: Application, *, output_fn=print) -> int:
    """Run the app with prompt-toolkit cleanup on every exit path.

    prompt-toolkit's ``run_async`` owns raw mode, alternate-screen setup,
    resize handling, and renderer reset in a ``finally`` block.  Disabling its
    interactive exception screen lets this boundary report a short,
    privacy-safe status after that cleanup has completed.
    """
    try:
        result = application.run(set_exception_handler=False, handle_sigint=True)
    except KeyboardInterrupt:
        output_fn("TUI interrupted; terminal restored.")
        return 130
    except EOFError:
        output_fn("TUI input closed; terminal restored.")
        return 0
    except BaseException as error:
        # Do not expose traceback, packet contents, prompts, or host paths.
        output_fn(f"TUI stopped ({type(error).__name__}); terminal restored.")
        return 1
    return int(result or 0)


def main() -> int:
    return run_application(build_application())
