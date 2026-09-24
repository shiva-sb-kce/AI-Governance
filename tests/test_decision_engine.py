from core.decision_engine import DecisionEngine
from models.schemas import (
    Decision,
    PermissionResult,
    PolicyResult
)


def make_risk(score):
    return {
        "risk_score": score
    }


def test_low_risk_allows():
    engine = DecisionEngine()

    policy = PolicyResult()

    result = engine.decide(
        policy_result=policy,
        risk_result=make_risk(10)
    )

    assert result == Decision.ALLOW


def test_medium_risk_monitors():
    engine = DecisionEngine()

    policy = PolicyResult()

    result = engine.decide(
        policy_result=policy,
        risk_result=make_risk(40)
    )

    assert result == Decision.MONITOR


def test_high_risk_requires_approval():
    engine = DecisionEngine()

    policy = PolicyResult()

    result = engine.decide(
        policy_result=policy,
        risk_result=make_risk(70)
    )

    assert result == Decision.APPROVAL


def test_critical_risk_blocks():
    engine = DecisionEngine()

    policy = PolicyResult()

    result = engine.decide(
        policy_result=policy,
        risk_result=make_risk(90)
    )

    assert result == Decision.BLOCK


def test_block_policy_overrides_low_risk():
    engine = DecisionEngine()

    policy = PolicyResult(
        mandatory_decision=Decision.BLOCK
    )

    result = engine.decide(
        policy_result=policy,
        risk_result=make_risk(10)
    )

    assert result == Decision.BLOCK


def test_permission_denial_blocks():
    engine = DecisionEngine()

    policy = PolicyResult()

    permission = PermissionResult(
        allowed=False,
        permission="DENY"
    )

    result = engine.decide(
        policy_result=policy,
        risk_result=make_risk(10),
        permission_result=permission
    )

    assert result == Decision.BLOCK


def test_policy_approval_overrides_low_risk():
    engine = DecisionEngine()

    policy = PolicyResult(
        mandatory_decision=Decision.APPROVAL
    )

    result = engine.decide(
        policy_result=policy,
        risk_result=make_risk(10)
    )

    assert result == Decision.APPROVAL


def test_permission_approval():
    engine = DecisionEngine()

    policy = PolicyResult()

    permission = PermissionResult(
        allowed=False,
        requires_approval=True,
        permission="APPROVAL"
    )

    result = engine.decide(
        policy_result=policy,
        risk_result=make_risk(10),
        permission_result=permission
    )

    assert result == Decision.APPROVAL


def test_block_has_priority_over_permission_approval():
    engine = DecisionEngine()

    policy = PolicyResult(
        mandatory_decision=Decision.BLOCK
    )

    permission = PermissionResult(
        allowed=False,
        requires_approval=True,
        permission="APPROVAL"
    )

    result = engine.decide(
        policy_result=policy,
        risk_result=make_risk(70),
        permission_result=permission
    )

    assert result == Decision.BLOCK
def test_critical_risk_overrides_permission_approval():

    engine = DecisionEngine()

    policy_result = PolicyResult()

    risk_result = {
        "risk_score": 90
    }

    permission_result = PermissionResult(
        allowed=False,
        requires_approval=True,
        permission="APPROVAL",
        role="ADMIN",
        action="execute_command"
    )

    result = engine.decide(
        policy_result,
        risk_result,
        permission_result
    )

    assert result == Decision.BLOCK
def test_high_risk_approval_remains_approval():

    engine = DecisionEngine()

    policy_result = PolicyResult()

    risk_result = {
        "risk_score": 80
    }

    permission_result = PermissionResult(
        allowed=False,
        requires_approval=True,
        permission="APPROVAL",
        role="ADMIN",
        action="delete_file"
    )

    result = engine.decide(
        policy_result,
        risk_result,
        permission_result
    )

    assert result == Decision.APPROVAL