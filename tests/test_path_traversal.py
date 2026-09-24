from agents.executor import SecureExecutor

from models.schemas import (
    ActionRequest,
    Decision,
    GovernanceResult,
    RiskLevel,
)


def test_executor_blocks_path_traversal():

    executor = SecureExecutor(
        sandbox_dir="sandbox"
    )

    action_request = ActionRequest(
        action_id="ACT-PATH-001",
        request_id="REQ-PATH-001",
        agent_id="agent-001",
        tool="write_file",
        resource="../../outside.txt",
        parameters={
            "content": "MALICIOUS"
        },
    )

    governance_result = GovernanceResult(
        request_id="REQ-PATH-001",
        decision=Decision.ALLOW,
        risk_score=10,
        risk_level=RiskLevel.LOW,
    )

    result = executor.execute(
        action_request,
        governance_result
    )

    assert result["executed"] is False
    assert result["status"] == "BLOCKED"