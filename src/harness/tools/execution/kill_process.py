from harness.tools.async_base_tool import AsyncBaseTool
from harness.tools.execution.process_terminator import ProcessTerminator
from .process_manager import ProcessManager


class KillProcessTool(AsyncBaseTool):
    def __init__(
        self, 
        process_manager: ProcessManager,
        process_terminator: ProcessTerminator,
        ):
        self.process_manager = process_manager
        self.process_terminator = process_terminator

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

    async def execute(self, process_id: int) -> str:
        managed = self.process_manager.get(process_id)
        process = managed.process

        if process.returncode is None:
            await self.process_terminator.terminate(process)

        managed.stdout_path.unlink(missing_ok=True)
        managed.stderr_path.unlink(missing_ok=True)
        self.process_manager.remove(process_id)
        
        return f"Successfully terminated process: {process_id}"