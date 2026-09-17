import asyncio
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import MagicMock

import pytest

from harness.tools.execution.process_terminator import ProcessTerminator


@pytest.mark.asyncio
async def test_terminate_does_nothing_for_finished_process():
    process = MagicMock()
    process.returncode = 0
    
    terminator = ProcessTerminator()
    
    await terminator.terminate(process)
    
    process.wait.assert_not_called()


@pytest.mark.asyncio
async def test_terminate_stops_running_process():
    creationflags = 0
    start_new_session = False

    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        start_new_session = True

    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-c",
        "import time; time.sleep(100)",
        creationflags=creationflags,
        start_new_session=start_new_session,
    )

    terminator = ProcessTerminator()

    try:
        await terminator.terminate(process)
        assert process.returncode is not None
    finally:
        if process.returncode is None:
            process.kill()
            
        await process.wait()


@pytest.mark.asyncio
async def test_termination_kills_process_group(tmp_path: Path):
    started_path = tmp_path / "started.txt"
    child_pid_path = tmp_path / "child_pid.txt"

    child_code = f"""
import os
import time
from pathlib import Path

Path({repr(str(started_path))}).write_text("started")
time.sleep(10)
"""

    parent_code = f"""
import sys
import subprocess
import time
from pathlib import Path

child = subprocess.Popen([
    sys.executable,
    "-c",
    {repr(child_code)},
])

Path({repr(str(child_pid_path))}).write_text(str(child.pid))

time.sleep(10)
"""

    kwargs = {}

    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True

    parent_process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-c",
        parent_code,
        **kwargs,
    )

    try:
        await asyncio.sleep(0.5)

        assert started_path.exists(), "child process never started"
        assert child_pid_path.exists(), "child PID was not written"

        child_pid = int(child_pid_path.read_text())

        await ProcessTerminator().terminate(parent_process)

        await asyncio.sleep(1)

        assert parent_process.returncode is not None

        if os.name != "nt":
            with pytest.raises(ProcessLookupError):
                os.kill(child_pid, 0)

    finally:
        if parent_process.returncode is None:
            parent_process.kill()

        await parent_process.wait()