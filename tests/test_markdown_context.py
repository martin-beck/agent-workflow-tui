from awtui.live import build_application_from_context


def test_context_documents_are_rendered_for_live_adapter_usage():
    app = build_application_from_context({"documents": {"design": "# Design\n\n**boundary**", "workplan": "# Plan\n\n- stage"}}, decisions=[{"point_id": "p", "anchor": "design:L2", "question": "Choose", "proposals": [{"label": "A"}, {"label": "B"}]}])
    assert "Design" in app.awtui_panes[0].text
    assert "# Design" not in app.awtui_panes[0].text
    app.awtui_state.switch_document()
    assert "Plan" in app.awtui_panes[0].text
    assert "# Plan" not in app.awtui_panes[0].text
