from approval.approval_manager import ApprovalManager
from approval.approval_workflow import ApprovalWorkflow

from models.schemas import (
    ActionRequest,
    Decision,
    GovernanceResult,
    RiskLevel,
    ApprovalStatus,
)


def test_approval_rejects_parameter_tampering():

    manager = ApprovalManager()

    workflow = ApprovalWorkflow(
        approval_manager=manager
    )

    # -----------------------------------------
    # Original action submitted for approval
    # -----------------------------------------

    governance_result = GovernanceResult(
        request_id="REQ-TAMPER-001",
        decision=Decision.APPROVAL,
        risk_score=70,
        risk_level=RiskLevel.HIGH,
        approval_required=True,
        approval_status=ApprovalStatus.PENDING,
    )

    original_request = ActionRequest(
        action_id="ACT-TAMPER-001",
        request_id="REQ-TAMPER-001",
        agent_id="agent-001",
        tool="write_file",
        resource="report.txt",
        parameters={
            "content": "Approved content"
        },
    )

    # -----------------------------------------
    # Create approval
    # -----------------------------------------

    approval = workflow.create_approval(
        governance_result,
        original_request
    )

    assert approval is not None

    # -----------------------------------------
    # Agent modifies the parameters
    # after approval was requested
    # -----------------------------------------

    tampered_request = ActionRequest(
        action_id="ACT-TAMPER-001",
        request_id="REQ-TAMPER-001",
        agent_id="agent-001",
        tool="write_file",
        resource="report.txt",
        parameters={
            "content": "TAMPERED CONTENT"
        },
    )

    # -----------------------------------------
    # Try to approve and execute
    # -----------------------------------------

    result = workflow.approve_and_execute(
        approval_id=approval.approval_id,
        approver_id="human-001",
        action_request=tampered_request,
        governance_result=governance_result,
    )

    # -----------------------------------------
    # SECURITY REQUIREMENT
    # Modified parameters must NOT execute
    # -----------------------------------------

    assert result["executed"] is False
    assert result["status"] == "BLOCKED"