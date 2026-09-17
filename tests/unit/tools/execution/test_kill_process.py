import asyncio
import os
from unittest.mock import MagicMock

import pytest

from harness.tools.execution.kill_process import KillProcessTool
from harness.tools.execution.process_manager import (
    ManagedProcess,
    ProcessManager,
)
from harness.tools.execution.process_terminator import ProcessTerminator


@pytest.fixture
def process_terminator():
    return MagicMock(spec=ProcessTerminator)


def make_managed_process(tmp_path):
    process = MagicMock()
    process.pid = 1234
    process.returncode = None

    return ManagedProcess(
        process=process,
        stdout_path=tmp_path / "stdout.txt",
        stderr_path=tmp_path / "stderr.txt",
    )


@pytest.mark.asyncio
async def test_kill_process_terminates_process(
    tmp_path,
    process_terminator,
):
    manager = MagicMock(spec=ProcessManager)
    managed = make_managed_process(tmp_path)

    manager.get.return_value = managed

    tool = KillProcessTool(manager, process_terminator)

    result = await tool.execute(1234)

    process_terminator.terminate.assert_called_once_with(
        managed.process
    )

    assert result == "Successfully terminated process: 1234"
    manager.remove.assert_called_once_with(1234)


@pytest.mark.asyncio
async def test_kill_process_waits_after_termination(
    tmp_path,
    process_terminator,
):
    manager = MagicMock(spec=ProcessManager)
    managed = make_managed_process(tmp_path)

    manager.get.return_value = managed

    tool = KillProcessTool(manager, process_terminator)

    await tool.execute(1234)

    process_terminator.terminate.assert_called_once_with(
        managed.process
    )
    manager.remove.assert_called_once_with(1234)


@pytest.mark.asyncio
async def test_kill_process_raises_for_unknown_process(
    process_terminator,
):
    manager = MagicMock(spec=ProcessManager)
    manager.get.side_effect = KeyError(9999)

    tool = KillProcessTool(manager, process_terminator)

    with pytest.raises(KeyError):
        await tool.execute(9999)


@pytest.mark.asyncio
async def test_kill_process_preserves_process_on_cancellation(
    tmp_path,
    process_terminator,
):
    manager = MagicMock(spec=ProcessManager)
    managed = make_managed_process(tmp_path)

    manager.get.return_value = managed

    termination_started = asyncio.Event()
    allow_termination = asyncio.Event()

    async def fake_terminate(process):
        termination_started.set()
        await allow_termination.wait()

    process_terminator.terminate = fake_terminate

    tool = KillProcessTool(manager, process_terminator)

    task = asyncio.create_task(tool.execute(1234))

    await termination_started.wait()

    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    manager.remove.assert_not_called()