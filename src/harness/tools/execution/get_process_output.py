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
        managed = self.process_manager.get(process_id)

        try:
            managed.process.wait()

            stdout = managed.stdout_path.read_text(encoding="utf-8")
            stderr = managed.stderr_path.read_text(encoding="utf-8")

            return (
                f"STDOUT:\n{stdout}"
                f"STDERR:\n{stderr}"
            )
        finally:
            managed.stdout_path.unlink(missing_ok=True)
            managed.stderr_path.unlink(missing_ok=True)
            self.process_manager.remove(process_id)
