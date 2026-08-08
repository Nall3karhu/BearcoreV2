import re


class AutoMemory:
    """Tunnistaa keskustelusta pitkäaikaisesti hyödyllisiä asioita."""

    def __init__(self):
        self.memory_patterns = [
            r"\bmuista\b",
            r"\bpidä mielessä\b",
            r"\bhaluan\b",
            r"\bhaluisin\b",
            r"\btavoite\b",
            r"\btavoitteena\b",
            r"\bsuunnitelma\b",
            r"\bsuunnitelmana\b",
            r"\btarkoitus on\b",
            r"\baion\b",
            r"\bprojekti\b",
            r"\bkehitetään\b",
            r"\brakennetaan\b",
            r"\bpidän\b",
            r"\btykkään\b",
            r"\bmieluummin\b",
        ]

        self.ignore_patterns = [
            r"^\s*joo\s*[.!?]*\s*$",
            r"^\s*juu\s*[.!?]*\s*$",
            r"^\s*okei\s*[.!?]*\s*$",
            r"^\s*ok\s*[.!?]*\s*$",
            r"^\s*yep\s*[.!?]*\s*$",
            r"^\s*yes\s*[.!?]*\s*$",
            r"^\s*kiitos\s*[.!?]*\s*$",
            r"^\s*hei\s*[.!?]*\s*$",
            r"^\s*moikka\s*[.!?]*\s*$",
        ]

    def should_remember(self, text):
        if not text:
            return False

        text = str(text).strip()

        if len(text) < 12:
            return False

        for pattern in self.ignore_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False

        return any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in self.memory_patterns
        )

    def extract(self, text):
        if not self.should_remember(text):
            return None

        return {
            "text": str(text).strip(),
            "source": "auto",
        }