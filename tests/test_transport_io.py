import io
import json

import pytest

from awtui.transport_io import read_json, read_json_file, write_json, write_json_file


def test_stdin_stdout_round_trip():
    source = io.BytesIO()
    write_json({"kind": "coordinator-tui-response", "ok": True}, source)
    source.seek(0)
    assert read_json(source)["ok"] is True


def test_text_stream_round_trip():
    source = io.StringIO()
    write_json({"ok": "ssh"}, source)
    source.seek(0)
    assert read_json(source)["ok"] == "ssh"


def test_file_transport_is_atomic_private_and_rejects_symlink(tmp_path):
    path = write_json_file({"sequence": 1}, tmp_path / "response.json")
    assert read_json_file(path)["sequence"] == 1
    if hasattr(path, "lstat"):
        assert path.stat().st_mode & 0o077 == 0
    link = tmp_path / "link.json"
    try:
        link.symlink_to(path)
    except (OSError, NotImplementedError):
        return
    with pytest.raises(ValueError, match="symlink"):
        write_json_file({"bad": True}, link)


def test_transport_rejects_oversized_or_non_object_messages():
    with pytest.raises(ValueError, match="bounded"):
        write_json({"data": "x" * 100}, io.BytesIO(), max_bytes=20)
    with pytest.raises(ValueError, match="object"):
        read_json(io.BytesIO(json.dumps([1]).encode()))
