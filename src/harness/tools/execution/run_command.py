import asyncio
import os
import signal
import subprocess

from harness.tools.async_base_tool import AsyncBaseTool
from .process_terminator import ProcessTerminator


class RunCommandTool(AsyncBaseTool):

    def __init__(self, process_terminator: ProcessTerminator):
        self.process_terminator = process_terminator

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


    async def execute(self, command: str, timeout: int = 30) -> str:
        creationflags = 0
        start_new_session = False

        if os.name == "nt":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            start_new_session = True

        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            creationflags=creationflags,
            start_new_session=start_new_session,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )

        except asyncio.TimeoutError:
            try:
                await self.process_terminator.terminate(process)
                return f"Command timed out after {timeout} seconds"

            except Exception as exc:
                return (
                    f"Command timed out after {timeout} seconds; "
                    f"process cleanup failed: {exc}"
                )

        except asyncio.CancelledError:
            try:
                await self.process_terminator.terminate(process)
            except Exception:
                pass
            raise

        stdout = stdout.decode().replace("\r\n", "\n")
        stderr = stderr.decode().replace("\r\n", "\n")

        return (
            f"Exit code: {process.returncode}\n"
            f"STDOUT:\n{stdout}"
            f"STDERR:\n{stderr}"
        )