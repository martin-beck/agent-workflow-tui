import pytest
from awtui.transport import EventAcknowledgement, RetryPolicy


def test_retry_policy_is_bounded_and_rejection_fails_closed():
    assert list(RetryPolicy(2).attempts()) == [1, 2]
    assert RetryPolicy.fail_closed(EventAcknowledgement("s", 1, False, "stale")) is True


def test_retry_policy_rejects_unbounded_configuration():
    with pytest.raises(ValueError):
        RetryPolicy(0)
