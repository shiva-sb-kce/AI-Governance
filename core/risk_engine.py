from models.schemas import RiskLevel


class RiskEngine:

    MAX_FACTOR_SCORE = 25

    def calculate(
        self,
        inspection_result,
        policy_result,
        permission_result=None,
        action_risk=0
    ):
        threat_score = self._calculate_threat_score(
            inspection_result
        )

        data_score = self._calculate_data_score(
            inspection_result
        )

        permission_score = self._calculate_permission_score(
            permission_result
        )

        action_score = min(
            max(action_risk, 0),
            self.MAX_FACTOR_SCORE
        )

        risk_score = min(
            threat_score
            + data_score
            + permission_score
            + action_score,
            100
        )

        risk_level = self._get_risk_level(
            risk_score
        )

        reasons = []

        if threat_score > 0:
            reasons.append(
                f"Threat indicators contributed "
                f"{threat_score} points."
            )

        if data_score > 0:
            reasons.append(
                f"Sensitive data contributed "
                f"{data_score} points."
            )

        if permission_score > 0:
            reasons.append(
                f"Permission risk contributed "
                f"{permission_score} points."
            )

        if action_score > 0:
            reasons.append(
                f"Action severity contributed "
                f"{action_score} points."
            )

        if policy_result.violated_policies:
            reasons.append(
                "One or more governance policies "
                "were violated."
            )

        return {
            "threat_score": threat_score,
            "data_score": data_score,
            "permission_score": permission_score,
            "action_score": action_score,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "factors": {
                "threat": threat_score,
                "data": data_score,
                "permission": permission_score,
                "action": action_score
            },
            "reasons": reasons
        }

    def _calculate_threat_score(
        self,
        inspection_result
    ):
        score = 0

        if inspection_result.injection_detected:
            score += 25

        if inspection_result.jailbreak_detected:
            score += 25

        return min(
            score,
            self.MAX_FACTOR_SCORE
        )

    def _calculate_data_score(
        self,
        inspection_result
    ):
        score = 0

        if inspection_result.pii_detected:
            score += 15

        if inspection_result.secret_detected:
            score += 25

        return min(
            score,
            self.MAX_FACTOR_SCORE
        )

    def _calculate_permission_score(
        self,
        permission_result
    ):
        if permission_result is None:
            return 0

        if permission_result.permission == "DENY":
            return 25

        if permission_result.permission == "APPROVAL":
            return 15

        return 0

    @staticmethod
    def _get_risk_level(score):
        if score <= 30:
            return RiskLevel.LOW

        if score <= 60:
            return RiskLevel.MEDIUM

        if score <= 80:
            return RiskLevel.HIGH

        return RiskLevel.CRITICAL