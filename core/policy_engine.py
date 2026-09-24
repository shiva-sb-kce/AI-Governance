import json
from pathlib import Path

from models.schemas import Decision, PolicyResult


BASE_DIR = Path(__file__).resolve().parents[1]

POLICIES_FILE = BASE_DIR / "policies" / "policies.json"


class PolicyEngine:

    def __init__(self):
        self.policies = self._load_policies()

    @staticmethod
    def _load_policies():
        with open(POLICIES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    def evaluate_input(self, inspection_result):
        violated_policies = []
        reasons = []
        policy_risk = 0

        # -------------------------
        # Prompt Injection
        # -------------------------

        if inspection_result.injection_detected:

            violated_policies.append("POLICY-001")

            policy = self.policies["POLICY-001"]

            policy_risk += policy["severity"]

            reasons.append(
                policy["description"]
            )

        # -------------------------
        # Jailbreak
        # -------------------------

        if inspection_result.jailbreak_detected:

            violated_policies.append("POLICY-002")

            policy = self.policies["POLICY-002"]

            policy_risk += policy["severity"]

            reasons.append(
                policy["description"]
            )

        # -------------------------
        # Sensitive Data
        # -------------------------

        if inspection_result.pii_detected:

            violated_policies.append("POLICY-003")

            policy = self.policies["POLICY-003"]

            policy_risk += policy["severity"]

            reasons.append(
                "Sensitive information requires "
                "additional governance evaluation."
            )

        # -------------------------
        # Secret Exposure
        # -------------------------

        if inspection_result.secret_detected:

            violated_policies.append("POLICY-006")

            policy = self.policies["POLICY-006"]

            policy_risk += policy["severity"]

            reasons.append(
                policy["description"]
            )

        # -------------------------
        # Determine mandatory action
        # -------------------------

        mandatory_decision = None

        for policy_id in violated_policies:

            policy = self.policies[policy_id]

            action = policy["action"]

            if action == "BLOCK":
                mandatory_decision = Decision.BLOCK
                break

            if (
                action == "APPROVAL"
                and mandatory_decision != Decision.BLOCK
            ):
                mandatory_decision = Decision.APPROVAL

        return PolicyResult(
            violated_policies=violated_policies,
            mandatory_decision=mandatory_decision,
            policy_risk=min(policy_risk, 100),
            reasons=reasons
        )