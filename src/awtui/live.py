"""Full-screen live interaction for Agent Workflow discussion packets."""
from __future__ import annotations

from dataclasses import replace
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import HSplit, Layout, VSplit
from prompt_toolkit.widgets import Frame, TextArea
from .discussion import DiscussionPacket, DecisionResponse, PacketPoint, Proposal
from .markdown import render_markdown

RECORDED_CONTROLS = {"\n": "select", "\r": "select", "r": "reject", "c": "clarify", "m": "request-more-evidence", "a": "add-proposal", "s": "safe-exit", "o": "reopen"}

def dispatch_recorded_input(keys: str, on_event) -> list[str]:
    emitted = []
    for key in keys:
        if key in RECORDED_CONTROLS:
            emitted.append(RECORDED_CONTROLS[key]); on_event(RECORDED_CONTROLS[key])
        elif key in {"q", "\x1b"}:
            break
    return emitted

class LiveInteraction:
    """Mutable view-model for point/proposal selection and batch responses."""
    def __init__(self, packet: DiscussionPacket):
        self.packet, self.point_index, self.proposal_index = packet, 0, 0
        self.document_mode = packet.document
        self.responses: dict[str, DecisionResponse] = {}
        self.input_mode = False
    @property
    def point(self): return self.packet.points[self.point_index]
    @property
    def proposal(self): return self.point.proposals[self.proposal_index]
    def move_point(self, delta: int):
        self.point_index = max(0, min(len(self.packet.points)-1, self.point_index + delta)); self.proposal_index = 0
    def move_proposal(self, delta: int):
        self.proposal_index = max(0, min(len(self.point.proposals)-1, self.proposal_index + delta))
    def add_proposal(self, proposal: Proposal):
        point = replace(self.point, proposals=self.point.proposals + (proposal,))
        self.packet = replace(self.packet, points=self.packet.points[:self.point_index] + (point,) + self.packet.points[self.point_index+1:])
        self.proposal_index = len(point.proposals)-1
        self._refresh_callback()
    def respond(self, disposition: str) -> DecisionResponse:
        user = self.proposal if self.proposal.label.startswith("User: ") else None
        response = DecisionResponse(self.point.point_id, disposition, self.proposal.label if disposition == "select" else None, user, user is not None)
        self.responses[self.point.point_id] = response
        self._refresh_callback()
        return response
    def render_points(self) -> str:
        lines = []
        for i, point in enumerate(self.packet.points):
            response = self.responses.get(point.point_id)
            user_proposal = next((proposal for proposal in point.proposals if proposal.label.startswith("User: ")), None)
            status = "✅ answered" if response else ("✎ proposal" if user_proposal else "unresolved")
            lines.append(f"{'▶' if i == self.point_index else ' '} {point.point_id} [{status}]  {point.anchor}")
        lines += ["", f"Decision: {self.point.question}"]
        response = self.responses.get(self.point.point_id)
        user_proposal = next((proposal for proposal in self.point.proposals if proposal.label.startswith("User: ")), None)
        if response and response.selected:
            visible = [(self.proposal_index, self.proposal)] if self.proposal.label == response.selected else [(index, proposal) for index, proposal in enumerate(self.point.proposals) if proposal.label == response.selected]
        elif user_proposal:
            visible = [(index, user_proposal) for index, proposal in enumerate(self.point.proposals) if proposal is user_proposal]
        else:
            visible = list(enumerate(self.point.proposals))
        lines += [f"  {'▶' if i == self.proposal_index else ' '} {p.label}" for i, p in visible]
        return "\n".join(lines)
    def render_helper(self) -> str:
        p = self.proposal
        return f"Proposal {self.proposal_index + 1}/{len(self.point.proposals)}: {p.label}\n\nRationale: {p.rationale}\nConfidence: {p.confidence:.2f}\nTrade-offs: {p.tradeoffs}\n\nAnchor: {self.point.anchor}\nHighlight: {self.point.highlight or self.point.question}\nImplications: {self.point.implications}\nEvidence gap: {self.point.evidence_gap or 'none recorded'}\nHuman intent is separate from implementation and quality evidence."

    def switch_document(self):
        self.document_mode = "workplan" if self.document_mode != "workplan" else "design"
        self._manual_document_switch = True
        self._refresh_callback()

    # Compatibility names used by scenario drivers and a convenient public UI API.
    def move(self, delta: int):
        self.move_point(delta)
        self._refresh_callback()

    def next_proposal(self, delta: int):
        self.move_proposal(delta)
        self._refresh_callback()

    def _refresh_callback(self):
        if hasattr(self, "_refresh"): self._refresh()

def _default_packet(document: str, points: str) -> DiscussionPacket:
    p = Proposal("Review in context", "Inspect the highlighted material", .7, "Requires human review")
    q = Proposal("Request evidence", "Ask for evidence before deciding", .8, "Delays the decision")
    return DiscussionPacket("interactive", 1, (PacketPoint("point-1", "document:1", points, (p, q), "Review downstream effects", "Evidence is synthetic", highlight=points),), document=document)

def _packet_from_decisions(decisions, design_document: str, workplan: str) -> DiscussionPacket:
    points = []
    for raw in decisions:
        proposals = tuple(Proposal(p.get("label", "Proposal"), p.get("rationale", "No rationale recorded"), float(p.get("confidence", .5)), p.get("tradeoffs", "No trade-offs recorded")) for p in raw.get("proposals", []))
        while len(proposals) < 2:
            proposals += (Proposal("Request evidence", "Gather missing evidence", .5, "Delays decision"),)
        points.append(PacketPoint(raw["point_id"], raw.get("anchor", "document:1"), raw.get("question", "What should happen?"), proposals, raw.get("helper", raw.get("implications", "Review downstream implications")), raw.get("evidence_gap", ""), highlight=raw.get("highlight", raw.get("question", ""))))
    return DiscussionPacket("interactive", 1, tuple(points), "design")


def _standalone_demo_decisions() -> list[dict]:
    return [{
        "point_id": f"standalone-{index}",
        "anchor": anchor,
        "question": question,
        "highlight": {"design:L4": "Design boundary", "workplan:L8": "Rollout step", "design:L16": "Validation path"}[anchor],
        "proposals": [
            {"label": "Conservative", "rationale": "Minimize change", "confidence": .8, "tradeoffs": "slower delivery"},
            {"label": "Expedite", "rationale": "Shorten feedback loop", "confidence": .6, "tradeoffs": "higher review load"},
        ],
        "helper": "Review the highlighted document anchor and downstream implications.",
        "evidence_gap": "Standalone demo evidence is synthetic.",
    } for index, (anchor, question) in enumerate((("design:L4", "Which design boundary?"), ("workplan:L8", "Which rollout step?"), ("design:L16", "Which validation path?")), 1)]


def run_application(application, *, output_fn=print) -> int:
    """Run a live app while restoring the terminal and redacting failures."""
    try:
        application.run()
        return 0
    except KeyboardInterrupt:
        output_fn("TUI interrupted; terminal restored.")
        return 130
    except Exception as error:  # noqa: BLE001 - public boundary intentionally redacts details
        output_fn(f"TUI stopped ({type(error).__name__}); terminal restored.")
        return 1


def build_application(*, document: str = "Awaiting AR context", points: str = "No discussion points", helper: str = "Select a point for implications and evidence", on_event=None, packet: DiscussionPacket | None = None, workplan: str = "Awaiting workplan", design_document: str | None = None, decisions=None) -> Application:
    design_document = design_document if design_document is not None else document
    packet = packet or (_packet_from_decisions(decisions, design_document, workplan) if decisions else None)
    interaction = LiveInteraction(packet or _default_packet(design_document, points))
    document_view = TextArea(text=render_markdown(design_document), read_only=True, scrollbar=True)
    points_view = TextArea(text=interaction.render_points() if packet else points, read_only=True, scrollbar=True)
    helper_view = TextArea(text=interaction.render_helper() if packet else helper, read_only=True, scrollbar=True)
    editor = TextArea(text="", multiline=True, scrollbar=True, height=3, prompt="New proposal (label | rationale | confidence | trade-offs): ")
    editor.visible = False
    footer = TextArea(text="↑/↓: decision  ←/→: proposal  tab/w/d: workplan/design  page-up/page-down: scroll document  enter: select  r: reject  c: clarify  m: evidence  a: add proposal  s: save  o: reopen  q: quit", read_only=True, height=1)
    bindings = KeyBindings()
    def refresh():
        points_view.text = interaction.render_points() if packet else points
        helper_view.text = ("Enter: label | rationale | confidence (0..1) | trade-offs" if interaction.input_mode else (interaction.render_helper() if packet else helper))
        document = workplan if interaction.document_mode == "workplan" else design_document
        rendered = render_markdown(document)
        if packet:
            point = interaction.point
            phrase = point.highlight or point.question or point.anchor
            # If the selected phrase is only present in the other authoritative
            # document, follow its anchor.  This keeps normal manual w/d
            # inspection possible when both documents contain the phrase.
            follow_anchor = not getattr(interaction, "_manual_document_switch", False)
            interaction._manual_document_switch = False
            if follow_anchor and phrase.casefold() not in rendered.casefold():
                target = point.anchor.split(":", 1)[0].lower()
                if target == "workplan" and interaction.document_mode != "workplan":
                    interaction.document_mode = "workplan"
                    rendered = render_markdown(workplan)
                elif target == "design" and interaction.document_mode != "design":
                    interaction.document_mode = "design"
                    rendered = render_markdown(design_document)
            # Keep the active context visible above the rendered Markdown and
            # locate the phrase in the rendered buffer so prompt-toolkit
            # scrolls the read-only pane to the selected decision.
            prefix = f"▶ ACTIVE DECISION ANCHOR: {point.anchor}\n▶ HIGHLIGHT TARGET\n\n"
            document_view.text = prefix + rendered
            # Search the rendered Markdown body, not the explanatory marker,
            # so the viewport lands on the actual source text.
            body_start = len(prefix)
            position = document_view.text.casefold().find(phrase.casefold(), body_start)
            if position < 0:
                # A live AR may refer to text not present in a stale document;
                # retain an explicit, visible marker rather than failing.
                document_view.text += f"\n\n▶ HIGHLIGHT NOT FOUND IN DOCUMENT: {phrase}"
                position = document_view.text.casefold().find(phrase.casefold())
            document_view.buffer.cursor_position = max(0, position)
        else:
            document_view.text = rendered
            document_view.buffer.cursor_position = 0
    def emit(event, event_type):
        if packet and event_type in {"select", "reject", "clarify"}: interaction.respond(event_type)
        refresh()
        if on_event is not None: on_event(event_type)
    @bindings.add("q")
    @bindings.add("escape")
    def quit_app(event):
        if interaction.input_mode:
            interaction.input_mode = False; editor.visible = False; editor.text = ""; event.app.layout.focus(points_view); refresh()
        else: event.app.exit(result=0)
    @bindings.add("up")
    def up(event): interaction.move_point(-1); refresh()
    @bindings.add("down")
    def down(event): interaction.move_point(1); refresh()
    @bindings.add("left")
    def left(event): interaction.move_proposal(-1); refresh()
    @bindings.add("right")
    def right(event): interaction.move_proposal(1); refresh()
    def page_document(event, delta):
        """Scroll the document pane while preserving active decision state."""
        buffer = document_view.buffer
        step = max(1, len(document_view.text) // 3)
        buffer.cursor_position = max(0, min(len(document_view.text), buffer.cursor_position + delta * step))
        event.app.layout.focus(document_view)
    @bindings.add(Keys.PageUp)
    def page_up(event): page_document(event, -1)
    @bindings.add(Keys.PageDown)
    def page_down(event): page_document(event, 1)
    @bindings.add("tab")
    def toggle_document(event): interaction.switch_document()
    @bindings.add("w")
    def workplan_key(event): interaction.document_mode = "workplan"; interaction._manual_document_switch = True; refresh()
    @bindings.add("d")
    def design_key(event): interaction.document_mode = "design"; interaction._manual_document_switch = True; refresh()
    @bindings.add("enter")
    def enter(event):
        if interaction.input_mode:
            fields = [x.strip() for x in editor.text.split("|", 3)]
            try:
                if len(fields) != 4 or not fields[0] or not fields[1] or not fields[3]: raise ValueError
                proposal = Proposal("User: " + fields[0], fields[1], float(fields[2]), fields[3])
            except (ValueError, TypeError): helper_view.text = "Invalid proposal. Use label | rationale | confidence (0..1) | trade-offs"; return
            interaction.add_proposal(proposal); interaction.input_mode = False; editor.visible = False; editor.text = ""; event.app.layout.focus(points_view); emit(event, "add-proposal"); return
        emit(event, "select")
    for key, event_type in (("r", "reject"), ("c", "clarify"), ("m", "request-more-evidence"), ("s", "safe-exit"), ("o", "reopen")):
        @bindings.add(key)
        def control(event, event_type=event_type): emit(event, event_type)
    @bindings.add("a")
    def add(event):
        if event.app is None:
            emit(event, "add-proposal")
            return
        interaction.input_mode = True; editor.visible = True; event.app.layout.focus(editor); refresh()
    body = HSplit([VSplit([Frame(document_view, title="Design / Workplan"), Frame(points_view, title="Decisions and proposals")]), Frame(helper_view, title="Helper: rationale, implications, evidence"), editor, footer])
    application = Application(
        layout=Layout(body), key_bindings=bindings, full_screen=True,
        erase_when_done=True,
    )
    interaction._refresh = refresh
    refresh()
    application.awtui_panes = (document_view, points_view, helper_view); application.awtui_footer = footer; application.editor = editor; application.interaction = interaction; application.awtui_state = interaction
    return application


def build_application_from_context(context: dict, *, decisions=None, on_event=None) -> Application:
    """Build the live UI from a Coordinator/AWG context, always rendering Markdown documents."""
    documents = context.get("documents", {})
    return build_application(
        design_document=documents.get("design", "# Design document\n\nNo design document supplied."),
        workplan=documents.get("workplan", "# Workplan\n\nNo workplan supplied."),
        decisions=decisions,
        on_event=on_event,
    )


def run_application(application: Application, *, output_fn=print) -> int:
    """Run the app and report a concise status after terminal cleanup.

    prompt-toolkit restores raw mode, resize handlers, the renderer, and the
    alternate screen in its ``finally`` path. Disabling its interactive error
    screen means this boundary reports only a safe summary after that cleanup,
    without tracebacks, packet contents, prompts, or host paths.
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
        output_fn(f"TUI stopped ({type(error).__name__}); terminal restored.")
        return 1
    return int(result or 0)


def main() -> int:
    return run_application(build_application(
        design_document="# Design document\n\nDefine the service boundary and validation strategy.",
        workplan="# Workplan\n\n1. Agree boundary\n2. Stage rollout\n3. Validate outcomes",
        decisions=_standalone_demo_decisions(),
    ))
