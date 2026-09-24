from typing import Dict, Any


class ModelService:
    """
    Offline model execution service.

    This abstraction allows real LLM/SLM providers
    to be plugged in later without changing the
    governance layer.
    """

    def generate(
        self,
        prompt: str,
        model_type: str = "LLM"
    ) -> Dict[str, Any]:

        if not prompt:
            return {
                "success": False,
                "output": "",
                "reason": "Empty prompt."
            }

        # --------------------------------------------------
        # Offline deterministic response
        # --------------------------------------------------

        output = (
            f"[{model_type} OFFLINE MODEL] "
            f"Processed request: {prompt}"
        )

        return {
            "success": True,
            "model_type": model_type,
            "output": output
        }