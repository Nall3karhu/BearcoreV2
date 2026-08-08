import json
from pathlib import Path


class Memory:
    def __init__(self, storage_file="data/memory.json"):
        self.storage_file = Path(storage_file)
        self.memories = []

        self._ensure_storage()
        self._load()

    def _ensure_storage(self):
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.storage_file.exists():
            self.storage_file.write_text(
                "[]",
                encoding="utf-8"
            )

    def _load(self):
        try:
            data = json.loads(
                self.storage_file.read_text(encoding="utf-8")
            )

            if isinstance(data, list):
                self.memories = data
            else:
                self.memories = []

        except (json.JSONDecodeError, OSError):
            self.memories = []

    def _save(self):
        self.storage_file.write_text(
            json.dumps(
                self.memories,
                ensure_ascii=False,
                indent=4
            ),
            encoding="utf-8"
        )

    def remember(self, text):
        text = text.strip()

        if not text:
            return

        self.memories.append(text)
        self._save()

    def get_memories(self):
        return self.memories.copy()

    def get_last_memory(self):
        if not self.memories:
            return None

        return self.memories[-1]

    def count(self):
        return len(self.memories)

    def clear(self):
        self.memories.clear()
        self._save()