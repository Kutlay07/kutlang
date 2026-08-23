import subprocess

from ..base_tool import BaseTool
from .process_manager import ProcessManager


class RunBackgroundCommandTool(BaseTool):
    def __init__(self, process_manager: ProcessManager):
        self.process_manager = process_manager

    @property
    def name(self) -> str:
        return "run_background_command"

    @property
    def description(self) -> str:
        return "Start a command as a background process"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Command to execute in the background.",
                },
            },
            "required": ["command"],
            "additionalProperties": False,
        }

    def execute(self, command: str) -> str:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        self.process_manager.add(process)

        return f"Started process: {process.pid}"