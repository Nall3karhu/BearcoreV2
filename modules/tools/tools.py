from datetime import datetime
from pathlib import Path
import operator


class Tools:
    def __init__(self):
        self.tools = {
            "time": self.get_time,
            "date": self.get_date,
            "list_files": self.list_files,
            "calculator": self.calculator,
        }

    def get_available_tools(self):
        return list(self.tools.keys())

    def execute(self, tool_name, *args, **kwargs):
        tool = self.tools.get(tool_name)

        if tool is None:
            return f"Työkalua '{tool_name}' ei löydy."

        try:
            return tool(*args, **kwargs)

        except Exception as error:
            return f"Työkalun suorittamisessa tapahtui virhe: {error}"

    def get_time(self):
        return datetime.now().strftime("%H:%M:%S")

    def get_date(self):
        return datetime.now().strftime("%d.%m.%Y")

    def list_files(self, directory="."):
        path = Path(directory)

        if not path.exists():
            return f"Kansiota ei löydy: {directory}"

        if not path.is_dir():
            return f"Kyseessä ei ole kansio: {directory}"

        files = [item.name for item in path.iterdir()]

        if not files:
            return "Kansio on tyhjä."

        return files

    def calculator(self, a, b, operation):
        operations = {
            "add": operator.add,
            "subtract": operator.sub,
            "multiply": operator.mul,
            "divide": operator.truediv,
        }

        if operation not in operations:
            return (
                "Tuntematon laskutoimitus. "
                "Käytä: add, subtract, multiply tai divide."
            )

        if operation == "divide" and b == 0:
            return "Nollalla ei voi jakaa."

        result = operations[operation](a, b)

        if isinstance(result, float) and result.is_integer():
            result = int(result)

        return result

    def get_tool_schemas(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "time",
                    "description": "Hakee tämänhetkisen kellonajan.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "date",
                    "description": "Hakee tämänhetkisen päivämäärän.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "Listaa annetun kansion tiedostot ja kansiot.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Listattavan kansion polku.",
                            }
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "calculator",
                    "description": "Laskee kahden luvun välisen laskutoimituksen.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "a": {
                                "type": "number",
                                "description": "Ensimmäinen luku.",
                            },
                            "b": {
                                "type": "number",
                                "description": "Toinen luku.",
                            },
                            "operation": {
                                "type": "string",
                                "enum": [
                                    "add",
                                    "subtract",
                                    "multiply",
                                    "divide",
                                ],
                                "description": "Laskutoimitus.",
                            },
                        },
                        "required": [
                            "a",
                            "b",
                            "operation",
                        ],
                    },
                },
            },
        ]