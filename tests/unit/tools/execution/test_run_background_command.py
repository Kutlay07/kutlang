import asyncio
import subprocess
import pytest
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from harness.tools.execution.process_manager import (
    ManagedProcess,
    ProcessManager,
)
from harness.tools.execution.process_terminator import ProcessTerminator
from harness.tools.execution.run_background_command import (
    RunBackgroundCommandTool,
)


@pytest.mark.asyncio
async def test_run_background_command_starts_process(tmp_path):
    manager = MagicMock(spec=ProcessManager)
    process = MagicMock()
    process.pid = 1234

    stdout_file = MagicMock()
    stderr_file = MagicMock()

    with patch(
        "harness.tools.execution.run_background_command.tempfile.NamedTemporaryFile",
        side_effect=[stdout_file, stderr_file],
    ), patch(
        "harness.tools.execution.run_background_command.asyncio.create_subprocess_shell",
        new_callable=AsyncMock,
        return_value=process,
    ) as popen:
        stdout_file.name = str(tmp_path / "stdout.txt")
        stderr_file.name = str(tmp_path / "stderr.txt")

        terminator = MagicMock(spec=ProcessTerminator)
        tool = RunBackgroundCommandTool(
            manager,
            terminator,
        )

        result = await tool.execute("python server.py")

    assert result == "Started process: 1234"

    manager.add.assert_called_once()

    managed = manager.add.call_args.args[0]

    assert isinstance(managed, ManagedProcess)
    assert managed.process is process
    assert managed.stdout_path == Path(stdout_file.name)
    assert managed.stderr_path == Path(stderr_file.name)


@pytest.mark.asyncio
@pytest.mark.skipif(
    os.name != "nt",
    reason="Windows-specific process-tree behavior",
)
async def test_run_background_command_uses_process_group(tmp_path):
    manager = MagicMock(spec=ProcessManager)
    process = MagicMock()
    process.pid = 1234

    stdout_file = MagicMock()
    stderr_file = MagicMock()

    stdout_file.name = str(tmp_path / "stdout.txt")
    stderr_file.name = str(tmp_path / "stderr.txt")

    with patch(
        "harness.tools.execution.run_background_command.tempfile.NamedTemporaryFile",
        side_effect=[stdout_file, stderr_file],
    ), patch(
        "harness.tools.execution.run_background_command.asyncio.create_subprocess_shell",
        new_callable=AsyncMock,
        return_value=process,
    ) as popen:
        terminator = MagicMock(spec=ProcessTerminator)

        tool = RunBackgroundCommandTool(
            manager,
            terminator,
        )
        

        await tool.execute("python server.py")
    popen.assert_awaited_once_with(
        "python server.py",
        stdout=stdout_file,
        stderr=stderr_file,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        start_new_session=False,
    )


@pytest.mark.asyncio
async def test_run_background_command_cleans_up_temp_files_on_cancellation(
    tmp_path,
):
    manager = MagicMock(spec=ProcessManager)

    stdout_path = tmp_path / "stdout.txt"
    stderr_path = tmp_path / "stderr.txt"

    stdout_file = MagicMock()
    stderr_file = MagicMock()

    with patch(
        "harness.tools.execution.run_background_command.tempfile.NamedTemporaryFile",
        side_effect=[stdout_file, stderr_file],
    ), patch(
        "harness.tools.execution.run_background_command.asyncio.create_subprocess_shell",
        new_callable=AsyncMock,
        side_effect=asyncio.CancelledError,
    ), patch(
        "harness.tools.execution.run_background_command.Path.unlink",
    ) as unlink:
        terminator = MagicMock(spec=ProcessTerminator)

        tool = RunBackgroundCommandTool(
            manager,
            terminator,
        )

        with pytest.raises(asyncio.CancelledError):
            await tool.execute("python server.py")

    assert unlink.call_count == 2
    stdout_file.close.assert_called_once_with()
    stderr_file.close.assert_called_once_with()


@pytest.mark.asyncio
async def test_run_background_command_cleans_up_created_process_on_cancellation(
    tmp_path,
):
    manager = MagicMock(spec=ProcessManager)

    stdout_file = MagicMock()
    stderr_file = MagicMock()

    stdout_file.name = str(tmp_path / "stdout.txt")
    stderr_file.name = str(tmp_path / "stderr.txt")

    creation_started = asyncio.Event()
    allow_creation = asyncio.Event()

    process = MagicMock()
    process.pid = 1234

    async def fake_create_process(*args, **kwargs):
        creation_started.set()

        try:
            await allow_creation.wait()
        except asyncio.CancelledError:
            return process

        return process

    with patch(
        "harness.tools.execution.run_background_command.tempfile.NamedTemporaryFile",
        side_effect=[stdout_file, stderr_file],
    ), patch(
        "harness.tools.execution.run_background_command.asyncio.create_subprocess_shell",
        side_effect=fake_create_process,
    ):
        terminator = MagicMock(spec=ProcessTerminator)

        tool = RunBackgroundCommandTool(
            manager,
            terminator,
        )

        task = asyncio.create_task(
            tool.execute("python server.py")
        )

        await creation_started.wait()

        task.cancel()
        allow_creation.set()

        with pytest.raises(asyncio.CancelledError):
            await task

        manager.add.assert_not_called()
        
        terminator.terminate.assert_awaited_once_with(process)