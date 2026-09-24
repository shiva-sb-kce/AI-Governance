from typing import Any, Dict

from integrations.base import AIAdapter

from models.schemas import (
    GovernanceRequest,
    EntityType
)


class LLMAdapter(AIAdapter):

    entity_type = EntityType.LLM

    def __init__(
        self,
        governance_gateway
    ):
        self.gateway = governance_gateway

    def execute(
        self,
        prompt: str,
        request_id: str,
        user_id: str,
        role: str = "USER",
        **kwargs
    ) -> Dict[str, Any]:

        request = GovernanceRequest(

            request_id=request_id,

            user_id=user_id,

            role=role,

            entity_type=EntityType.LLM,

            prompt=prompt,

            context=kwargs
        )

        result = self.gateway.process(
            request
        )

        return {
            "entity_type": (
                EntityType.LLM.value
            ),

            "request_id": request_id,

            "decision": (
                result.decision.value
            ),

            "risk_score": (
                result.risk_score
            ),

            "risk_level": (
                result.risk_level.value
            ),

            "permission": (
                result.permission
            ),

            "approval_required": (
                result.approval_required
            ),

            "approval_status": (
                result.approval_status.value
            ),

            "threats": (
                result.threats
            ),

            "violated_policies": (
                result.violated_policies
            ),

            "reasons": (
                result.reasons
            ),

            "allowed": (
                result.decision.value
                == "ALLOW"
            )
        }