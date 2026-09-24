from models.schemas import InspectionResult

from security.pii_detector import PIIDetector
from security.injection_detector import InjectionDetector


class OutputValidator:

    def __init__(self):

        self.pii_detector = PIIDetector()

        self.injection_detector = (
            InjectionDetector()
        )

    # ==================================================
    # VALIDATE OUTPUT
    # ==================================================

    def validate(
        self,
        output: str
    ) -> InspectionResult:

        if output is None:
            output = ""

        output = str(output)

        # ----------------------------------------------
        # PII detection
        # ----------------------------------------------

        pii_result = (
            self.pii_detector.detect(
                output
            )
        )

        # ----------------------------------------------
        # Injection detection
        # ----------------------------------------------

        injection_result = (
            self.injection_detector.detect(
                output
            )
        )

        reasons = []

        indicators = []

        detected_patterns = []

        detected_pii = []

        # ----------------------------------------------
        # Sensitive data
        # ----------------------------------------------

        if pii_result["detected"]:

            reasons.append(
                "Sensitive information detected "
                "in model output."
            )

            indicators.extend(
                pii_result.get(
                    "types",
                    []
                )
            )

            detected_pii.extend(
                pii_result.get(
                    "types",
                    []
                )
            )

        # ----------------------------------------------
        # Secret detection
        # ----------------------------------------------

        pii_types = [
            str(item).lower()
            for item in pii_result.get(
                "types",
                []
            )
        ]

        secret_detected = any(
            secret_type in pii_types
            for secret_type in [
                "api_key",
                "password",
                "secret",
                "token",
                "credential"
            ]
        )

        if secret_detected:

            reasons.append(
                "Potential credential or secret "
                "detected in model output."
            )

            indicators.append(
                "SECRET_EXPOSURE"
            )

        # ----------------------------------------------
        # Injection-like output
        # ----------------------------------------------

        if injection_result["detected"]:

            reasons.append(
                "Governance-sensitive instruction "
                "pattern detected in model output."
            )

            indicators.extend(
                injection_result.get(
                    "categories",
                    []
                )
            )

            detected_patterns.extend(
                injection_result.get(
                    "matches",
                    []
                )
            )

        # ----------------------------------------------
        # Severity
        # ----------------------------------------------

        severity = max(
            pii_result.get(
                "severity",
                0
            ),

            injection_result.get(
                "severity",
                0
            )
        )

        # ----------------------------------------------
        # Final inspection result
        # ----------------------------------------------

        return InspectionResult(

            injection_detected=(
                injection_result["detected"]
            ),

            jailbreak_detected=(
                "role_manipulation"
                in injection_result.get(
                    "categories",
                    []
                )
            ),

            pii_detected=(
                pii_result["detected"]
            ),

            secret_detected=(
                secret_detected
            ),

            detected_patterns=(
                detected_patterns
            ),

            detected_pii=(
                detected_pii
            ),

            indicators=(
                indicators
            ),

            severity=(
                severity
            ),

            reasons=(
                reasons
            )
        )