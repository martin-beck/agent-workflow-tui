import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]


def context():
    return {"project_id": "demo", "ar_id": "AR-0005", "task_revision": 3, "packet_digest": "sha256:" + "a" * 64, "contract_versions": {"awg": "1", "coordinator": "1", "awq": "1"}, "session_id": "session-1"}


def event():
    return {**{k: context()[k] for k in ("project_id", "ar_id", "task_revision", "packet_digest", "session_id")}, "sequence": 1, "event_type": "select", "payload": {"point_id": "design", "choice": "a"}}


def run(value, kind, tmp_path):
    path = tmp_path / (kind + ".json")
    path.write_text(json.dumps(value))
    return subprocess.run([sys.executable, str(ROOT / "tools/check_envelopes.py"), str(path), kind], cwd=ROOT)


def test_context_and_event_pass(tmp_path):
    assert run(context(), "context", tmp_path).returncode == 0
    assert run(event(), "event", tmp_path).returncode == 0


def test_stale_or_cross_ar_shape_rejected(tmp_path):
    bad = event()
    bad["ar_id"] = "AR-99"
    bad["unexpected"] = True
    assert run(bad, "event", tmp_path).returncode != 0
