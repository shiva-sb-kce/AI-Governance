from integrations.llm_adapter import (
    LLMAdapter
)

from integrations.slm_adapter import (
    SLMAdapter
)

from integrations.agent_adapter import (
    AgentAdapter
)


class IntegrationManager:

    def __init__(
        self,
        governance_gateway
    ):

        self.gateway = (
            governance_gateway
        )

        self.llm = LLMAdapter(
            governance_gateway
        )

        self.slm = SLMAdapter(
            governance_gateway
        )

        self.agent = AgentAdapter(
            governance_gateway
        )

    # ==================================================
    # LLM
    # ==================================================

    def process_llm(
        self,
        prompt,
        request_id,
        user_id,
        role="USER",
        **context
    ):

        return self.llm.execute(
            prompt=prompt,
            request_id=request_id,
            user_id=user_id,
            role=role,
            **context
        )

    # ==================================================
    # SLM
    # ==================================================

    def process_slm(
        self,
        prompt,
        request_id,
        user_id,
        role="USER",
        **context
    ):

        return self.slm.execute(
            prompt=prompt,
            request_id=request_id,
            user_id=user_id,
            role=role,
            **context
        )

    # ==================================================
    # AGENT
    # ==================================================

    def process_agent(
        self,
        action_request,
        role="AGENT"
    ):

        return self.agent.execute(
            action_request=action_request,
            role=role
        )