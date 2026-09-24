from typing import Any, Dict

from integrations.base import AIAdapter

from models.schemas import ActionRequest


class AgentAdapter(AIAdapter):

    def __init__(
        self,
        governance_gateway
    ):
        self.gateway = governance_gateway

    def execute(
        self,
        action_request: ActionRequest,
        role: str = "AGENT"
    ) -> Dict[str, Any]:

        return self.gateway.process_action(
            action_request=action_request,
            role=role
        )