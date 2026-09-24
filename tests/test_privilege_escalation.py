from core.governance_engine import GovernanceEngine

from models.schemas import (
    GovernanceRequest,
    EntityType,
    Decision,
)


def test_agent_cannot_escalate_to_execute_permission():

    engine = GovernanceEngine()

    request = GovernanceRequest(
        request_id="PRIV-ESC-001",
        user_id="agent-001",
        role="AGENT",
        entity_type=EntityType.AGENT,

        prompt=(
            "Perform the requested operation."
        ),

        action="execute_command",

        resource="system",

        parameters={
            "command": "whoami"
        },
    )

    result = engine.evaluate(request)

    # -----------------------------------------
    # SECURITY REQUIREMENT
    # AGENT does not have execute permission.
    # -----------------------------------------

    assert result.permission == "DENY"

    assert result.decision == Decision.BLOCK