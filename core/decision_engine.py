from models.schemas import Decision


class DecisionEngine:

    def decide(
        self,
        policy_result,
        risk_result,
        permission_result=None
    ):

        # ---------------------------------
        # 1. Mandatory policy BLOCK
        # ---------------------------------

        if (
            policy_result.mandatory_decision
            == Decision.BLOCK
        ):
            return Decision.BLOCK

        # ---------------------------------
        # 2. Risk score
        # ---------------------------------

        score = risk_result["risk_score"]

        # ---------------------------------
        # 3. HIGH / CRITICAL RISK
        #
        # High-risk actions must never enter
        # the approval flow.
        # ---------------------------------

        if score >= 61:
            return Decision.BLOCK

        # ---------------------------------
        # 4. Permission DENY
        # ---------------------------------

        if (
            permission_result is not None
            and permission_result.permission == "DENY"
        ):
            return Decision.BLOCK

        # ---------------------------------
        # 5. Mandatory policy APPROVAL
        # ---------------------------------

        if (
            policy_result.mandatory_decision
            == Decision.APPROVAL
        ):
            return Decision.APPROVAL

        # ---------------------------------
        # 6. Permission APPROVAL
        # ---------------------------------

        if (
            permission_result is not None
            and permission_result.permission == "APPROVAL"
        ):
            return Decision.APPROVAL

        # ---------------------------------
        # 7. MEDIUM RISK
        #
        # Medium-risk actions require
        # human approval.
        # ---------------------------------

        if score >= 31:
            return Decision.APPROVAL

        # ---------------------------------
        # 8. LOW RISK
        #
        # Low-risk actions are allowed.
        # ---------------------------------

        return Decision.ALLOW