from modules.ai.local_ai import LocalAI


class AIRouter:
    def __init__(self):
        self.quick_ai = LocalAI(model="qwen3:1.7b")
        self.smart_ai = LocalAI(model="qwen3:8b")

    def is_available(self):
        return (
            self.quick_ai.is_available()
            or self.smart_ai.is_available()
        )

    def choose_model(self, message):
        message_lower = message.lower()

        smart_keywords = [
            "suunnittele",
            "analysoi",
            "analysointi",
            "kehitä",
            "kehittäminen",
            "ohjelmoi",
            "koodi",
            "selitä tarkasti",
            "robotti",
            "robottikäsi",
            "bearcore",
            "arkkitehtuuri",
            "järjestelmä",
        ]

        tool_keywords = [
            "paljonko",
            "laske",
            "lask",
            "kello",
            "aika",
            "päivämäärä",
            "tiedostot",
            "tiedosto",
        ]

        if any(
            keyword in message_lower
            for keyword in smart_keywords
        ):
            return "smart"

        if any(
            keyword in message_lower
            for keyword in tool_keywords
        ):
            return "quick"

        if len(message) > 250:
            return "smart"

        return "quick"

    def get_ai(self, message):
        selected = self.choose_model(message)

        if selected == "smart":
            if self.smart_ai.is_available():
                return self.smart_ai

            return self.quick_ai

        if self.quick_ai.is_available():
            return self.quick_ai

        return self.smart_ai

    def get_model_name(self, message):
        ai = self.get_ai(message)
        return ai.get_model()