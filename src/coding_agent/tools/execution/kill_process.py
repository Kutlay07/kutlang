from ..base_tool import BaseTool
from .process_manager import ProcessManager


class KillProcessTool(BaseTool):
    def __init__(self, process_manager: ProcessManager):
        self.process_manager = process_manager

    @property
    def name(self) -> str:
        return "kill_process"

    @property
    def description(self) -> str:
        return "Terminate a background process"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "process_id": {
                    "type": "integer",
                    "description": "ID of the background process to terminate.",
                },
            },
            "required": ["process_id"],
            "additionalProperties": False,
        }

    def execute(self, process_id: int) -> str:
        process = self.process_manager.get(process_id)

        process.terminate()
        self.process_manager.remove(process_id)

        return f"Successfully terminated process: {process_id}"