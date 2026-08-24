import os
import signal
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
        creationflags = 0

        if os.name == "nt":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=creationflags,
        )

        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            self._terminate_process_group(process)

            stdout, stderr = process.communicate()

            return f"Command timed out after {timeout} seconds"

        return (
            f"Exit code: {process.returncode}\n"
            f"STDOUT:\n{stdout}"
            f"STDERR:\n{stderr}"
        )

    @staticmethod
    def _terminate_process_group(process: subprocess.Popen) -> None:
        if process.poll() is not None:
            return

        if os.name == "nt":
            subprocess.run(
                [
                    "taskkill",
                    "/PID",
                    str(process.pid),
                    "/T",
                    "/F",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        else:
            os.killpg(
                os.getpgid(process.pid),
                signal.SIGTERM,
            )
