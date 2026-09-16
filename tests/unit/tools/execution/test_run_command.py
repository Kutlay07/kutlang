import asyncio
import os
from pathlib import Path
import subprocess
import sys
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from harness.tools.execution.run_command import RunCommandTool


@pytest.mark.asyncio
async def test_run_command_executes_command():
    tool = RunCommandTool()

    result = await tool.execute(
        command="python -c \"print('hello')\""
    )

    assert result == (
        "Exit code: 0\n"
        "STDOUT:\n"
        "hello\n"
        "STDERR:\n"
    )


@pytest.mark.asyncio
async def test_run_command_returns_stderr():
    tool = RunCommandTool()

    result = await tool.execute(
        command="python -c \"import sys; sys.stderr.write('error')\""
    )

    assert result == (
        "Exit code: 0\n"
        "STDOUT:\n"
        "STDERR:\n"
        "error"
    )


@pytest.mark.asyncio
async def test_run_command_returns_exit_code():
    tool = RunCommandTool()

    result = await tool.execute(
        command="python -c \"raise SystemExit(3)\""
    )

    assert "Exit code: 3" in result


@pytest.mark.asyncio
async def test_run_command_handles_timeout():
    tool = RunCommandTool()

    result = await tool.execute(
        command="python -c \"import time; time.sleep(2)\"",
        timeout=1,
    )

    assert result == "Command timed out after 1 seconds"


@pytest.mark.asyncio
async def test_run_command_handles_execution_error():
    tool = RunCommandTool()

    result = await tool.execute(
        command="this-command-does-not-exist-12345"
    )

    assert "Exit code:" in result
    assert "STDERR:" in result


@pytest.mark.asyncio
async def test_run_command_times_out():
    tool = RunCommandTool()

    result = await tool.execute(
        command="python -c \"import time; time.sleep(10)\"",
        timeout=1,
    )

    assert result == "Command timed out after 1 seconds"


@pytest.mark.asyncio
async def test_run_command_accepts_timeout():
    tool = RunCommandTool()

    result = await tool.execute(
        command="python -c \"print('hello')\"",
        timeout=5,
    )

    assert result == (
        "Exit code: 0\n"
        "STDOUT:\n"
        "hello\n"
        "STDERR:\n"
    )


@pytest.mark.asyncio
async def test_run_command_handles_nonzero_exit_code():
    tool = RunCommandTool()

    result = await tool.execute(
        command="python -c \"raise SystemExit(42)\""
    )

    assert "Exit code: 42" in result


@pytest.mark.asyncio
async def test_run_command_combines_stdout_and_stderr():
    tool = RunCommandTool()

    result = await tool.execute(
        command=(
            "python -c "
            "\"import sys; print('out'); sys.stderr.write('err')\""
        )
    )

    assert result == (
        "Exit code: 0\n"
        "STDOUT:\n"
        "out\n"
        "STDERR:\n"
        "err"
    )


@pytest.mark.asyncio
async def test_run_command_uses_process_group_on_windows():
    process = MagicMock()
    process.communicate = AsyncMock(
        return_value=(b"hello\n", b"")
    )
    process.returncode = 0
    process.pid = 1234

    with patch(
        "harness.tools.execution.run_command.asyncio.create_subprocess_shell",
        return_value=process,
    ) as create_subprocess_shell:
        tool = RunCommandTool()

        result = await tool.execute(
            "python -c \"print('hello')\""
        )

    if os.name == "nt":
        create_subprocess_shell.assert_called_once_with(
            "python -c \"print('hello')\"",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            start_new_session=False,
        )

    assert result == (
        "Exit code: 0\n"
        "STDOUT:\n"
        "hello\n"
        "STDERR:\n"
    )


@pytest.mark.asyncio
async def test_run_command_kills_process_tree_on_timeout():
    process = MagicMock()
    process.communicate = AsyncMock(
        side_effect=asyncio.TimeoutError
    )
    process.returncode = None
    process.pid = 1234

    with patch(
        "harness.tools.execution.run_command.asyncio.create_subprocess_shell",
        return_value=process,
    ), patch.object(
        RunCommandTool,
        "_terminate_process_group",
        new_callable=AsyncMock,
    ) as terminate_process_group:
        tool = RunCommandTool()

        result = await tool.execute(
            "python -c \"import time; time.sleep(10)\"",
            timeout=1,
        )

    terminate_process_group.assert_awaited_once_with(process)

    assert result == "Command timed out after 1 seconds"


@pytest.mark.asyncio
async def test_terminate_process_group_terminates_real_process():
    kwargs = {}

    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True

    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-c",
        "import time; time.sleep(10)",
        **kwargs,
    )

    try:
        await RunCommandTool._terminate_process_group(process)

        assert process.returncode is not None
    finally:
        if process.returncode is None:
            process.kill()

        await process.wait()


@pytest.mark.asyncio
async def test_process_tree_termination(tmp_path: Path):
    marker_path = tmp_path / "marker.txt"
    started_path = tmp_path / "started.txt"

    child_code = f"""
import time
from pathlib import Path

started = Path({repr(str(started_path))})
marker = Path({repr(str(marker_path))})

started.write_text("started")
time.sleep(3)
marker.write_text("alive")
"""

    parent_code = f"""
import time
import sys
import subprocess

subprocess.Popen([
    sys.executable,
    "-c",
    {repr(child_code)},
])

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

        await RunCommandTool._terminate_process_group(parent_process)

        await asyncio.sleep(4)

        assert not marker_path.exists(), (
            "Child process survived termination"
        )
    finally:
        if parent_process.returncode is None:
            parent_process.kill()

        await parent_process.wait()


@pytest.mark.asyncio
async def test_timeout_with_cleanup_failure():
    tool = RunCommandTool()

    process = MagicMock()
    process.communicate = AsyncMock(
        side_effect=asyncio.TimeoutError
    )
    process.returncode = None
    process.pid = 1234

    with patch(
        "harness.tools.execution.run_command.asyncio.create_subprocess_shell",
        return_value=process,
    ), patch.object(
        RunCommandTool,
        "_terminate_process_group",
        new_callable=AsyncMock,
        side_effect=RuntimeError("cleanup failed"),
    ):
        result = await tool.execute(
            "test-command",
            timeout=1,
        )

    assert "Command timed out after 1 seconds" in result
    assert "cleanup failed" in result


@pytest.mark.asyncio
async def test_cancellation():
    process = MagicMock()
    process.communicate = AsyncMock(
        side_effect=asyncio.CancelledError
    )

    process.returncode = None
    process.pid = 1234

    with patch(
        "harness.tools.execution.run_command.asyncio.create_subprocess_shell",
        return_value=process,
    ), patch.object(
        RunCommandTool,
        "_terminate_process_group",
        new_callable=AsyncMock,
    ) as terminate_process_group:

        tool = RunCommandTool()

        with pytest.raises(asyncio.CancelledError):
            await tool.execute(
                "python -c \"import time; time.sleep(10)\""
            )

    terminate_process_group.assert_awaited_once_with(process)

@pytest.mark.asyncio
async def test_real_cancellation():
    tool = RunCommandTool()

    task = asyncio.create_task(
        tool.execute(
            "python -c \"import time; time.sleep(10)\""
        )
    )

    await asyncio.sleep(0.5)

    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_real_cancellation_cleans_up_process_tree(tmp_path: Path):
    started_path = tmp_path / "started.txt"
    marker_path = tmp_path / "alive.txt"

    child_code = f"""
import time
from pathlib import Path

started = Path({repr(str(started_path))})
marker = Path({repr(str(marker_path))})

started.write_text("started")
time.sleep(3)
marker.write_text("alive")
"""
    child_script = tmp_path / "child.py"
    child_script.write_text(child_code, encoding="utf-8")

    command = subprocess.list2cmdline([
        sys.executable,
        str(child_script),
    ])


    tool = RunCommandTool()

    task = asyncio.create_task(
        tool.execute(command)
    )

    for _ in range(20):
        if started_path.exists():
            break

        await asyncio.sleep(0.1)

    assert started_path.exists()

    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    await asyncio.sleep(4)

    assert not marker_path.exists()