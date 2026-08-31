from harness.policy.policy_decision import PolicyDecision


def test_policy_decision_has_expected_values():
    assert PolicyDecision.ALLOW.value == "allow"
    assert PolicyDecision.ASK.value == "ask"
    assert PolicyDecision.DENY.value == "deny"


def test_policy_decision_is_string_compatible():
    assert PolicyDecision.ALLOW == "allow"
    assert PolicyDecision.ASK == "ask"
    assert PolicyDecision.DENY == "deny"