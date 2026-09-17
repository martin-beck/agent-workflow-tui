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
