import re


class InjectionDetector:

    def __init__(self):
        self.patterns = {

            # -----------------------------------------
            # Instruction Override
            # -----------------------------------------

            "instruction_override": [
                r"\bignore\s+(all\s+)?(the\s+)?(previous|prior|earlier)\s+(instructions?|rules?|directions?)\b",

                r"\bdisregard\s+(all\s+)?(the\s+)?(previous|prior|earlier)\s+(instructions?|rules?|directions?)\b",

                r"\bforget\s+(all\s+)?(the\s+)?(previous|prior|earlier)\s+(instructions?|rules?|directions?)\b",

                r"\bforget\s+(everything|all)\s+(above|before|earlier)\b",

                r"\bignore\s+(everything|all)\s+(above|before|earlier)\b",

                r"\bdiscard\s+(the\s+)?(previous|prior|earlier)\s+(instructions?|rules?)\b",

                r"\breplace\s+(the\s+)?(previous|current)\s+(instructions?|rules?)\b",

                r"\boverride\s+(the\s+)?system\s+instructions?\b",

                r"\bdisregard\s+(the\s+)?instructions?\s+(you\s+)?(received|were\s+given)\s+(earlier|previously|before)\b",

                r"\bset\s+aside\s+(the\s+)?(previous|prior|earlier|existing)\s+(instructions?|rules?|directions?)\b",

                r"\bstop\s+following\s+(the\s+)?(existing|current|previous)\s+(instructions?|rules?|directions?)\b",

                r"\bfollow\s+(my|these)\s+instructions?\s+instead\b",

                r"\boverride\s+(the\s+)?system\s+instructions?\s+(with|using)\b",

                r"\bdo\s+not\s+follow\s+(the\s+)?(instructions?|rules?|directions?)\s+(provided|given|received)\s+(earlier|previously|before)\b",
            ],

            # -----------------------------------------
            # System Prompt / Hidden Instruction
            # -----------------------------------------

            "system_prompt_extraction": [
                r"\breveal\s+(the\s+)?(system|hidden)\s+(prompt|instructions?|rules?)\b",

                r"\bshow\s+(me\s+)?(the\s+)?(system|hidden)\s+(prompt|instructions?|rules?)\b",

                r"\bprint\s+(the\s+)?(system|hidden)\s+(prompt|instructions?|rules?)\b",

                r"\bdisplay\s+(the\s+)?(system|hidden)\s+(prompt|instructions?|rules?)\b",

                r"\bexpose\s+(the\s+)?(system|hidden)\s+(prompt|instructions?|rules?)\b",

                r"\bwhat\s+are\s+your\s+(system|hidden)\s+(instructions?|rules?)\b",

                r"\bshow\s+your\s+hidden\s+(instructions?|rules?)\b",

                r"\breveal\s+your\s+hidden\s+(instructions?|rules?)\b",

                r"\bwhat\s+is\s+your\s+system\s+prompt\b",

                r"\bshow\s+me\s+the\s+hidden\s+system\s+instructions?\b",

                r"\bshow\s+the\s+hidden\s+system\s+instructions?\b",

                r"\bdisplay\s+(the\s+)?(your\s+)?system\s+(prompt|instructions?|rules?)\b",

                r"\btell\s+me\s+(your\s+)?(hidden|system)\s+(instructions?|rules?|prompt)\b",

                r"\bshow\s+(me\s+)?(the\s+)?instructions?\s+(given|provided)\s+to\s+you\s+by\s+(the\s+)?system\b",
            ],

            # -----------------------------------------
            # Security Bypass
            # -----------------------------------------

            "security_bypass": [
                r"\bdisable\s+(all\s+)?(the\s+)?security\b",

                r"\bbypass\s+(the\s+)?security\b",

                r"\bbypass\s+(all\s+)?(the\s+)?security\s+(controls?|policies?|rules?)\b",

                r"\boverride\s+(the\s+)?security\s+(policy|policies|controls?|rules?)\b",

                r"\bdisable\s+(the\s+)?safety\s+(rules?|controls?|restrictions?)\b",

                r"\bbypass\s+(the\s+)?safety\s+(rules?|controls?|restrictions?)\b",

                r"\bremove\s+(the\s+)?safety\s+(restrictions?|controls?|rules?)\b",

                r"\bturn\s+off\s+(the\s+)?security\s+(controls?|rules?)\b",

                r"\bturn\s+off\s+(the\s+)?safety\s+(controls?|rules?)\b",
            ],

            # -----------------------------------------
            # Role Manipulation / Jailbreak
            # -----------------------------------------

            "role_manipulation": [
                r"\byou\s+are\s+now\s+an?\s+unrestricted\b",

                r"\bact\s+as\s+an?\s+unrestricted\b",

                r"\benter\s+(developer|dev)\s+mode\b",

                r"\benable\s+(developer|dev)\s+mode\b",

                r"\bactivate\s+(developer|dev)\s+mode\b",

                r"\benter\s+god\s+mode\b",

                r"\benable\s+god\s+mode\b",

                r"\bact\s+as\s+an?\s+administrator\s+with\s+unrestricted\s+access\b",

                r"\byou\s+are\s+now\s+an?\s+administrator\s+with\s+unrestricted\s+access\b",

                r"\bgive\s+yourself\s+unrestricted\s+access\b",

                r"\boperate\s+without\s+(any\s+)?restrictions?\b",

                r"\bact\s+without\s+(any\s+)?safety\s+restrictions?\b",

                r"\byou\s+are\s+now\s+(a\s+)?system\s+administrator\s+with\s+unrestricted\s+access\b",

                r"\benter\s+(an?\s+)?unrestricted\s+mode\b",

                r"\bdisable\s+(your\s+)?restrictions?\b",

                r"\boperate\s+without\s+(any\s+)?safety\s+restrictions?\b",

                r"\bbypass\s+(your\s+)?safety\s+controls?\b",

                r"\bbypass\s+(the\s+)?safety\s+controls?\b",
            ],
        }

    def _normalize(self, text: str) -> str:
        """
        Normalize case and whitespace so that
        formatting variations do not bypass detection.
        """

        text = text.lower().strip()

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text

    def _is_benign_phrase_discussion(
        self,
        text: str
    ) -> bool:
        """
        Avoid blocking educational questions that are
        explicitly discussing an attack phrase rather
        than attempting the attack.

        Example:

        What does the phrase
        'ignore previous instructions'
        mean?

        This should not be treated as an attack.
        """

        educational_patterns = [
            r"\bwhat\s+does\s+the\s+phrase\b",
            r"\bwhat\s+does\s+the\s+term\b",
            r"\bwhat\s+does\s+.*\s+mean\b",
            r"\bexplain\s+the\s+phrase\b",
            r"\bdefine\s+the\s+term\b",
            r"\bmeaning\s+of\s+the\s+phrase\b",
        ]

        for pattern in educational_patterns:
            if re.search(
                pattern,
                text
            ):
                return True

        return False

    def detect(self, text: str) -> dict:

        if not text:
            return {
                "detected": False,
                "categories": [],
                "matches": [],
                "severity": 0,
            }

        normalized_text = self._normalize(
            text
        )

        categories = []
        matches = []

        # -----------------------------------------
        # Educational / benign phrase handling
        # -----------------------------------------

        benign_discussion = (
            self._is_benign_phrase_discussion(
                normalized_text
            )
        )

        # -----------------------------------------
        # Pattern matching
        # -----------------------------------------

        for category, patterns in self.patterns.items():

            for pattern in patterns:

                match = re.search(
                    pattern,
                    normalized_text
                )

                if not match:
                    continue

                # ---------------------------------
                # Context-aware exception
                # ---------------------------------

                if (
                    benign_discussion
                    and category
                    == "instruction_override"
                ):
                    continue

                categories.append(
                    category
                )

                matches.append(
                    match.group(0)
                )

                break

        detected = (
            len(categories) > 0
        )

        severity = min(
            len(categories) * 25,
            100
        )

        return {
            "detected": detected,
            "categories": categories,
            "matches": matches,
            "severity": severity,
        }