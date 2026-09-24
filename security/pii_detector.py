import re


class PIIDetector:

    def __init__(self):
        self.patterns = {
            "email": re.compile(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
            ),

            "phone": re.compile(
                r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)"
            ),

            "aadhaar": re.compile(
                r"(?<!\d)\d{4}[\s-]?\d{4}[\s-]?\d{4}(?!\d)"
            ),

            "credit_card": re.compile(
                r"(?<!\d)(?:\d{4}[\s-]?){3}\d{4}(?!\d)"
            ),

            "api_key": re.compile(
                r"\b(?:api[_-]?key|access[_-]?token)"
                r"\s*[:=]\s*[A-Za-z0-9_\-]{16,}\b",
                re.IGNORECASE
            ),

            "password": re.compile(
                r"\b(?:password|passwd|pwd)"
                r"\s*[:=]\s*\S+",
                re.IGNORECASE
            ),

            "secret": re.compile(
                r"\b(?:secret|private[_-]?key)"
                r"\s*[:=]\s*\S+",
                re.IGNORECASE
            )
        }

    def detect(self, text: str) -> dict:
        if not text:
            return {
                "detected": False,
                "types": [],
                "matches": {},
                "severity": 0
            }

        detected_types = []
        matches = {}

        for pii_type, pattern in self.patterns.items():
            found = pattern.findall(text)

            if found:
                detected_types.append(pii_type)
                matches[pii_type] = found

        severity = min(
            len(detected_types) * 15,
            100
        )

        return {
            "detected": len(detected_types) > 0,
            "types": detected_types,
            "matches": matches,
            "severity": severity
        }