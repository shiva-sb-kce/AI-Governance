from core.governance_engine import GovernanceEngine
from approval.approval_workflow import ApprovalWorkflow
from agents.executor import SecureExecutor

from models.schemas import (
    GovernanceRequest,
    ActionRequest,
    EntityType,
    Decision,
)


def test_end_to_end_requires_human_approval(
    tmp_path
):

    # -----------------------------------------
    # Initialize components
    # -----------------------------------------

    engine = GovernanceEngine()

    executor = SecureExecutor(
        sandbox_dir=str(tmp_path)
    )

    workflow = ApprovalWorkflow(
        executor=executor
    )

    # -----------------------------------------
    # Agent requests a risky file write
    # -----------------------------------------

    request = GovernanceRequest(
        request_id="E2E-APPROVAL-001",
        user_id="agent-001",

        # ADMIN is used here because it has
        # permission for write_file.
        # The tool itself still requires approval.
        role="ADMIN",

        entity_type=EntityType.AGENT,

        prompt=(
            "Create the requested project report."
        ),

        action="write_file",

        resource="report.txt",

        parameters={
            "content": "Approved project report"
        }
    )

    # -----------------------------------------
    # Governance evaluation
    # -----------------------------------------

    governance_result = engine.evaluate(
        request
    )

    # -----------------------------------------
    # SECURITY REQUIREMENT
    # Risky write must require approval
    # -----------------------------------------

    assert (
        governance_result.decision
        == Decision.APPROVAL
    )

    assert (
        governance_result.approval_required
        is True
    )

    # -----------------------------------------
    # Convert request into ActionRequest
    # -----------------------------------------

    action_request = ActionRequest(
        action_id="ACT-APPROVAL-001",

        request_id="E2E-APPROVAL-001",

        agent_id="agent-001",

        tool="write_file",

        resource="report.txt",

        parameters={
            "content": "Approved project report"
        }
    )

    # -----------------------------------------
    # Create human approval request
    # -----------------------------------------

    approval = workflow.create_approval(
        governance_result,
        action_request
    )

    assert approval is not None

    assert approval.status.value == "PENDING"

    # -----------------------------------------
    # Human approves
    # -----------------------------------------

    result = workflow.approve_and_execute(
        approval_id=approval.approval_id,

        approver_id="human-reviewer-001",

        action_request=action_request,

        governance_result=governance_result
    )

    # -----------------------------------------
    # Action should now execute
    # -----------------------------------------

    assert result["executed"] is True

    assert (
        result["status"]
        == "SUCCESS"
    )

    # -----------------------------------------
    # Verify actual file creation
    # -----------------------------------------

    report = tmp_path / "report.txt"

    assert report.exists()

    assert (
        report.read_text(
            encoding="utf-8"
        )
        == "Approved project report"
    )
    