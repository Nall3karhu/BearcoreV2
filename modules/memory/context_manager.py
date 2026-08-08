import re


class ContextManager:
    def __init__(
        self,
        max_history=6,
        max_memories=5
    ):
        self.max_history = max_history
        self.max_memories = max_memories

    def _words(self, text):
        return set(
            re.findall(
                r"\b[\wäöåÄÖÅ]+\b",
                text.lower()
            )
        )

    def _memory_score(self, message, memory):
        message_words = self._words(message)
        memory_words = self._words(memory)

        if not message_words or not memory_words:
            return 0

        common_words = (
            message_words & memory_words
        )

        return len(common_words)

    def select_memories(
        self,
        message,
        memories
    ):
        if not memories:
            return []

        scored = []

        for index, memory in enumerate(memories):
            score = self._memory_score(
                message,
                str(memory)
            )

            scored.append(
                (
                    score,
                    index,
                    memory
                )
            )

        scored.sort(
            key=lambda item: (
                item[0],
                item[1]
            ),
            reverse=True
        )

        relevant = [
            item[2]
            for item in scored
            if item[0] > 0
        ]

        if not relevant:
            relevant = list(
                memories[-self.max_memories:]
            )

        return relevant[
            :self.max_memories
        ]

    def build_context(
        self,
        message,
        memories,
        history
    ):
        parts = []

        selected_memories = (
            self.select_memories(
                message,
                memories
            )
        )

        if selected_memories:
            parts.append("Relevantti muisti:")

            for memory in selected_memories:
                parts.append(
                    f"- {memory}"
                )

        recent_history = history[
            -self.max_history:
        ]

        if recent_history:
            parts.append(
                "\nViimeisin keskustelu:"
            )

            for item in recent_history:
                role = item.get(
                    "role",
                    "unknown"
                )

                content = item.get(
                    "content",
                    ""
                )

                parts.append(
                    f"{role}: {content}"
                )

        if not parts:
            return (
                "Relevanttia muistia tai "
                "keskusteluhistoriaa ei ole."
            )

        return "\n".join(parts)