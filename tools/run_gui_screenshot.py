#!/usr/bin/env python3
"""Capture a redacted initial GUI decision batch for CI documentation."""
from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from awtui.gui import build_gui_application
from awtui.live import _standalone_demo_decisions


def main() -> int:
    target = Path(os.environ.get("AWUI_GUI_SCREENSHOT", "artifacts/gui-batch.png"))
    target.parent.mkdir(parents=True, exist_ok=True)
    window = build_gui_application(
        design_document="# Design\n\n## Boundary\nReview the service boundary.",
        workplan="# Work plan\n\n## Rollout\nValidate the rollout step.",
        decisions=_standalone_demo_decisions(),
    )
    window.window.show()
    window.app.processEvents()
    if not window.window.grab().save(str(target), "PNG"):
        raise RuntimeError("GUI screenshot could not be written")
    window.window.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
