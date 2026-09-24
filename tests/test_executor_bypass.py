from agents.executor import SecureExecutor

from models.schemas import (
    ActionRequest,
    Decision,
    GovernanceResult,
    RiskLevel,
)


def test_executor_rejects_governance_bypass():

    executor = SecureExecutor(
        sandbox_dir="sandbox"
    )

    action_request = ActionRequest(
        action_id="ACT-BYPASS-001",
        request_id="REQ-BYPASS-001",
        agent_id="agent-001",
        tool="write_file",
        resource="bypass.txt",
        parameters={
            "content": "UNAUTHORIZED"
        },
    )

    governance_result = GovernanceResult(
        request_id="REQ-BYPASS-001",
        decision=Decision.BLOCK,
        risk_score=90,
        risk_level=RiskLevel.CRITICAL,
    )

    result = executor.execute(
        action_request,
        governance_result
    )

    assert result["executed"] is False
    assert result["status"] == "BLOCKED"