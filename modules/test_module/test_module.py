"""BearCore module."""


class TestModule:
    """Uuden BearCore-moduulin pohja."""

    def __init__(self):
        self.name = "test_module"

    def status(self):
        return {
            "module": self.name,
            "status": "ready",
        }
