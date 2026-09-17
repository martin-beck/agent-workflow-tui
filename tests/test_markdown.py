import pytest
from awtui.markdown import render_markdown


def test_markdown_renderer_formats_headings_and_lists_for_terminal_pane():
    rendered = render_markdown("# Design\n\n- boundary\n- rollback")
    assert "Design" in rendered
    assert "boundary" in rendered and "rollback" in rendered
    assert "# Design" not in rendered


def test_markdown_renderer_rejects_non_text_documents():
    with pytest.raises(TypeError):
        render_markdown(None)
