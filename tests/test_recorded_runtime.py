from awtui.live import dispatch_recorded_input


def test_recorded_terminal_input_replays_controls_until_quit():
    events = []
    assert dispatch_recorded_input("\nr mocq", events.append) == ["select", "reject", "request-more-evidence", "reopen", "clarify"]
    assert events[-1] == "clarify"
