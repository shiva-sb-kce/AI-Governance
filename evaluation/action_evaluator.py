from models.schemas import (
    RiskLevel,
    PolicyResult,
    ActionRequest,
)

from security.action_validator import ActionValidator
from core.permission_engine import PermissionEngine
from agents.tool_registry import ToolRegistry
from core.decision_engine import DecisionEngine


class ActionGovernanceEvaluator:

    def __init__(self):
        self.action_validator = ActionValidator()
        self.tool_registry = ToolRegistry()
        self.permission_engine = PermissionEngine()
        self.decision_engine = DecisionEngine()

    @staticmethod
    def _risk_level(score):

        if score >= 81:
            return RiskLevel.CRITICAL

        if score >= 61:
            return RiskLevel.HIGH

        if score >= 31:
            return RiskLevel.MEDIUM

        return RiskLevel.LOW

    def evaluate(self, scenario):

        # -----------------------------------------
        # Action validation
        # -----------------------------------------


        action_request = ActionRequest(
            action_id=scenario.scenario_id,
            request_id=scenario.scenario_id,
            agent_id=f"{scenario.role.lower()}-001",
            tool=scenario.tool,
            resource=scenario.resource
        )

        validation = self.action_validator.validate(
            action_request,
            self.tool_registry
        )

        # -----------------------------------------
        # Unknown tool
        # -----------------------------------------

        if not validation["valid"]:

            return {
                "scenario_id": scenario.scenario_id,
                "expected": scenario.expected_decision,
                "actual": "BLOCK",
                "correct": (
                    scenario.expected_decision
                    == "BLOCK"
                ),
                "reasons": validation["reasons"]
            }

        # -----------------------------------------
        # Permission
        # -----------------------------------------

        permission_result = (
            self.permission_engine.check_permission(
                role=scenario.role,
                action=scenario.tool,
                resource=scenario.resource
            )
        )

        # -----------------------------------------
        # Risk
        # -----------------------------------------

        risk_score = validation["risk"]

        risk_result = {
            "risk_score": risk_score,
            "risk_level": self._risk_level(
                risk_score
            )
        }

        # -----------------------------------------
        # Decision
        # -----------------------------------------

        policy_result = PolicyResult()

        decision = self.decision_engine.decide(
            policy_result=policy_result,
            risk_result=risk_result,
            permission_result=permission_result
        )

        actual = decision.value

        reasons = []

        reasons.extend(
            validation["reasons"]
        )

        reasons.extend(
            permission_result.reasons
        )

        return {
            "scenario_id": scenario.scenario_id,
            "expected": scenario.expected_decision,
            "actual": actual,
            "correct": (
                scenario.expected_decision
                == actual
            ),
            "risk_score": risk_score,
            "risk_level": (
                risk_result["risk_level"].value
            ),
            "permission": (
                permission_result.permission
            ),
            "reasons": reasons
        }

    def evaluate_all(self, scenarios):

        return [
            self.evaluate(scenario)
            for scenario in scenarios
        ]