from typing import Dict, Any

from core.gateway import GovernanceGateway

from models.schemas import (
    GovernanceRequest,
    EntityType
)

from security.output_validator import (
    OutputValidator
)

from services.model_service import (
    ModelService
)


class SecuredAIService:

    def __init__(
        self,
        gateway: GovernanceGateway,
        model_service=None,
        output_validator=None
    ):

        self.gateway = gateway

        self.model_service = (
            model_service
            or ModelService()
        )

        self.output_validator = (
            output_validator
            or OutputValidator()
        )

    # ==================================================
    # MAIN PIPELINE
    # ==================================================

    def process(
        self,
        request: GovernanceRequest
    ) -> Dict[str, Any]:

        # ----------------------------------------------
        # 1. INPUT GOVERNANCE
        # ----------------------------------------------

        governance_result = (
            self.gateway.process(
                request
            )
        )

        decision = (
            governance_result.decision.value
        )

        # ----------------------------------------------
        # 2. BLOCK BEFORE MODEL
        # ----------------------------------------------

        if decision == "BLOCK":

            return {
                "status": "BLOCKED",

                "executed": False,

                "entity_type": (
                    request.entity_type.value
                ),

                "request_id": (
                    request.request_id
                ),

                "decision": decision,

                "risk_score": (
                    governance_result.risk_score
                ),

                "risk_level": (
                    governance_result.risk_level.value
                ),

                "threats": (
                    governance_result.threats
                ),

                "violated_policies": (
                    governance_result
                    .violated_policies
                ),

                "reasons": (
                    governance_result.reasons
                )
            }

        # ----------------------------------------------
        # 3. APPROVAL / MONITOR
        # ----------------------------------------------

        if decision == "APPROVAL":

            return {
                "status": "PENDING_APPROVAL",

                "executed": False,

                "entity_type": (
                    request.entity_type.value
                ),

                "request_id": (
                    request.request_id
                ),

                "decision": decision,

                "risk_score": (
                    governance_result.risk_score
                ),

                "risk_level": (
                    governance_result.risk_level.value
                ),

                "approval_required": True,

                "reasons": (
                    governance_result.reasons
                )
            }

        # ----------------------------------------------
        # 4. MODEL EXECUTION
        # ----------------------------------------------

        model_type = (
            request.entity_type.value.upper()
        )

        model_result = (
            self.model_service.generate(
                prompt=request.prompt,
                model_type=model_type
            )
        )

        if not model_result.get(
            "success",
            False
        ):

            return {
                "status": "MODEL_ERROR",

                "executed": False,

                "request_id": (
                    request.request_id
                ),

                "decision": decision,

                "reason": (
                    model_result.get(
                        "reason",
                        "Model execution failed."
                    )
                )
            }

        output = model_result.get(
            "output",
            ""
        )

        # ----------------------------------------------
        # 5. OUTPUT VALIDATION
        # ----------------------------------------------

        inspection = (
            self.output_validator.validate(
                output
            )
        )

        # ----------------------------------------------
        # 6. BLOCK UNSAFE OUTPUT
        # ----------------------------------------------

        if inspection.severity >= 70:

            return {
                "status": "OUTPUT_BLOCKED",

                "executed": True,

                "output_released": False,

                "request_id": (
                    request.request_id
                ),

                "decision": decision,

                "risk_score": (
                    governance_result.risk_score
                ),

                "output_severity": (
                    inspection.severity
                ),

                "output_security": {
                    "injection_detected": (
                        inspection
                        .injection_detected
                    ),

                    "jailbreak_detected": (
                        inspection
                        .jailbreak_detected
                    ),

                    "pii_detected": (
                        inspection
                        .pii_detected
                    ),

                    "secret_detected": (
                        inspection
                        .secret_detected
                    ),

                    "detected_patterns": (
                        inspection
                        .detected_patterns
                    ),

                    "detected_pii": (
                        inspection
                        .detected_pii
                    ),

                    "indicators": (
                        inspection
                        .indicators
                    ),

                    "reasons": (
                        inspection
                        .reasons
                    )
                }
            }

        # ----------------------------------------------
        # 7. SAFE OUTPUT
        # ----------------------------------------------

        return {
            "status": "SUCCESS",

            "executed": True,

            "output_released": True,

            "entity_type": (
                request.entity_type.value
            ),

            "request_id": (
                request.request_id
            ),

            "decision": decision,

            "risk_score": (
                governance_result.risk_score
            ),

            "risk_level": (
                governance_result.risk_level.value
            ),

            "output": output,

            "output_security": {

                "severity": (
                    inspection.severity
                ),

                "injection_detected": (
                    inspection.injection_detected
                ),

                "jailbreak_detected": (
                    inspection.jailbreak_detected
                ),

                "pii_detected": (
                    inspection.pii_detected
                ),

                "secret_detected": (
                    inspection.secret_detected
                ),

                "indicators": (
                    inspection.indicators
                ),

                "reasons": (
                    inspection.reasons
                )
            }
        }