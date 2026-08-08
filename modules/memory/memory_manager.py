import re
from datetime import datetime


class MemoryManager:
    """
    BearCoren älykkäämpi muistikerros.

    Vastuu:
    - tunnistaa muistettavia asioita
    - luokitella niitä
    - hakea olennaisia muistoja
    - pitää muisti rajattuna
    """

    def __init__(self, max_memories=100):
        self.max_memories = max_memories
        self.memories = []

    # -----------------------------------------
    # NORMALISOINTI
    # -----------------------------------------

    def _normalize(self, text):
        return re.sub(
            r"\s+",
            " ",
            str(text).strip()
        )

    def _words(self, text):
        return set(
            re.findall(
                r"\b[\wäöåÄÖÅ]+\b",
                str(text).lower()
            )
        )

    # -----------------------------------------
    # LUOKITTELU
    # -----------------------------------------

    def classify(self, text):
        text_lower = text.lower()

        if any(
            word in text_lower
            for word in [
                "haluan",
                "haluisin",
                "tavoite",
                "tarkoitus",
                "suunnitelma",
            ]
        ):
            return "goal"

        if any(
            word in text_lower
            for word in [
                "bearcore",
                "projekti",
                "moduuli",
                "ohjelma",
                "kehitys",
            ]
        ):
            return "project"

        if any(
            word in text_lower
            for word in [
                "tykkään",
                "pidän",
                "kiinnostaa",
                "mieluummin",
                "haluan käyttää",
            ]
        ):
            return "preference"

        if any(
            word in text_lower
            for word in [
                "muista",
                "muista että",
                "pidä mielessä",
            ]
        ):
            return "fact"

        return "conversation"

    # -----------------------------------------
    # TALLENNUS
    # -----------------------------------------

    def remember(self, text):
        text = self._normalize(text)

        if not text:
            return None

        category = self.classify(text)

        memory = {
            "text": text,
            "category": category,
            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            ),
        }

        self.memories.append(memory)

        if len(self.memories) > self.max_memories:
            self.memories.pop(0)

        return memory

    # -----------------------------------------
    # HAKU
    # -----------------------------------------

    def search(self, query, limit=5):
        query_words = self._words(query)

        if not query_words:
            return []

        scored = []

        for memory in self.memories:
            memory_words = self._words(
                memory["text"]
            )

            score = len(
                query_words & memory_words
            )

            if score > 0:
                scored.append(
                    (
                        score,
                        memory
                    )
                )

        scored.sort(
            key=lambda item: item[0],
            reverse=True
        )

        return [
            memory
            for _, memory in scored[:limit]
        ]

    # -----------------------------------------
    # KATEGORIAN HAKU
    # -----------------------------------------

    def get_by_category(
        self,
        category,
        limit=10
    ):
        return [
            memory
            for memory in self.memories
            if memory["category"] == category
        ][-limit:]

    # -----------------------------------------
    # KAIKKI MUISTIT
    # -----------------------------------------

    def get_all(self):
        return list(self.memories)

    # -----------------------------------------
    # POISTA
    # -----------------------------------------

    def clear(self):
        self.memories.clear()