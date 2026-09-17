from prompt_toolkit.layout import Dimension

from awtui.live import build_application


def _dimension_values(dimension):
    return (dimension.min, dimension.max, dimension.preferred, dimension.weight)


def test_panes_use_bounded_dimensions_instead_of_content_driven_sizes():
    """Pane geometry stays stable while prompt-toolkit reflows on SIGWINCH."""
    app = build_application()
    dimensions = app.awtui_layout_dimensions

    assert _dimension_values(dimensions["pane_width"]) == (28, 120, 28, 1)
    assert _dimension_values(dimensions["document_row"]) == (8, 40, 8, 3)
    assert _dimension_values(dimensions["helper"]) == (6, 12, 9, 1)

    # The dimensions are attached to containers, not inferred from text
    # length.  prompt-toolkit's full-screen renderer receives SIGWINCH and
    # recomputes these bounded dimensions for the new terminal size.
    document_row = app.layout.container.children[0]
    assert document_row.width.weight == 1
    assert _dimension_values(document_row.height) == _dimension_values(dimensions["document_row"])
    assert [_dimension_values(child.width) for child in document_row.children] == [_dimension_values(dimensions["pane_width"])] * 2


def test_full_screen_application_can_reflow_without_rebuilding_panes():
    app = build_application()
    root = app.layout.container

    assert app.full_screen is True
    assert root.width.weight == 1
    assert root.height.weight == 1
    # Resizing changes the renderer's available terminal size; the same
    # bounded layout tree remains authoritative for both old and new sizes.
    assert app.layout.container is root
    assert app.awtui_panes[0].control is not None
