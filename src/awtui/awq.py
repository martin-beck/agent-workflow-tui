"""AWQ evidence gate adapter; quality is not oracle intent."""
from __future__ import annotations

from typing import Any


def check_evidence(evidence: dict[str, Any], *, ar_id: str, task_revision: int) -> dict[str, Any]:
    required = {"ar_id", "task_revision", "kind", "status", "digest"}
    if set(evidence) != required or evidence["ar_id"] != ar_id or evidence["task_revision"] != task_revision:
        raise ValueError("evidence is not bound to the active AR revision")
    if evidence["kind"] not in {"schema", "formal", "privacy", "runtime"} or evidence["status"] not in {"pass", "fail"} or not str(evidence["digest"]).startswith("sha256:"):
        raise ValueError("invalid AWQ evidence record")
    return {"quality_evidence": evidence, "user_intent": "separate"}

