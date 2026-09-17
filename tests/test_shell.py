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
