from abc import ABC, abstractmethod
from typing import Any, Dict


class AIAdapter(ABC):
    """
    Common interface for AI integrations.

    LLMs, SLMs and agents can use the same
    governance interception architecture.
    """

    entity_type = None

    @abstractmethod
    def execute(
        self,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a governed AI operation.
        """
        raise NotImplementedError