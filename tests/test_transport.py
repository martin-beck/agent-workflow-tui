from awtui.transport import EventAcknowledgement, SessionEnvelope


def test_envelope_and_ack_preserve_session_correlation():
    envelope = SessionEnvelope("p", "AR-27", 2, "digest", "session", 1, "select")
    assert envelope.as_event(point_id="p1")["task_revision"] == 2
    assert EventAcknowledgement("session", 1, True).as_dict()["accepted"] is True
