from models.schemas import (
    EntityType,
    Decision,
    RiskLevel,
    GovernanceRequest,
)


def test_governance_request():
    request = GovernanceRequest(
        request_id="REQ-001",
        user_id="user-001",
        role="user",
        entity_type=EntityType.AGENT,
        prompt="Read the project documentation.",
        action="read_file",
        resource="README.md",
    )

    assert request.request_id == "REQ-001"
    assert request.entity_type == EntityType.AGENT
    assert request.action == "read_file"


def test_decision_values():
    assert Decision.ALLOW.value == "ALLOW"
    assert Decision.BLOCK.value == "BLOCK"


def test_risk_levels():
    assert RiskLevel.LOW.value == "LOW"
    assert RiskLevel.CRITICAL.value == "CRITICAL"