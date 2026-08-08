import json

from modules.memory.memory import Memory
from modules.memory.context_manager import ContextManager

from modules.conversation.conversation import Conversation

from modules.tools.tools import Tools
from modules.tools.tool_manager import ToolManager

from modules.ai.ai import AI
from modules.ai.local_ai import LocalAI
from modules.ai.router import AIRouter


class BearCore:
    def __init__(self):
        self.name = "BearCore"

        # Memory
        self.memory = Memory()

        # Smart context
        self.context_manager = ContextManager(
            max_history=6,
            max_memories=5
        )

        # Conversation
        self.conversation = Conversation()

        # Tools
        self.tools = Tools()
        self.tool_manager = ToolManager(
            self.tools
        )

        # AI
        self.ai = AI()
        self.local_ai = LocalAI()

        # AI Router
        self.ai_router = AIRouter()

        # Performance
        self.max_tool_rounds = 3

    def _build_context(self, message):
        memories = self.memory.get_memories()

        history = (
            self.conversation.get_history()
        )

        return self.context_manager.build_context(
            message,
            memories,
            history
        )

    def _build_system_prompt(self, message):
        context = self._build_context(
            message
        )

        return (
            "Olet BearCore, käyttäjän "
            "henkilökohtainen AI-avustaja.\n\n"

            "Vastaa luonnollisesti, rennosti "
            "ja suomeksi.\n"

            "Ole yleensä ytimekäs, ellei käyttäjä "
            "pyydä tarkempaa selitystä.\n\n"

            "Käytä alla olevaa kontekstia vain "
            "tarvittaessa.\n"

            "Älä keksi käyttäjästä asioita, "
            "joita kontekstissa ei ole.\n\n"

            f"{context}"
        )

    def _execute_tool_call(
        self,
        tool_call
    ):
        function = tool_call.get(
            "function",
            {}
        )

        tool_name = function.get(
            "name"
        )

        arguments = function.get(
            "arguments",
            {}
        )

        if isinstance(
            arguments,
            str
        ):
            try:
                arguments = json.loads(
                    arguments
                )

            except json.JSONDecodeError:
                arguments = {}

        return self.tool_manager.execute(
            tool_name,
            **arguments
        )

    def _run_local_ai(
        self,
        message,
        ai
    ):
        messages = [
            {
                "role": "system",
                "content": (
                    self._build_system_prompt(
                        message
                    )
                )
            },
            {
                "role": "user",
                "content": message
            }
        ]

        tools = (
            self.tools.get_tool_schemas()
        )

        for _ in range(
            self.max_tool_rounds
        ):
            response = ai.chat(
                messages,
                tools=tools,
                think=False
            )

            if "error" in response:
                return response["error"]

            assistant_message = response.get(
                "message",
                {}
            )

            messages.append(
                assistant_message
            )

            tool_calls = (
                assistant_message.get(
                    "tool_calls",
                    []
                )
            )

            if not tool_calls:
                return assistant_message.get(
                    "content",
                    "BearCore ei saanut vastausta."
                )

            for tool_call in tool_calls:
                result = (
                    self._execute_tool_call(
                        tool_call
                    )
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_name": tool_call[
                            "function"
                        ]["name"],
                        "content": str(result)
                    }
                )

        return (
            "Työkalukutsujen enimmäismäärä "
            "saavutettiin."
        )

    def process(self, message):
        message = message.strip()

        if not message:
            return "Et kirjoittanut mitään."

        # Save user message
        self.conversation.add_message(
            "user",
            message
        )

        # Save to persistent memory
        self.memory.remember(
            message
        )

        # Local AI
        if self.ai_router.is_available():

            selected_ai = (
                self.ai_router.get_ai(
                    message
                )
            )

            response = self._run_local_ai(
                message,
                selected_ai
            )

        # OpenAI fallback
        elif self.ai.is_available():

            response = self.ai.ask(
                message,
                instructions=(
                    self._build_system_prompt(
                        message
                    )
                )
            )

        # Basic fallback
        else:

            response = (
                f"Vastaanotettu: {message}"
            )

        # Save response
        self.conversation.add_message(
            "bearcore",
            response
        )

        return response