from core.decision_engine import DecisionEngine
from core.permission_engine import PermissionEngine
from core.policy_engine import PolicyEngine
from core.risk_engine import RiskEngine

from security.input_inspector import InputInspector
from audit.audit_logger import AuditLogger

from models.schemas import (
    GovernanceRequest,
    GovernanceResult,
    ApprovalStatus,
    EntityType
)


class GovernanceEngine:

    def __init__(self, audit_logger=None):
        self.input_inspector = InputInspector()
        self.policy_engine = PolicyEngine()
        self.permission_engine = PermissionEngine()
        self.risk_engine = RiskEngine()
        self.decision_engine = DecisionEngine()

        self.audit_logger = (
            audit_logger
            or AuditLogger()
    )

    def evaluate(
        self,
        request: GovernanceRequest
    ) -> GovernanceResult:

        # ---------------------------------------
        # 1. Inspect input
        # ---------------------------------------

        inspection = self.input_inspector.inspect(
            request.prompt
        )

        # ---------------------------------------
        # 2. Evaluate policies
        # ---------------------------------------

        policy_result = (
            self.policy_engine.evaluate_input(
                inspection
            )
        )

        # ---------------------------------------
        # 3. Evaluate permission
        # ---------------------------------------

        permission_result = None

        if request.action:

            permission_result = (
                self.permission_engine.check_permission(
                    role=request.role,
                    action=request.action,
                    resource=request.resource
                )
            )

        # ---------------------------------------
        # 4. Calculate action risk
        # ---------------------------------------

        action_risk = 0

        if request.action:

            tool_config = (
                self.permission_engine.tools.get(
                    request.action
                )
            )

            if tool_config:

                action_risk = tool_config.get(
                    "risk",
                    0
                )

                # Normalize tool risk (0-100)
                # to risk factor (0-25)

                action_risk = min(
                    action_risk // 4,
                    25
                )

        # ---------------------------------------
        # 5. Calculate overall risk
        # ---------------------------------------

        risk_result = self.risk_engine.calculate(
            inspection_result=inspection,
            policy_result=policy_result,
            permission_result=permission_result,
            action_risk=action_risk
        )

        # ---------------------------------------
        # 6. Final decision
        # ---------------------------------------

        decision = self.decision_engine.decide(
            policy_result=policy_result,
            risk_result=risk_result,
            permission_result=permission_result
        )

        # ---------------------------------------
        # 7. Approval state
        # ---------------------------------------

        approval_required = (
            decision.value == "APPROVAL"
        )

        if approval_required:
            approval_status = (
                ApprovalStatus.PENDING
            )
        else:
            approval_status = (
                ApprovalStatus.NOT_REQUIRED
            )

        # ---------------------------------------
        # 8. Combine reasons
        # ---------------------------------------

        reasons = []

        reasons.extend(
            inspection.reasons
        )

        reasons.extend(
            policy_result.reasons
        )

        reasons.extend(
            risk_result["reasons"]
        )

        if permission_result:

            reasons.extend(
                permission_result.reasons
            )

        # ---------------------------------------
        # 9. Threat list
        # ---------------------------------------

        threats = []

        if inspection.injection_detected:
            threats.append(
                "PROMPT_INJECTION"
            )

        if inspection.jailbreak_detected:
            threats.append(
                "JAILBREAK"
            )

        if inspection.pii_detected:
            threats.append(
                "SENSITIVE_DATA"
            )

        if inspection.secret_detected:
            threats.append(
                "SECRET_EXPOSURE"
            )

        # ---------------------------------------
        # 10. Final result
        # ---------------------------------------
        self.audit_logger.log(
            event_type="GOVERNANCE_DECISION",
            request_id=request.request_id,
            decision=decision.value,
            entity_type=request.entity_type.value,
            entity_id=request.user_id,
            action=request.action,
            resource=request.resource,
            risk_score=risk_result["risk_score"],
            risk_level=risk_result["risk_level"].value,
            threats=threats,
            violated_policies=(
                policy_result.violated_policies
            ),
            permission=(
                permission_result.permission
                if permission_result
                else "NOT_APPLICABLE"
            ),
            reasons=reasons
        )

        return GovernanceResult(
            request_id=request.request_id,
            decision=decision,
            risk_score=risk_result["risk_score"],
            risk_level=risk_result["risk_level"],
            threats=threats,
            violated_policies=(
                policy_result.violated_policies
            ),
            permission=(
                permission_result.permission
                if permission_result
                else "NOT_APPLICABLE"
            ),
            reasons=reasons,
            approval_required=approval_required,
            approval_status=approval_status
        )
    def evaluate_action(
        self,
        action_request,
        agent_role="AGENT"
    ):
        request = GovernanceRequest(
            request_id=action_request.request_id,
            user_id=action_request.agent_id,
            role=agent_role,
            entity_type=EntityType.AGENT,
            prompt="",
            action=action_request.tool,
            resource=action_request.resource,
            parameters=action_request.parameters
        )

        return self.evaluate(request)