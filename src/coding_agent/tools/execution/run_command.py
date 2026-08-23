import subprocess

from ..base_tool import BaseTool


class RunCommandTool(BaseTool):
    @property
    def name(self) -> str:
        return "run_command"

    @property
    def description(self) -> str:
        return "Execute a shell command"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Command to execute.",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Maximum execution time in seconds.",
                    "default": 30,
                },
            },
            "required": ["command"],
            "additionalProperties": False,
        }

    def execute(self, command: str, timeout: int = 30) -> str:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return f"Command timed out after {timeout} seconds"

        return (
            f"Exit code: {result.returncode}\n"
            f"STDOUT:\n{result.stdout}"
            f"STDERR:\n{result.stderr}"
        )