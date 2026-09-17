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
    assert transport.boundary.next_sequence == 1


def test_failed_delivery_does_not_consume_sequence_before_retry():
    delivered = []

    def receiver(event):
        delivered.append(event)
        return len(delivered) > 1

    transport = LiveSessionTransport(
        {"project_id": "p", "ar_id": "AR-25", "task_revision": 1, "packet_digest": "d", "session_id": "s"},
        receiver,
        RetryPolicy(1),
    )
    assert transport.submit("select").accepted is False
    retry = transport.submit("select")
    assert retry.accepted is True
    assert [event["sequence"] for event in delivered] == [1, 1]
    assert transport.boundary.next_sequence == 2
