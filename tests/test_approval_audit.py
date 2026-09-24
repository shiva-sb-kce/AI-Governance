from agents.executor import SecureExecutor
from approval.approval_manager import ApprovalManager
from approval.approval_workflow import ApprovalWorkflow
from audit.audit_logger import AuditLogger

from models.schemas import (
    ActionRequest,
    Decision,
    GovernanceResult,
    RiskLevel
)


def make_action(
    tool="write_file",
    resource="approved.txt"
):
    return ActionRequest(
        action_id="ACT-100",
        request_id="REQ-100",
        agent_id="admin-001",
        tool=tool,
        resource=resource,
        parameters={
            "content": "Approved content"
        }
    )


def make_governance():
    return GovernanceResult(
        request_id="REQ-100",
        decision=Decision.APPROVAL,
        risk_score=70,
        risk_level=RiskLevel.HIGH,
        reasons=[
            "Human approval required."
        ],
        approval_required=True
    )


def test_approval_creation_is_audited(tmp_path):

    logger = AuditLogger(
        log_file=tmp_path / "audit.jsonl"
    )

    manager = ApprovalManager()

    workflow = ApprovalWorkflow(
        approval_manager=manager,
        audit_logger=logger
    )

    action = make_action()

    governance = make_governance()

    approval = workflow.create_approval(
        governance,
        action
    )

    events = logger.find_by_request(
        "REQ-100"
    )

    assert approval is not None
    assert len(events) == 1
    assert events[0]["event_type"] == (
        "APPROVAL_CREATED"
    )


def test_approved_execution_is_audited(tmp_path):

    logger = AuditLogger(
        log_file=tmp_path / "audit.jsonl"
    )

    manager = ApprovalManager()

    executor = SecureExecutor(
        sandbox_dir=tmp_path
    )

    workflow = ApprovalWorkflow(
        approval_manager=manager,
        executor=executor,
        audit_logger=logger
    )

    action = make_action()

    governance = make_governance()

    approval = workflow.create_approval(
        governance,
        action
    )

    result = workflow.approve_and_execute(
        approval_id=approval.approval_id,
        approver_id="admin-001",
        action_request=action,
        governance_result=governance
    )

    assert result["executed"] is True

    events = logger.find_by_request(
        "REQ-100"
    )

    assert len(events) == 2

    assert events[0]["event_type"] == (
        "APPROVAL_CREATED"
    )

    assert events[1]["event_type"] == (
        "EXECUTION"
    )

    assert events[1]["execution_status"] == (
        "SUCCESS"
    )


def test_mismatched_approval_is_audited(tmp_path):

    logger = AuditLogger(
        log_file=tmp_path / "audit.jsonl"
    )

    manager = ApprovalManager()

    executor = SecureExecutor(
        sandbox_dir=tmp_path
    )

    workflow = ApprovalWorkflow(
        approval_manager=manager,
        executor=executor,
        audit_logger=logger
    )

    original_action = make_action(
        resource="approved.txt"
    )

    governance = make_governance()

    approval = workflow.create_approval(
        governance,
        original_action
    )

    modified_action = make_action(
        resource="secret.txt"
    )

    result = workflow.approve_and_execute(
        approval_id=approval.approval_id,
        approver_id="admin-001",
        action_request=modified_action,
        governance_result=governance
    )

    assert result["executed"] is False

    events = logger.find_by_request(
        "REQ-100"
    )

    assert len(events) == 2

    assert events[1]["event_type"] == (
        "APPROVAL_MISMATCH"
    )

    assert events[1]["decision"] == "BLOCK"