import tarfile

from awtui.connect import environment_fingerprint, bootstrap_runtime, runtime_archive_name


def test_environment_fingerprint_has_portable_runtime_facts():
    facts = environment_fingerprint()
    assert set(facts) == {"platform", "architecture", "python", "shell"}
    assert facts["platform"]
    assert facts["architecture"]


def test_runtime_archive_is_platform_specific_and_safely_extracted(tmp_path):
    archive = tmp_path / "runtime.tar.gz"
    payload = tmp_path / "payload"; payload.mkdir(); (payload / "bin").mkdir()
    (payload / "bin" / "awui-live").write_text("#!/bin/sh\n")
    with tarfile.open(archive, "w:gz") as bundle:
        bundle.add(payload / "bin" / "awui-live", arcname="bin/awui-live")
    destination = bootstrap_runtime(archive, tmp_path / "out")
    assert (destination / "bin/awui-live").is_file()
    assert runtime_archive_name({"platform": "windows", "architecture": "amd64"}) == "awui-windows-amd64.tar.gz"
