from approval.approval_manager import ApprovalManager

from models.schemas import (
    ApprovalStatus,
    RiskLevel
)


def create_manager():
    return ApprovalManager()


def create_request(manager):
    return manager.create_request(
        request_id="REQ-001",
        action="delete_file",
        resource="report.txt",
        risk_score=75,
        risk_level=RiskLevel.HIGH,
        reason="Protected resource modification."
    )


def test_create_approval_request():
    manager = create_manager()

    approval = create_request(
        manager
    )

    assert approval.status == (
        ApprovalStatus.PENDING
    )

    assert approval.request_id == (
        "REQ-001"
    )

    assert approval.action == (
        "delete_file"
    )


def test_get_approval_request():
    manager = create_manager()

    approval = create_request(
        manager
    )

    result = manager.get_request(
        approval.approval_id
    )

    assert result is approval


def test_approve_request():
    manager = create_manager()

    approval = create_request(
        manager
    )

    result = manager.approve(
        approval.approval_id,
        "admin-001"
    )

    assert result is True

    assert approval.status == (
        ApprovalStatus.APPROVED
    )

    assert approval.approved_by == (
        "admin-001"
    )

    assert approval.approved_at is not None


def test_deny_request():
    manager = create_manager()

    approval = create_request(
        manager
    )

    result = manager.deny(
        approval.approval_id,
        "admin-001"
    )

    assert result is True

    assert approval.status == (
        ApprovalStatus.DENIED
    )


def test_cannot_approve_twice():
    manager = create_manager()

    approval = create_request(
        manager
    )

    assert manager.approve(
        approval.approval_id,
        "admin-001"
    ) is True

    assert manager.approve(
        approval.approval_id,
        "admin-002"
    ) is False


def test_cannot_deny_after_approval():
    manager = create_manager()

    approval = create_request(
        manager
    )

    manager.approve(
        approval.approval_id,
        "admin-001"
    )

    assert manager.deny(
        approval.approval_id,
        "admin-002"
    ) is False


def test_approved_action_matches_request():
    manager = create_manager()

    approval = create_request(
        manager
    )

    manager.approve(
        approval.approval_id,
        "admin-001"
    )

    result = manager.is_approved(
        approval_id=approval.approval_id,
        request_id="REQ-001",
        action="delete_file",
        resource="report.txt"
    )

    assert result is True


def test_approval_cannot_be_reused_for_other_action():
    manager = create_manager()

    approval = create_request(
        manager
    )

    manager.approve(
        approval.approval_id,
        "admin-001"
    )

    result = manager.is_approved(
        approval_id=approval.approval_id,
        request_id="REQ-001",
        action="execute_command",
        resource="report.txt"
    )

    assert result is False


def test_approval_cannot_be_reused_for_other_resource():
    manager = create_manager()

    approval = create_request(
        manager
    )

    manager.approve(
        approval.approval_id,
        "admin-001"
    )

    result = manager.is_approved(
        approval_id=approval.approval_id,
        request_id="REQ-001",
        action="delete_file",
        resource="passwords.txt"
    )

    assert result is False


def test_pending_requests():
    manager = create_manager()

    approval1 = create_request(
        manager
    )

    approval2 = manager.create_request(
        request_id="REQ-002",
        action="send_email",
        resource="external@example.com",
        risk_score=70,
        risk_level=RiskLevel.HIGH,
        reason="External communication."
    )

    manager.approve(
        approval1.approval_id,
        "admin-001"
    )

    pending = manager.list_pending()

    assert len(pending) == 1
    assert pending[0] is approval2