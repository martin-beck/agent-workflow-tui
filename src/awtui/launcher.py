"""Environment-aware GUI/TUI selection for Coordinator handoff."""
from __future__ import annotations

import os


def detect_ui_backend(*, environ: dict[str, str] | None = None) -> str:
    env = os.environ if environ is None else environ
    if env.get("AWUI_BACKEND") in {"gui", "tui"}:
        return env["AWUI_BACKEND"]
    if env.get("DISPLAY") or env.get("WAYLAND_DISPLAY"):
        return "gui"
    return "tui"


def command_for_environment(*, environ: dict[str, str] | None = None, session_file: str | None = None) -> list[str]:
    command = "awui-live" if detect_ui_backend(environ=environ) == "gui" else "awtui-live"
    return [command, "--session-file", session_file] if session_file else [command]


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(prog="awui-live")
    parser.add_argument("--session-file")
    args = parser.parse_args()
    if detect_ui_backend() == "tui":
        from .live import main as tui_main
        return int(tui_main(["--session-file", args.session_file] if args.session_file else []))
    if args.session_file:
        from .awg import envelope_requests_to_tui
        from .gui import build_gui_application
        from .host import attach_session
        request = attach_session(args.session_file)
        _context, decisions = envelope_requests_to_tui(request, project_id=request["project_id"], session_id=request["session_id"], documents=request.get("documents"))
        window = build_gui_application(
            design_document=(request.get("documents") or {}).get("design", "# Design\n\nAwaiting context"),
            workplan=(request.get("documents") or {}).get("workplan", "# Work plan\n\nAwaiting context"),
            decisions=decisions,
        )
        return window.run()
    from .gui import main as gui_main
    return int(gui_main())


if __name__ == "__main__":
    raise SystemExit(main())
