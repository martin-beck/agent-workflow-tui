import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from awtui.app import run_screen


class Screen:
    def __init__(self):
        self.calls = []

    def getmaxyx(self):
        return (24, 80)

    def erase(self):
        self.calls.append("erase")

    def addnstr(self, *args):
        self.calls.append(args)

    def refresh(self):
        self.calls.append("refresh")

    def keypad(self, value):
        self.calls.append(("keypad", value))


def test_shell_quits_and_draws():
    screen = Screen()
    assert run_screen(screen, input_fn=lambda: ord("q")) == 0
    assert "refresh" in screen.calls


def test_shell_is_bounded():
    screen = Screen()
    assert run_screen(screen, input_fn=lambda: ord("x"), max_steps=2) == 2


def test_packet_preserves_ranked_proposals_and_identity():
    from awtui.discussion import DiscussionPacket, PacketPoint, Proposal
    point = PacketPoint("design", "design:42", "Which path?", (Proposal("a", "small", .8, "less scope"), Proposal("b", "safe", .6, "more work")), "downstream impact", "needs runtime evidence")
    packet = DiscussionPacket("AR-0004", 2, (point,))
    assert packet.active().point_id == "design"
    assert packet.active().evidence_gap == "needs runtime evidence"


def test_decision_session_keeps_responses_per_point_and_evaluates_added_proposal():
    from awtui.discussion import DecisionResponse, DecisionSession, DiscussionPacket, PacketPoint, Proposal
    proposals = (Proposal("a", "small", .8, "less scope"), Proposal("b", "safe", .6, "more work"))
    packet = DiscussionPacket("AR-0005", 2, (PacketPoint("design", "design:42", "Which?", proposals, "impact"), PacketPoint("storage", "plan:8", "Where?", proposals, "impact")))
    session = DecisionSession(packet)
    session.respond(DecisionResponse("design", "select", selected="a", user_proposal=Proposal("c", "user", .5, "tradeoff"), user_proposal_evaluated=True))
    assert session.unanswered() == ("storage",)


def test_journal_save_and_stale_resume_rejection(tmp_path):
    from awtui.journal import resume, save
    path = tmp_path / "session.json"
    value = {"project_id": "demo", "ar_id": "AR-0006", "task_revision": 3, "packet_digest": "sha256:" + "b" * 64, "responses": {"design": {"selected": "a"}}, "unresolved": ["storage"], "future_requests": [{"text": "security", "ar_ref": "AR-0009"}]}
    save(path, value)
    assert resume(path, project_id="demo", ar_id="AR-0006", task_revision=3, packet_digest=value["packet_digest"])["unresolved"] == ["storage"]
    try:
        resume(path, project_id="demo", ar_id="AR-0006", task_revision=4, packet_digest=value["packet_digest"])
    except ValueError as error:
        assert "stale" in str(error)
    else:
        raise AssertionError("stale journal was accepted")


def test_contradiction_requires_targeted_reopen():
    from awtui.reconciliation import Reconciliation
    reopened = Reconciliation("AR-0007", 4, ("AR-0008",), ("revision conflict",), "discussion-required")
    assert reopened.event_type() == "reopen"
    try:
        Reconciliation("AR-0007", 4, ("AR-0008",), ("revision conflict",), "reconciled")
    except ValueError as error:
        assert "contradictions" in str(error)
    else:
        raise AssertionError("contradictory reconciliation was accepted")


def test_awg_event_preserves_explicit_decision_authority():
    from awtui.awg import decision_event
    from awtui.discussion import DecisionResponse
    value = decision_event(DecisionResponse("design", "select", selected="a"), project_id="demo", ar_id="AR-0009", task_revision=2, packet_digest="sha256:" + "c" * 64, session_id="s", sequence=1)
    assert value["event_type"] == "select"
    assert value["payload"]["point_id"] == "design"
    assert "implementation" not in value["payload"]
