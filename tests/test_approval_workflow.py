from agents.executor import SecureExecutor
from approval.approval_manager import ApprovalManager
from approval.approval_workflow import ApprovalWorkflow

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
        action_id="ACT-001",
        request_id="REQ-001",
        agent_id="admin-001",
        tool=tool,
        resource=resource,
        parameters={
            "content": "Approved execution"
        }
    )


def make_governance_result():
    return GovernanceResult(
        request_id="REQ-001",
        decision=Decision.APPROVAL,
        risk_score=70,
        risk_level=RiskLevel.HIGH,
        reasons=[
            "Human approval required."
        ],
        approval_required=True
    )


def test_create_approval():
    manager = ApprovalManager()

    workflow = ApprovalWorkflow(
        approval_manager=manager
    )

    action = make_action()

    governance = make_governance_result()

    approval = workflow.create_approval(
        governance,
        action
    )

    assert approval is not None
    assert approval.status.value == "PENDING"
    assert approval.action == "write_file"
    assert approval.resource == "approved.txt"


def test_non_approval_does_not_create_request():
    manager = ApprovalManager()

    workflow = ApprovalWorkflow(
        approval_manager=manager
    )

    action = make_action()

    governance = make_governance_result()

    governance.decision = Decision.ALLOW

    approval = workflow.create_approval(
        governance,
        action
    )

    assert approval is None


def test_approved_action_executes(tmp_path):
    manager = ApprovalManager()

    executor = SecureExecutor(
        sandbox_dir=tmp_path
    )

    workflow = ApprovalWorkflow(
        approval_manager=manager,
        executor=executor
    )

    action = make_action()

    governance = make_governance_result()

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
    assert result["status"] == "SUCCESS"


def test_wrong_resource_cannot_use_approval(
    tmp_path
):
    manager = ApprovalManager()

    executor = SecureExecutor(
        sandbox_dir=tmp_path
    )

    workflow = ApprovalWorkflow(
        approval_manager=manager,
        executor=executor
    )

    original_action = make_action(
        resource="approved.txt"
    )

    governance = make_governance_result()

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
    assert result["status"] == "BLOCKED"


def test_wrong_tool_cannot_use_approval(
    tmp_path
):
    manager = ApprovalManager()

    executor = SecureExecutor(
        sandbox_dir=tmp_path
    )

    workflow = ApprovalWorkflow(
        approval_manager=manager,
        executor=executor
    )

    original_action = make_action(
        tool="write_file"
    )

    governance = make_governance_result()

    approval = workflow.create_approval(
        governance,
        original_action
    )

    modified_action = make_action(
        tool="execute_command"
    )

    result = workflow.approve_and_execute(
        approval_id=approval.approval_id,
        approver_id="admin-001",
        action_request=modified_action,
        governance_result=governance
    )

    assert result["executed"] is False
    assert result["status"] == "BLOCKED"