"""Atomic, revision-bound public session journal."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def save(path: Path, session: dict[str, Any]) -> None:
    required = {"project_id", "ar_id", "task_revision", "packet_digest", "responses", "unresolved", "future_requests"}
    if set(session) != required or not isinstance(session["responses"], dict) or not isinstance(session["unresolved"], list) or not isinstance(session["future_requests"], list):
        raise ValueError("incomplete public session journal")
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(session, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def resume(path: Path, *, project_id: str, ar_id: str, task_revision: int, packet_digest: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    for key, expected in (("project_id", project_id), ("ar_id", ar_id), ("task_revision", task_revision), ("packet_digest", packet_digest)):
        if value.get(key) != expected:
            raise ValueError(f"stale journal {key}")
    return value


def render_history(session: dict[str, Any]) -> str:
    """Render public journal state for the helper pane without private transcripts."""
    lines = [f"Journal {session['ar_id']} revision {session['task_revision']}"]
    lines.append(f"answered: {len(session['responses'])}")
    lines.append(f"unresolved: {', '.join(session['unresolved']) or 'none'}")
    requests = session["future_requests"]
    lines.append("future ARs: " + (", ".join(requests) if requests else "none"))
    return "\n".join(lines)
