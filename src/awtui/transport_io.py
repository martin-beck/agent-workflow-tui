"""Bounded, shell-free JSON transport for local and SSH-hosted sessions."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, BinaryIO, TextIO

MAX_MESSAGE_BYTES = 2 * 1024 * 1024


def _encoded(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def read_json(stream: BinaryIO | TextIO, *, max_bytes: int = MAX_MESSAGE_BYTES) -> dict[str, Any]:
    """Read exactly one bounded JSON message from stdin or an SSH pipe."""
    raw = stream.buffer.read(max_bytes + 1) if hasattr(stream, "buffer") else stream.read(max_bytes + 1)
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    if len(raw) > max_bytes:
        raise ValueError("JSON transport message exceeds bounded size")
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON transport message must be an object")
    return value


def write_json(value: dict[str, Any], stream: BinaryIO | TextIO, *, max_bytes: int = MAX_MESSAGE_BYTES) -> None:
    """Write one canonical bounded JSON message to stdout or an SSH pipe."""
    raw = _encoded(value)
    if len(raw) > max_bytes:
        raise ValueError("JSON transport message exceeds bounded size")
    target = stream.buffer if hasattr(stream, "buffer") else stream
    try:
        target.write(raw)
    except TypeError:
        target.write(raw.decode("utf-8"))
    target.flush()


def write_json_file(value: dict[str, Any], path: str | Path, *, max_bytes: int = MAX_MESSAGE_BYTES) -> Path:
    """Atomically replace a private response file; safe across Windows/POSIX."""
    target = Path(path)
    if target.is_symlink():
        raise ValueError("refusing to replace symlink transport file")
    raw = _encoded(value)
    if len(raw) > max_bytes:
        raise ValueError("JSON transport message exceeds bounded size")
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        if os.name != "nt":
            temporary_path.chmod(0o600)
        os.replace(temporary_path, target)
        if os.name != "nt":
            target.chmod(0o600)
    finally:
        try:
            temporary_path.unlink()
        except FileNotFoundError:
            pass
    return target


def read_json_file(path: str | Path, *, max_bytes: int = MAX_MESSAGE_BYTES) -> dict[str, Any]:
    """Read one bounded JSON file, rejecting symlinks."""
    target = Path(path)
    if target.is_symlink():
        raise ValueError("refusing to read symlink transport file")
    with target.open("rb") as stream:
        return read_json(stream, max_bytes=max_bytes)
