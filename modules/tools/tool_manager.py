class ToolManager:
    def __init__(self, tools):
        self.tools = tools

    def get_available_tools(self):
        return self.tools.get_available_tools()

    def execute(self, tool_name, *args, **kwargs):
        return self.tools.execute(
            tool_name,
            *args,
            **kwargs
        )

    def describe_tools(self):
        descriptions = {
            "time": "Hakee tämänhetkisen kellonajan.",
            "date": "Hakee tämänhetkisen päivämäärän.",
            "list_files": "Listaa kansion sisältämät tiedostot ja kansiot.",
            "calculator": "Laskee kahden luvun välisen laskutoimituksen.",
        }

        available = self.get_available_tools()

        return {
            name: descriptions.get(
                name,
                "Työkalu ilman kuvausta."
            )
            for name in available
        }