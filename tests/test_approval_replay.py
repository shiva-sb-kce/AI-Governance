from approval.approval_manager import ApprovalManager
from approval.approval_workflow import ApprovalWorkflow

from models.schemas import (
    ActionRequest,
    Decision,
    GovernanceResult,
    RiskLevel,
    ApprovalStatus,
)


def test_approved_action_cannot_be_replayed():

    manager = ApprovalManager()

    workflow = ApprovalWorkflow(
        approval_manager=manager
    )

    governance_result = GovernanceResult(
        request_id="REQ-REPLAY-001",
        decision=Decision.APPROVAL,
        risk_score=70,
        risk_level=RiskLevel.HIGH,
        approval_required=True,
        approval_status=ApprovalStatus.PENDING,
    )

    action_request = ActionRequest(
        action_id="ACT-REPLAY-001",
        request_id="REQ-REPLAY-001",
        agent_id="agent-001",
        tool="write_file",
        resource="replay.txt",
        parameters={
            "content": "approved once"
        },
    )

    approval = workflow.create_approval(
        governance_result,
        action_request
    )

    assert approval is not None

    # First execution should succeed.
    first_result = workflow.approve_and_execute(
        approval_id=approval.approval_id,
        approver_id="human-001",
        action_request=action_request,
        governance_result=governance_result,
    )

    assert first_result["executed"] is True

    # -----------------------------------------
    # Replay the SAME approval
    # -----------------------------------------

    replay_result = workflow.approve_and_execute(
        approval_id=approval.approval_id,
        approver_id="attacker",
        action_request=action_request,
        governance_result=governance_result,
    )

    # -----------------------------------------
    # SECURITY REQUIREMENT
    # An approval must be single-use.
    # -----------------------------------------

    assert replay_result["executed"] is False
    assert replay_result["status"] == "BLOCKED"