"""Safe local host handoff for Coordinator-owned TUI sessions."""
from __future__ import annotations

import json
import os
import shlex
import stat
import sys
from pathlib import Path
from typing import Any

LAUNCH_MODES = {"inline", "tty", "tmux", "manual"}
MAX_SESSION_BYTES = 2 * 1024 * 1024


def detect_launch_mode(*, environ: dict[str, str] | None = None, stdin_tty: bool | None = None, stdout_tty: bool | None = None) -> str:
    """Select a host mode without executing host commands."""
    env = os.environ if environ is None else environ
    requested = env.get("AWTUI_LAUNCH_MODE", "").lower()
    if requested in LAUNCH_MODES:
        return requested
    if env.get("TMUX"):
        return "tmux"
    in_tty = sys.stdin.isatty() if stdin_tty is None else stdin_tty
    out_tty = sys.stdout.isatty() if stdout_tty is None else stdout_tty
    return "tty" if in_tty and out_tty else "manual"


def write_session_file(request: dict[str, Any], directory: str | Path) -> Path:
    """Write a Coordinator request with private permissions and bounded size."""
    if request.get("kind") != "coordinator-tui-request" or request.get("schema_version") != "1.0":
        raise ValueError("only coordinator-tui-request schema 1.0 may be attached")
    session_id = request.get("session_id")
    safe = isinstance(session_id, str) and session_id and all(c.isalnum() or c in "._-" for c in session_id)
    if not safe:
        raise ValueError("session_id is not a safe filename component")
    encoded = json.dumps(request, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(encoded) > MAX_SESSION_BYTES:
        raise ValueError("session request exceeds bounded session-file size")
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"awtui-{session_id}.json"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded)
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise
    return path


def attach_session(path: str | Path) -> dict[str, Any]:
    """Read and validate the minimal host handoff envelope."""
    candidate = Path(path)
    data = candidate.read_bytes()
    if len(data) > MAX_SESSION_BYTES:
        raise ValueError("session file exceeds bounded size")
    if stat.S_IMODE(candidate.stat().st_mode) & 0o077:
        raise ValueError("session file must not be group/world accessible")
    value = json.loads(data.decode("utf-8"))
    if value.get("kind") != "coordinator-tui-request" or value.get("schema_version") != "1.0":
        raise ValueError("unsupported session request")
    return value


def append_event(path: str | Path, event: dict[str, Any]) -> None:
    """Append one bounded revision-bound event to a private session journal."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    current = target.stat().st_size if target.exists() else 0
    if current + len(encoded) > MAX_SESSION_BYTES:
        raise ValueError("session event journal exceeds bounded size")
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    fd = os.open(target, flags, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if target.exists() and stat.S_IMODE(target.stat().st_mode) & 0o077:
            target.chmod(0o600)


def launch_argv(mode: str, session_file: str | Path) -> list[str] | None:
    """Return an argv for a host launcher, or None for manual handoff."""
    if mode not in LAUNCH_MODES:
        raise ValueError("unknown launch mode")
    if mode == "manual":
        return None
    command = ["awtui-live", "--session-file", str(session_file)]
    return ["tmux", "new-window", *command] if mode == "tmux" else command


def handoff_message(mode: str, session_file: str | Path, *, summary: str) -> str:
    """Render a concise user-facing handoff without launching a process."""
    if mode not in LAUNCH_MODES:
        raise ValueError("unknown launch mode")
    command = shlex.join(["awtui-live", "--session-file", str(session_file)])
    if mode == "manual":
        action = f"Run in a user-controlled terminal:\n  {command}"
    elif mode == "tmux":
        action = f"Open a configured tmux window with:\n  {shlex.join(launch_argv(mode, session_file) or [])}"
    else:
        action = "The configured terminal host can launch the TUI in the current session."
    return f"HUMAN DECISION REQUIRED\n{summary}\n{action}\nWaiting for Coordinator acceptance."
