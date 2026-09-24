from core.risk_engine import RiskEngine
from models.schemas import (
    InspectionResult,
    PolicyResult,
    PermissionResult,
    RiskLevel
)


def test_safe_request_has_low_risk():
    engine = RiskEngine()

    inspection = InspectionResult()

    policy = PolicyResult()

    result = engine.calculate(
        inspection_result=inspection,
        policy_result=policy
    )

    assert result["risk_score"] == 0
    assert result["risk_level"] == RiskLevel.LOW


def test_injection_increases_threat_score():
    engine = RiskEngine()

    inspection = InspectionResult(
        injection_detected=True
    )

    policy = PolicyResult(
        violated_policies=["POLICY-001"]
    )

    result = engine.calculate(
        inspection_result=inspection,
        policy_result=policy
    )

    assert result["threat_score"] == 25
    assert result["risk_score"] == 25


def test_pii_increases_data_score():
    engine = RiskEngine()

    inspection = InspectionResult(
        pii_detected=True
    )

    policy = PolicyResult(
        violated_policies=["POLICY-003"]
    )

    result = engine.calculate(
        inspection_result=inspection,
        policy_result=policy
    )

    assert result["data_score"] == 15
    assert result["risk_score"] == 15


def test_secret_has_high_data_risk():
    engine = RiskEngine()

    inspection = InspectionResult(
        secret_detected=True,
        pii_detected=True
    )

    policy = PolicyResult(
        violated_policies=["POLICY-006"]
    )

    result = engine.calculate(
        inspection_result=inspection,
        policy_result=policy
    )

    assert result["data_score"] == 25
    assert result["risk_score"] == 25


def test_denied_permission_increases_risk():
    engine = RiskEngine()

    inspection = InspectionResult()

    policy = PolicyResult()

    permission = PermissionResult(
        allowed=False,
        permission="DENY"
    )

    result = engine.calculate(
        inspection_result=inspection,
        policy_result=policy,
        permission_result=permission
    )

    assert result["permission_score"] == 25
    assert result["risk_score"] == 25


def test_approval_permission():
    engine = RiskEngine()

    inspection = InspectionResult()

    policy = PolicyResult()

    permission = PermissionResult(
        allowed=False,
        requires_approval=True,
        permission="APPROVAL"
    )

    result = engine.calculate(
        inspection_result=inspection,
        policy_result=policy,
        permission_result=permission
    )

    assert result["permission_score"] == 15


def test_action_risk_is_capped():
    engine = RiskEngine()

    inspection = InspectionResult()

    policy = PolicyResult()

    result = engine.calculate(
        inspection_result=inspection,
        policy_result=policy,
        action_risk=100
    )

    assert result["action_score"] == 25


def test_critical_risk():
    engine = RiskEngine()

    inspection = InspectionResult(
        injection_detected=True,
        pii_detected=True,
        secret_detected=True
    )

    policy = PolicyResult(
        violated_policies=[
            "POLICY-001",
            "POLICY-006"
        ]
    )

    permission = PermissionResult(
        allowed=False,
        permission="DENY"
    )

    result = engine.calculate(
        inspection_result=inspection,
        policy_result=policy,
        permission_result=permission,
        action_risk=25
    )

    assert result["risk_score"] == 100
    assert result["risk_level"] == RiskLevel.CRITICAL