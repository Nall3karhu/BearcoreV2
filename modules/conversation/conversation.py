class Conversation:
    def __init__(self):
        self.history = []

    def add_message(self, role, content):
        message = {
            "role": role,
            "content": content
        }

        self.history.append(message)

    def get_history(self):
        return self.history

    def get_last_message(self):
        if not self.history:
            return None

        return self.history[-1]

    def clear(self):
        self.history.clear()