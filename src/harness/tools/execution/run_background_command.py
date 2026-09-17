import asyncio
import os
from pathlib import Path
import subprocess
import tempfile

from harness.tools.async_base_tool import AsyncBaseTool
from harness.tools.execution.process_terminator import ProcessTerminator
from .process_manager import ManagedProcess, ProcessManager


class RunBackgroundCommandTool(AsyncBaseTool):
    def __init__(
        self, 
        process_manager: ProcessManager,
        process_terminator: ProcessTerminator,
        ):
        self.process_manager = process_manager
        self.process_terminator = process_terminator

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

    async def execute(self, command: str) -> str:
        stdout_file = tempfile.NamedTemporaryFile(
            mode="w+",
            encoding="utf-8",
            delete=False,
        )
        stderr_file = tempfile.NamedTemporaryFile(
            mode="w+",
            encoding="utf-8",
            delete=False,
        )

        stdout_path = Path(stdout_file.name)
        stderr_path = Path(stderr_file.name)

        try:
            creationflags = 0
            start_new_session = False

            if os.name == "nt":
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                start_new_session = True

            creation_task = asyncio.create_task(
                asyncio.create_subprocess_shell(
                    command,
                    stdout=stdout_file,
                    stderr=stderr_file,
                    creationflags=creationflags,
                    start_new_session=start_new_session
                    )
            )
            process = await asyncio.shield(creation_task)

        except asyncio.CancelledError:
            try:
                process = await creation_task
                await self.process_terminator.terminate(process)
            finally:
                stdout_file.close()
                stderr_file.close()
                stdout_path.unlink(missing_ok=True)
                stderr_path.unlink(missing_ok=True)
            raise

        except Exception:
            stdout_file.close()
            stderr_file.close()
            stdout_path.unlink(missing_ok=True)
            stderr_path.unlink(missing_ok=True)
            raise
        else:
            stdout_file.close()
            stderr_file.close()

        self.process_manager.add(
            ManagedProcess(
                process=process,
                stdout_path=stdout_path,
                stderr_path=stderr_path,
            )
        )

        return f"Started process: {process.pid}"