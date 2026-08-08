import json
import urllib.request
import urllib.error


class LocalAI:
    def __init__(
        self,
        model="qwen3:8b",
        host="http://localhost:11434"
    ):
        self.model = model
        self.host = host.rstrip("/")

    def is_available(self):
        try:
            request = urllib.request.Request(
                f"{self.host}/api/tags",
                method="GET"
            )

            with urllib.request.urlopen(request, timeout=5):
                return True

        except (urllib.error.URLError, TimeoutError):
            return False

    def chat(self, messages, tools=None, think=False):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "think": think,
        }

        if tools:
            payload["tools"] = tools

        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            f"{self.host}/api/chat",
            data=data,
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=120
            ) as response:

                return json.loads(
                    response.read().decode("utf-8")
                )

        except urllib.error.URLError as error:
            return {
                "error": f"Local AI -yhteysvirhe: {error}"
            }

        except TimeoutError:
            return {
                "error": "Local AI:n vastaus kesti liian kauan."
            }

        except json.JSONDecodeError:
            return {
                "error": "Local AI palautti virheellisen vastauksen."
            }

    def ask(self, message, system_prompt=None):
        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        messages.append({
            "role": "user",
            "content": message
        })

        response = self.chat(
            messages,
            think=False
        )

        if "error" in response:
            return response["error"]

        return response.get(
            "message",
            {}
        ).get(
            "content",
            "Paikallinen AI ei palauttanut vastausta."
        )

    def get_model(self):
        return self.model

    def set_model(self, model):
        self.model = model