from models.schemas import InspectionResult

from security.injection_detector import InjectionDetector
from security.pii_detector import PIIDetector


class InputInspector:

    def __init__(self):
        self.injection_detector = InjectionDetector()
        self.pii_detector = PIIDetector()

    def inspect(self, text: str) -> InspectionResult:
        injection_result = self.injection_detector.detect(text)
        pii_result = self.pii_detector.detect(text)

        reasons = []
        indicators = []
        detected_patterns = []
        detected_pii = []

        # -------------------------
        # Injection findings
        # -------------------------

        if injection_result["detected"]:
            reasons.append(
                "Potential prompt injection detected."
            )

            indicators.extend(
                injection_result["categories"]
            )

            detected_patterns.extend(
                injection_result["matches"]
            )

        # -------------------------
        # PII findings
        # -------------------------

        if pii_result["detected"]:
            reasons.append(
                "Sensitive information detected in input."
            )

            indicators.extend(
                pii_result["types"]
            )

            detected_pii.extend(
                pii_result["types"]
            )

        # -------------------------
        # Calculate severity
        # -------------------------

        severity = max(
            injection_result["severity"],
            pii_result["severity"]
        )

        return InspectionResult(
            injection_detected=injection_result["detected"],
            jailbreak_detected=(
                "role_manipulation"
                in injection_result["categories"]
            ),
            pii_detected=pii_result["detected"],
            secret_detected=(
                "api_key" in pii_result["types"]
                or "password" in pii_result["types"]
                or "secret" in pii_result["types"]
            ),
            detected_patterns=detected_patterns,
            detected_pii=detected_pii,
            indicators=indicators,
            severity=severity,
            reasons=reasons
        )