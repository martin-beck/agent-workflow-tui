from awtui.discussion import render_guardrails


def test_guardrails_keep_authority_and_evidence_distinct():
    text = render_guardrails(authority="oracle", evidence_gap="no rollout data", limitations="not an implementation review")
    assert "authority: oracle" in text
    assert "request-more-evidence" in text
    assert "decision is human intent" in text
