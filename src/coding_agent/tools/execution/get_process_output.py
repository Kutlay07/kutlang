from ..base_tool import BaseTool
from .process_manager import ProcessManager


class GetProcessOutputTool(BaseTool):
    def __init__(self, process_manager: ProcessManager):
        self.process_manager = process_manager

    @property
    def name(self) -> str:
        return "get_process_output"

    @property
    def description(self) -> str:
        return "Get the output of a background process"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "process_id": {
                    "type": "integer",
                    "description": "ID of the background process.",
                },
            },
            "required": ["process_id"],
            "additionalProperties": False,
        }

    def execute(self, process_id: int) -> str:
        process = self.process_manager.get(process_id)

        stdout, stderr = process.communicate()

        self.process_manager.remove(process_id)

        return (
            f"STDOUT:\n{stdout}"
            f"STDERR:\n{stderr}"
        )