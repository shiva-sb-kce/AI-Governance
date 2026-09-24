from core.governance_engine import GovernanceEngine
from agents.executor import SecureExecutor

from models.schemas import (
    GovernanceRequest,
    EntityType,
    Decision,
)


def test_end_to_end_allows_safe_agent_action(
    tmp_path
):

    engine = GovernanceEngine()

    executor = SecureExecutor(
        sandbox_dir=str(tmp_path)
    )

    request = GovernanceRequest(
        request_id="E2E-SAFE-001",
        user_id="agent-001",
        role="AGENT",
        entity_type=EntityType.AGENT,

        prompt=(
            "Read the project configuration file."
        ),

        action="read_file",

        resource="config.txt",

        parameters={}
    )

    # -----------------------------------------
    # Create file inside sandbox
    # -----------------------------------------

    config_file = tmp_path / "config.txt"

    config_file.write_text(
        "AI Governance configuration",
        encoding="utf-8"
    )

    # -----------------------------------------
    # Governance
    # -----------------------------------------

    governance_result = engine.evaluate(
        request
    )

    # -----------------------------------------
    # Safe action must be allowed
    # -----------------------------------------

    assert (
        governance_result.decision
        == Decision.ALLOW
    )

    assert (
        governance_result.permission
        == "ALLOW"
    )

    assert governance_result.risk_score < 31

    # -----------------------------------------
    # Execute only after governance ALLOW
    # -----------------------------------------

    execution_result = executor.execute(
        type(
            "Action",
            (),
            {
                "tool": "read_file",
                "resource": "config.txt",
                "parameters": {},
            }
        )(),
        governance_result
    )

    assert execution_result["executed"] is True

    assert (
        execution_result["status"]
        == "SUCCESS"
    )
    