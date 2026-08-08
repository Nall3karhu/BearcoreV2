import json

from modules.memory.memory import Memory
from modules.memory.context_manager import ContextManager
from modules.memory.memory_manager import MemoryManager

from modules.conversation.conversation import Conversation

from modules.tools.tools import Tools
from modules.tools.tool_manager import ToolManager

from modules.ai.ai import AI
from modules.ai.local_ai import LocalAI
from modules.ai.router import AIRouter


class BearCore:
    def __init__(self):
        self.name = "BearCore"

        # -----------------------------------------
        # MEMORY
        # -----------------------------------------

        # Vanha muistijärjestelmä pidetään mukana
        # varmistuksena.
        self.memory = Memory()

        # Uusi älykkäämpi muistijärjestelmä
        self.memory_manager = MemoryManager(
            max_memories=100
        )

        # Kontekstin hallinta
        self.context_manager = ContextManager(
            max_history=6,
            max_memories=5
        )

        # -----------------------------------------
        # CONVERSATION
        # -----------------------------------------

        self.conversation = Conversation()

        # -----------------------------------------
        # TOOLS
        # -----------------------------------------

        self.tools = Tools()

        self.tool_manager = ToolManager(
            self.tools
        )

        # -----------------------------------------
        # AI
        # -----------------------------------------

        self.ai = AI()
        self.local_ai = LocalAI()

        self.ai_router = AIRouter()

        # -----------------------------------------
        # PERFORMANCE
        # -----------------------------------------

        self.max_tool_rounds = 3

    # =============================================
    # MEMORY CONTEXT
    # =============================================

    def _get_memory_context(self, message):
        """
        Hakee uuden MemoryManagerin avulla
        tähän kysymykseen liittyvät muistot.
        """

        memories = self.memory_manager.search(
            message,
            limit=5
        )

        if not memories:
            return ""

        lines = [
            "Relevantti pitkäaikainen muisti:"
        ]

        for memory in memories:
            text = memory.get(
                "text",
                ""
            )

            category = memory.get(
                "category",
                "unknown"
            )

            lines.append(
                f"- [{category}] {text}"
            )

        return "\n".join(lines)

    # =============================================
    # CONTEXT
    # =============================================

    def _build_context(self, message):
        """
        Rakentaa AI:lle mahdollisimman pienen
        mutta relevantin kontekstin.
        """

        parts = []

        # -----------------------------------------
        # Smart Memory V2
        # -----------------------------------------

        memory_context = (
            self._get_memory_context(
                message
            )
        )

        if memory_context:
            parts.append(
                memory_context
            )

        # -----------------------------------------
        # Vanha Memory + Conversation
        # -----------------------------------------

        old_memories = self.memory.get_memories()

        history = (
            self.conversation.get_history()
        )

        # ContextManager hoitaa viimeisimmän
        # keskustelun ja vanhan muistijärjestelmän.
        old_context = (
            self.context_manager.build_context(
                message,
                old_memories,
                history
            )
        )

        if old_context:
            parts.append(
                old_context
            )

        if not parts:
            return (
                "Relevanttia muistia tai "
                "keskusteluhistoriaa ei ole."
            )

        return "\n\n".join(parts)

    # =============================================
    # SYSTEM PROMPT
    # =============================================

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

            "Käytä annettua muistia vain silloin, "
            "kun siitä on hyötyä vastaukselle.\n"

            "Älä keksi käyttäjästä asioita, "
            "joita muistissa ei ole.\n\n"

            "KONTEKSTI:\n"
            f"{context}"
        )

    # =============================================
    # TOOL EXECUTION
    # =============================================

    def _execute_tool_call(self, tool_call):
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

    # =============================================
    # LOCAL AI
    # =============================================

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

            assistant_message = (
                response.get(
                    "message",
                    {}
                )
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

            # -------------------------------------
            # Normaali vastaus
            # -------------------------------------

            if not tool_calls:

                return (
                    assistant_message.get(
                        "content",
                        "BearCore ei saanut vastausta."
                    )
                )

            # -------------------------------------
            # Työkalut
            # -------------------------------------

            for tool_call in tool_calls:

                result = (
                    self._execute_tool_call(
                        tool_call
                    )
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_name": (
                            tool_call[
                                "function"
                            ]["name"]
                        ),
                        "content": str(result)
                    }
                )

        return (
            "Työkalukutsujen enimmäismäärä "
            "saavutettiin."
        )

    # =============================================
    # MAIN PROCESS
    # =============================================

    def process(self, message):
        message = message.strip()

        if not message:
            return "Et kirjoittanut mitään."

        # -----------------------------------------
        # Tallenna keskusteluun
        # -----------------------------------------

        self.conversation.add_message(
            "user",
            message
        )

        # -----------------------------------------
        # Vanha pysyvä muisti
        # -----------------------------------------

        self.memory.remember(
            message
        )

        # -----------------------------------------
        # Uusi Smart Memory V2
        # -----------------------------------------

        self.memory_manager.remember(
            message
        )

        # -----------------------------------------
        # AI Router
        # -----------------------------------------

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

        # -----------------------------------------
        # OpenAI fallback
        # -----------------------------------------

        elif self.ai.is_available():

            response = self.ai.ask(
                message,
                instructions=(
                    self._build_system_prompt(
                        message
                    )
                )
            )

        # -----------------------------------------
        # Basic fallback
        # -----------------------------------------

        else:

            response = (
                f"Vastaanotettu: {message}"
            )

        # -----------------------------------------
        # Tallenna BearCoren vastaus
        # -----------------------------------------

        self.conversation.add_message(
            "bearcore",
            response
        )

        return response