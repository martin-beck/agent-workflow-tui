import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from awtui.awg import decision_event
from awtui.awq import check_evidence
from awtui.coordinator import CoordinatorAdapter
from awtui.discussion import DecisionResponse
from awtui.reconciliation import Reconciliation


def test_end_to_end_public_contract_trace():
    context = {"project_id": "demo", "ar_id": "AR-0011", "task_revision": 2, "packet_digest": "sha256:" + "e" * 64, "session_id": "cross-1"}
    recorded = []
    coordinator = CoordinatorAdapter(context, recorded.append)
    event = decision_event(DecisionResponse("design", "select", selected="a"), **context, sequence=1)
    coordinator.submit(event)
    quality = check_evidence({"ar_id": "AR-0011", "task_revision": 2, "kind": "formal", "status": "pass", "digest": "sha256:" + "f" * 64}, ar_id="AR-0011", task_revision=2)
    reconciliation = Reconciliation("AR-0011", 2, ("AR-0012",))
    assert recorded == [event]
    assert quality["user_intent"] == "separate"
    assert reconciliation.event_type() == "reconciled"

