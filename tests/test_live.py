from awtui.live import build_application


def test_prompt_toolkit_application_has_two_panes_and_quit_binding():
    app = build_application(document="design:42", points="design [unresolved]", helper="confidence=.8; impact=bounded")
    assert app.full_screen is True
    assert any(any(str(key) == "q" for key in binding.keys) for binding in app.key_bindings.bindings)
    assert [pane.text for pane in app.awtui_panes] == ["design:42", "design [unresolved]", "confidence=.8; impact=bounded"]


def test_live_controls_emit_explicit_event_types():
    events = []
    app = build_application(on_event=events.append)
    class Event:
        app = None
    for key, expected in (("enter", "select"), ("r", "reject"), ("c", "clarify"), ("m", "request-more-evidence"), ("a", "add-proposal"), ("s", "safe-exit"), ("o", "reopen")):
        binding = next(binding for binding in app.key_bindings.bindings if (str(binding.keys[0]) == key or (key == "enter" and str(binding.keys[0]) == "Keys.ControlM")))
        binding.handler(Event())
        assert events[-1] == expected


def test_live_navigation_switches_documents_and_tracks_decision_anchor():
    app = build_application(
        workplan="WORKPLAN: ship parser",
        design_document="DESIGN: parser boundary",
        decisions=[
            {"point_id": "parser", "anchor": "design:L12", "question": "Which parser?",
             "proposals": [{"label": "strict", "rationale": "bounded", "tradeoffs": "migration", "confidence": .8},
                           {"label": "permissive", "rationale": "compatible", "tradeoffs": "ambiguity", "confidence": .6}],
             "helper": "Impact: changes validation."},
            {"point_id": "rollout", "anchor": "plan:L4", "question": "How roll out?",
             "proposals": [{"label": "canary"}, {"label": "direct"}], "helper": "Impact: changes blast radius."},
        ],
    )
    state = app.awtui_state
    assert state.document_mode == "design"
    assert "▶ parser" in app.awtui_panes[1].text
    assert "Anchor: design:L12" in app.awtui_panes[2].text
    state.move(1)
    assert "▶ rollout" in app.awtui_panes[1].text
    assert "Anchor: plan:L4" in app.awtui_panes[2].text
    state.next_proposal(1)
    assert "Proposal 2/2: direct" in app.awtui_panes[2].text
    state.switch_document()
    assert state.document_mode == "workplan"
    assert app.awtui_panes[0].text == "WORKPLAN: ship parser"


def test_live_footer_advertises_document_and_focus_controls():
    app = build_application(workplan="plan", design_document="design", decisions=[])
    footer = app.awtui_footer.text
    assert "tab/w/d: workplan/design" in footer
    assert "↑/↓: decision" in footer
    assert "←/→: proposal" in footer


def test_live_application_erases_final_frame_on_terminal_exit():
    app = build_application()
    assert app.erase_when_done is True


def test_run_application_reports_only_safe_status_after_interrupt():
    from awtui.live import run_application

    class Interrupted:
        def run(self, **_kwargs):
            raise KeyboardInterrupt

    output = []
    assert run_application(Interrupted(), output_fn=output.append) == 130
    assert output == ["TUI interrupted; terminal restored."]


def test_run_application_redacts_exception_details():
    from awtui.live import run_application

    class Broken:
        def run(self, **_kwargs):
            raise RuntimeError("private prompt /srv/secret")

    output = []
    assert run_application(Broken(), output_fn=output.append) == 1
    assert output == ["TUI stopped (RuntimeError); terminal restored."]
    assert "/srv/secret" not in output[0]
