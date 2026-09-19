import os

import pytest

pytest.importorskip("PySide6")

from awtui.gui import build_gui_application


def test_gui_actions_have_accessible_names_and_supplemental_help(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    window = build_gui_application()
    buttons = window.window.findChildren(window.QtWidgets.QPushButton)
    assert {button.text() for button in buttons} >= {"Select", "Reject", "Clarify", "Save", "Save + Exit"}
    assert all(button.accessibleName() for button in buttons)
    assert all(button.toolTip() for button in buttons)
    window.window.close()
