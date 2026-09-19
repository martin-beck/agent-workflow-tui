import json
import os
import stat
import tarfile

import pytest
from awtui.connect import environment_fingerprint, bootstrap_runtime, runtime_archive_name, runtime_manifest, _validate_remote_path
from awtui.connect import connect


def test_environment_fingerprint_has_portable_runtime_facts():
    facts = environment_fingerprint()
    assert set(facts) == {"platform", "architecture", "python", "shell"}
    assert facts["platform"]
    assert facts["architecture"]


def test_runtime_archive_is_platform_specific_and_safely_extracted(tmp_path):
    archive = tmp_path / "runtime.tar.gz"
    payload = tmp_path / "payload"; payload.mkdir(); (payload / "bin").mkdir()
    (payload / "bin" / "awui-live").write_text("#!/bin/sh\n")
    (payload / "runtime-manifest.json").write_text(__import__("json").dumps(runtime_manifest({"platform": "linux", "architecture": "x86_64", "python": "3.12"})))
    with tarfile.open(archive, "w:gz") as bundle:
        bundle.add(payload / "bin" / "awui-live", arcname="bin/awui-live")
        bundle.add(payload / "runtime-manifest.json", arcname="runtime-manifest.json")
    destination = bootstrap_runtime(archive, tmp_path / "out", expected={"schema_version": "1", "platform": "linux", "architecture": "x86_64", "python": "3.12"})
    assert (destination / "bin/awui-live").is_file()
    assert runtime_archive_name({"platform": "windows", "architecture": "amd64"}) == "awui-windows-amd64.tar.gz"
    assert runtime_manifest({"platform": "linux", "architecture": "aarch64", "python": "3.12"})["architecture"] == "aarch64"


@pytest.mark.parametrize("path", ["relative.json", "/tmp/../escape", "/tmp/a\njson"])
def test_remote_paths_fail_closed(path):
    with pytest.raises(ValueError):
        _validate_remote_path(path)


@pytest.mark.parametrize(
    ("platform", "architecture"),
    [("linux", "x86_64"), ("windows", "amd64"), ("darwin", "arm64"), ("linux", "aarch64")],
)
def test_runtime_manifest_matrix_is_addressable(platform, architecture):
    facts = {"platform": platform, "architecture": architecture, "python": "3.12"}
    assert runtime_archive_name(facts) == f"awui-{platform}-{architecture}.tar.gz"
    manifest = runtime_manifest(facts)
    assert manifest["platform"] == platform
    assert manifest["architecture"] == architecture


@pytest.mark.parametrize("backend, executable", [("gui", "awui-live"), ("tui", "awtui-live")])
def test_connect_local_invokes_selected_backend_and_writes_result(tmp_path, monkeypatch, backend, executable):
    shim = tmp_path / executable
    shim.write_text(
        "#!/usr/bin/env python3\n"
        "import json, pathlib, sys\n"
        "a=sys.argv; req=pathlib.Path(a[a.index('--session-file')+1]); out=pathlib.Path(a[a.index('--output-json')+1])\n"
        "data=json.loads(req.read_text()); out.write_text(json.dumps({'event_type':'select','session_id':data['session_id']})+'\\n')\n",
        encoding="utf-8",
    )
    shim.chmod(shim.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ.get('PATH', '')}")
    request = tmp_path / "request.json"
    request.write_text(json.dumps({"session_id": "local-e2e"}), encoding="utf-8")
    result = tmp_path / "events.jsonl"
    assert connect(session_file=str(request), remote_event_file=str(result), backend=backend) == 0
    assert json.loads(result.read_text(encoding="utf-8"))["session_id"] == "local-e2e"
