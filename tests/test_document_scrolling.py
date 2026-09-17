from awtui.live import build_application


def _binding(app, key):
    """Return a binding by its prompt-toolkit key name."""
    return next(
        binding
        for binding in app.key_bindings.bindings
        if any(str(candidate) == key for candidate in binding.keys)
    )


class _Event:
    def __init__(self, app):
        self.app = app


def _decisions():
    return [
        {
            "point_id": "boundary",
            "anchor": "design:L3",
            "highlight": "Boundary phrase",
            "question": "Which boundary?",
            "proposals": [{"label": "A"}, {"label": "B"}],
        },
        {
            "point_id": "rollout",
            "anchor": "workplan:L80",
            "highlight": "Rollout phrase",
            "question": "Which rollout?",
            "proposals": [{"label": "Canary"}, {"label": "Direct"}],
        },
    ]


def _long_document():
    lines = ["# Design document", "", "Boundary phrase"]
    lines.extend(f"filler line {index}" for index in range(4, 80))
    lines.append("Rollout phrase")
    lines.extend(f"tail line {index}" for index in range(81, 150))
    return "\n".join(lines)


def test_active_decision_seeks_its_highlight_in_rendered_document():
    app = build_application(
        design_document=_long_document(),
        workplan="# Workplan\n\nRollout phrase",
        decisions=_decisions(),
    )

    document = app.awtui_panes[0]
    first_position = document.buffer.cursor_position
    first_phrase = document.text.index("Boundary phrase")
    assert first_position == first_phrase

    app.awtui_state.move(1)

    second_position = document.buffer.cursor_position
    second_phrase = document.text.index("Rollout phrase")
    assert app.awtui_state.point.point_id == "rollout"
    assert second_position == second_phrase
    assert second_position > first_position


def test_page_navigation_moves_document_without_changing_active_highlight():
    app = build_application(
        design_document=_long_document(),
        workplan="# Workplan\n\nRollout phrase",
        decisions=_decisions(),
    )
    document = app.awtui_panes[0]
    app.awtui_state.move(1)
    anchored_position = document.buffer.cursor_position

    page_down = _binding(app, "Keys.PageDown")
    page_up = _binding(app, "Keys.PageUp")
    page_down.handler(_Event(app))
    paged_position = document.buffer.cursor_position
    assert paged_position > anchored_position
    assert app.awtui_state.point.point_id == "rollout"
    assert "Rollout phrase" in document.text

    page_up.handler(_Event(app))
    assert document.buffer.cursor_position == anchored_position
    assert app.awtui_state.point.point_id == "rollout"


def test_footer_advertises_document_page_navigation():
    app = build_application(
        design_document="# Design\n\nBoundary phrase",
        workplan="# Workplan\n\nRollout phrase",
        decisions=_decisions(),
    )
    footer = app.awtui_footer.text.lower()
    assert "page-up" in footer or "pageup" in footer
    assert "page-down" in footer or "pagedown" in footer
