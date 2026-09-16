import asyncio
import os
import signal
import subprocess

from harness.tools.async_base_tool import AsyncBaseTool
from .process_manager import ProcessManager


class KillProcessTool(AsyncBaseTool):
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

    async def execute(self, process_id: int) -> str:
        managed = self.process_manager.get(process_id)
        process = managed.process

        try:
            if process.returncode is None:
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

                try:
                    await asyncio.wait_for(process.wait(), timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    await process.wait()

            return f"Successfully terminated process: {process_id}"
        finally:
            managed.stdout_path.unlink(missing_ok=True)
            managed.stderr_path.unlink(missing_ok=True)
            self.process_manager.remove(process_id)
