import asyncio
import os
import signal
import subprocess

from harness.tools.async_base_tool import AsyncBaseTool


class RunCommandTool(AsyncBaseTool):
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
                await self._terminate_process_group(process)
                return f"Command timed out after {timeout} seconds"

            except Exception as exc:
                return (
                    f"Command timed out after {timeout} seconds; "
                    f"process cleanup failed: {exc}"
                )

        except asyncio.CancelledError:
            await self._terminate_process_group(process)
            raise

        stdout = stdout.decode().replace("\r\n", "\n")
        stderr = stderr.decode().replace("\r\n", "\n")

        return (
            f"Exit code: {process.returncode}\n"
            f"STDOUT:\n{stdout}"
            f"STDERR:\n{stderr}"
        )


    @staticmethod
    async def _terminate_process_group(
        process: asyncio.subprocess.Process,
        ) -> None:

        if process.returncode is not None:
            return

        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                check=False,
                capture_output=True,
                text=True,
            )
            await process.wait()

        else:
            try:
                pgid = os.getpgid(process.pid)

                if pgid <= 1:
                    return

                os.killpg(pgid, signal.SIGTERM)

                await asyncio.wait_for(
                    process.wait(),
                    timeout=2,
                )

            except asyncio.TimeoutError:
                os.killpg(pgid, signal.SIGKILL)
                await process.wait()