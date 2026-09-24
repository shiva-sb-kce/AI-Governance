from core.governance_engine import GovernanceEngine
from models.schemas import (
    GovernanceRequest,
    EntityType
)

class SecurityEvaluator:

    def __init__(self, governance_engine=None):
        self.engine = (
            governance_engine
            or GovernanceEngine()
        )

    def evaluate_scenario(self, scenario):

        request = GovernanceRequest(
            request_id=scenario.scenario_id,
            user_id="evaluation-user",
            role=scenario.role,
            entity_type=scenario.entity_type,
            prompt=scenario.prompt,
            action=scenario.action,
            resource=scenario.resource
        )

        result = self.engine.evaluate(
            request
        )

        expected = scenario.expected_decision
        actual = result.decision.value

        return {
            "scenario_id": scenario.scenario_id,
            "name": scenario.name,
            "expected": expected,
            "actual": actual,
            "correct": expected == actual,
            "risk_score": result.risk_score,
            "risk_level": result.risk_level.value,
            "threats": result.threats,
            "policies": result.violated_policies
        }

    def evaluate_all(self, scenarios):

        results = []

        for scenario in scenarios:
            results.append(
                self.evaluate_scenario(
                    scenario
                )
            )

        return results

    @staticmethod
    def calculate_metrics(results):

        total = len(results)

        correct = sum(
            result["correct"]
            for result in results
        )

        accuracy = (
            correct / total
            if total
            else 0
        )

        return {
            "total": total,
            "correct": correct,
            "incorrect": total - correct,
            "accuracy": accuracy
        }
    def evaluate_adversarial(
        self,
        scenarios
    ):

        results = []

        for scenario in scenarios:

            request = GovernanceRequest(
                request_id=scenario.scenario_id,
                user_id="adversarial-test",
                role="USER",
                entity_type=EntityType.USER,
                prompt=scenario.prompt
            )

            result = self.engine.evaluate(
                request
            )

            # For this binary attack benchmark:
            # BLOCK = detected as malicious
            predicted_malicious = (
                result.decision.value == "BLOCK"
            )

            results.append({
                "scenario_id": scenario.scenario_id,
                "name": scenario.name,
                "expected_malicious": (
                    scenario.malicious
                ),
                "predicted_malicious": (
                    predicted_malicious
                ),
                "decision": (
                    result.decision.value
                ),
                "correct": (
                    scenario.malicious
                    == predicted_malicious
                ),
                "risk_score": result.risk_score,
                "threats": result.threats,
                "policies": result.violated_policies
            })

        return results