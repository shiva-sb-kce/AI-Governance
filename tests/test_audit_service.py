from services.audit_service import AuditService

from models.schemas import (
    EntityType,
    Decision,
    RiskLevel,
    ApprovalStatus
)


def test_audit_event_is_created():

    service = AuditService()

    event = service.log_event(
        request_id="REQ-001",
        entity_type=EntityType.AGENT,
        entity_id="agent-001",
        action="write_file",
        risk_score=25,
        risk_level=RiskLevel.LOW,
        decision=Decision.APPROVAL,
        threats=[],
        policies=["POLICY-001"],
        approval_status=ApprovalStatus.PENDING,
        details={
            "resource": "test.txt"
        }
    )

    assert event is not None
    assert event.audit_id.startswith("AUD-")
    assert event.request_id == "REQ-001"
    assert event.entity_id == "agent-001"
    assert event.action == "write_file"
    assert event.risk_score == 25
    assert event.decision == Decision.APPROVAL


def test_recent_events():

    service = AuditService()

    for i in range(5):

        service.log_event(
            request_id=f"REQ-{i}",
            entity_type=EntityType.AGENT,
            entity_id="agent-001",
            action="read_file",
            risk_score=10,
            risk_level=RiskLevel.LOW,
            decision=Decision.ALLOW
        )

    events = service.get_recent(3)

    assert len(events) == 3


def test_get_by_request():

    service = AuditService()

    service.log_event(
        request_id="REQ-001",
        entity_type=EntityType.AGENT,
        entity_id="agent-001",
        action="read_file",
        risk_score=10,
        risk_level=RiskLevel.LOW,
        decision=Decision.ALLOW
    )

    service.log_event(
        request_id="REQ-002",
        entity_type=EntityType.AGENT,
        entity_id="agent-001",
        action="write_file",
        risk_score=25,
        risk_level=RiskLevel.LOW,
        decision=Decision.APPROVAL
    )

    events = service.get_by_request(
        "REQ-001"
    )

    assert len(events) == 1
    assert events[0].request_id == "REQ-001"


def test_get_by_decision():

    service = AuditService()

    service.log_event(
        request_id="REQ-001",
        entity_type=EntityType.AGENT,
        entity_id="agent-001",
        action="write_file",
        risk_score=50,
        risk_level=RiskLevel.MEDIUM,
        decision=Decision.BLOCK
    )

    events = service.get_by_decision(
        Decision.BLOCK
    )

    assert len(events) == 1
    assert events[0].decision == Decision.BLOCK


def test_clear_events():

    service = AuditService()

    service.log_event(
        request_id="REQ-001",
        entity_type=EntityType.USER,
        entity_id="user-001",
        action=None,
        risk_score=0,
        risk_level=RiskLevel.LOW,
        decision=Decision.ALLOW
    )

    assert len(
        service.get_events()
    ) == 1

    service.clear()

    assert len(
        service.get_events()
    ) == 0