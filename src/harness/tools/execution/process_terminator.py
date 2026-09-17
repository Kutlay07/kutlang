import asyncio
import subprocess
import os
import signal


class ProcessTerminator:
    async def terminate(
        self,
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