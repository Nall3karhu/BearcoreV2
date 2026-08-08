import os

from dotenv import load_dotenv


class AI:
    def __init__(self, model="gpt-5.5"):
        self.model = model
        self.client = None
        self.enabled = False

        load_dotenv()
        self._initialize()

    def _initialize(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            return

        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=api_key)
            self.enabled = True

        except ImportError:
            self.client = None
            self.enabled = False

    def is_available(self):
        return self.enabled

    def ask(self, message, instructions=None):
        if not self.enabled:
            return (
                "AI ei ole käytössä. "
                "Tarkista OPENAI_API_KEY."
            )

        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=instructions,
                input=message,
            )

            return response.output_text

        except Exception as error:
            return f"AI-virhe: {error}"

    def get_model(self):
        return self.model

    def set_model(self, model):
        self.model = model