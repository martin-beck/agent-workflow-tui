from awtui.live import build_application


def test_prompt_toolkit_application_has_two_panes_and_quit_binding():
    app = build_application(document="design:42", points="design [unresolved]")
    assert app.full_screen is True
    assert any(any(str(key) == "q" for key in binding.keys) for binding in app.key_bindings.bindings)
    assert [pane.text for pane in app.awtui_panes] == ["design:42", "design [unresolved]"]
