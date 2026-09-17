from awtui.transport import LiveSessionTransport, RetryPolicy


def test_live_transport_delivers_revision_bound_event_and_acknowledges():
    events = []
    transport = LiveSessionTransport({"project_id": "p", "ar_id": "AR-25", "task_revision": 1, "packet_digest": "d", "session_id": "s"}, events.append)
    ack = transport.submit("select", point_id="p1")
    assert ack.accepted is True
    assert events[0]["sequence"] == 1


def test_live_transport_bounds_failures_and_reports_rejection():
    transport = LiveSessionTransport({"project_id": "p", "ar_id": "AR-25", "task_revision": 1, "packet_digest": "d", "session_id": "s"}, lambda _event: False, RetryPolicy(2))
    ack = transport.submit("select")
    assert ack.accepted is False
    assert ack.reason == "delivery rejected"
