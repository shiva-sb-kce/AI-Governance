from agents.executor import SecureExecutor

from models.schemas import (
    ActionRequest,
    Decision,
    GovernanceResult,
    RiskLevel,
)


def test_executor_blocks_absolute_windows_path():

    executor = SecureExecutor(
        sandbox_dir="sandbox"
    )

    action_request = ActionRequest(
        action_id="ACT-PATH-002",
        request_id="REQ-PATH-002",
        agent_id="agent-001",
        tool="write_file",
        resource=r"C:\Users\USER\outside.txt",
        parameters={
            "content": "MALICIOUS"
        },
    )

    governance_result = GovernanceResult(
        request_id="REQ-PATH-002",
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