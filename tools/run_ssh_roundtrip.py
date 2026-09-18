#!/usr/bin/env python3
"""Exercise a revision-bound request/response over an SSH file round trip.

The script intentionally performs no UI interaction.  It validates the same
transport and Coordinator projection used after a human GUI/TUI session, and
is suitable for an ephemeral CI sshd as well as a manually prepared test host.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from awtui.bridge import tui_to_coordinator_response
from awtui.transport_io import read_json_file, write_json_file


def _remote_path(path: str) -> str:
    if not re.fullmatch(r"/[A-Za-z0-9._/-]+", path):
        raise ValueError("remote path must be an absolute, single-line path")
    return path


def _run(command: list[str], *, input_text: str | None = None) -> str:
    result = subprocess.run(
        command,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"transport command failed ({result.returncode})")
    return result.stdout


def run_roundtrip(*, host: str, port: int, user: str, identity: str, remote_dir: str, insecure: bool) -> dict[str, object]:
    if not host or any(char in host for char in "\r\n;&|`$"):
        raise ValueError("host must be a plain SSH alias or hostname")
    if not user or any(char in user for char in "\r\n;&|`$"):
        raise ValueError("user must be a plain SSH username")
    remote_root = _remote_path(remote_dir).rstrip("/")
    remote_request = f"{remote_root}/awui-roundtrip-request.json"
    remote_response = f"{remote_root}/awui-roundtrip-response.json"
    ssh_options = ["-p", str(port), "-i", identity, "-o", "BatchMode=yes"]
    # ``-O`` keeps the fixture compatible with minimal ephemeral sshd configs
    # that expose the classic remote-copy protocol but no SFTP subsystem.
    scp_options = ["-O", "-P", str(port), "-i", identity, "-o", "BatchMode=yes"]
    if insecure:
        ssh_options += ["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null"]
        scp_options += ["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null"]
    destination = f"{user}@{host}"
    request = {
        "schema_version": "1.0",
        "kind": "coordinator-tui-request",
        "project_id": "ssh-roundtrip",
        "session_id": "AWTUI-SSH-ROUNDTRIP",
        "ar": {"ar_id": "AR-0099", "task_revision": 4, "status": "open", "description": "synthetic", "specification": {}},
        "interaction": {"interaction_required": True, "decision_request_ref": "AWG-SSH-ROUNDTRIP", "decision_status": "pending", "trigger": "decision"},
        "guidance_request": {"schema_version": "0.2", "request_id": "AWG-SSH-ROUNDTRIP", "context": {}, "formal_check": {}, "candidates": [{"candidate_id": "candidate-a", "label": "Use the reviewed path"}]},
    }
    event = {
        "session_id": request["session_id"],
        "sequence": 1,
        "event_type": "select",
        "payload": {"point_id": "AWG-SSH-ROUNDTRIP", "disposition": "select", "selected": "Use the reviewed path", "selected_candidate": "candidate-a"},
    }
    with tempfile.TemporaryDirectory(prefix="awui-ssh-roundtrip-") as directory:
        local_request = Path(directory) / "request.json"
        local_response = Path(directory) / "response.json"
        write_json_file(request, local_request)
        _run(["ssh", *ssh_options, destination, "mkdir", "-p", remote_root])
        _run(["scp", *scp_options, str(local_request), f"{destination}:{remote_request}"])
        fetched = _run(["ssh", *ssh_options, destination, "cat", "--", remote_request])
        if json.loads(fetched) != request:
            raise RuntimeError("remote request differs from the revision-bound request")
        response = tui_to_coordinator_response(request, event, description_append="\nSelected candidate-a.")
        write_json_file(response, local_response)
        _run(["scp", *scp_options, str(local_response), f"{destination}:{remote_response}"])
        returned = json.loads(_run(["ssh", *ssh_options, destination, "cat", "--", remote_response]))
        if returned != read_json_file(local_response):
            raise RuntimeError("returned response differs from the Coordinator response")
        if returned["ar_update"]["decision_status"] != "resolved":
            raise RuntimeError("selected decision did not resolve the AR update")
        _run(["ssh", *ssh_options, destination, "rm", "-f", remote_request, remote_response])
    return {"host": host, "port": port, "ar_id": request["ar"]["ar_id"], "sequence": event["sequence"], "status": "resolved"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--identity", required=True)
    parser.add_argument("--remote-dir", required=True)
    parser.add_argument("--insecure-host-key-check", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(run_roundtrip(host=args.host, port=args.port, user=args.user, identity=args.identity, remote_dir=args.remote_dir, insecure=args.insecure_host_key_check), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
