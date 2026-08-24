import os
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from harness.tools.execution.kill_process import KillProcessTool
from harness.tools.execution.process_manager import (
    ManagedProcess,
    ProcessManager,
)


def make_managed_process(tmp_path):
    process = MagicMock()
    process.pid = 1234
    process.poll.return_value = None

    return ManagedProcess(
        process=process,
        stdout_path=tmp_path / "stdout.txt",
        stderr_path=tmp_path / "stderr.txt",
    )


@pytest.mark.skipif(os.name != "nt", reason="Windows-specific process-tree behavior")
def test_kill_process_terminates_process_tree(tmp_path):
    manager = MagicMock(spec=ProcessManager)
    managed = make_managed_process(tmp_path)

    manager.get.return_value = managed

    tool = KillProcessTool(manager)

    with patch(
        "harness.tools.execution.kill_process.subprocess.run"
    ) as run:
        result = tool.execute(1234)

    run.assert_called_once_with(
        [
            "taskkill",
            "/PID",
            "1234",
            "/T",
            "/F",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    managed.process.wait.assert_called_once_with(timeout=5)

    assert result == "Successfully terminated process: 1234"

    manager.remove.assert_called_once_with(1234)


def test_kill_process_waits_after_termination(tmp_path):
    manager = MagicMock(spec=ProcessManager)
    managed = make_managed_process(tmp_path)

    manager.get.return_value = managed

    tool = KillProcessTool(manager)

    if os.name == "nt":
        with patch(
            "harness.tools.execution.kill_process.subprocess.run"
        ):
            tool.execute(1234)
    else:
        with patch(
            "harness.tools.execution.kill_process.os.killpg"
        ), patch(
            "harness.tools.execution.kill_process.os.getpgid",
            return_value=1234,
        ):
            tool.execute(1234)

    managed.process.wait.assert_called_once_with(timeout=5)
    manager.remove.assert_called_once_with(1234)


def test_kill_process_falls_back_to_kill(tmp_path):
    manager = MagicMock(spec=ProcessManager)
    managed = make_managed_process(tmp_path)

    manager.get.return_value = managed

    managed.process.wait.side_effect = [
        subprocess.TimeoutExpired("process", 5),
        None,
    ]

    tool = KillProcessTool(manager)

    if os.name == "nt":
        with patch(
            "harness.tools.execution.kill_process.subprocess.run"
        ):
            tool.execute(1234)
    else:
        with patch(
            "harness.tools.execution.kill_process.os.killpg"
        ), patch(
            "harness.tools.execution.kill_process.os.getpgid",
            return_value=1234,
        ):
            tool.execute(1234)

    managed.process.kill.assert_called_once_with()
    assert managed.process.wait.call_count == 2
    manager.remove.assert_called_once_with(1234)


def test_kill_process_raises_for_unknown_process():
    manager = MagicMock(spec=ProcessManager)
    manager.get.side_effect = KeyError(9999)

    tool = KillProcessTool(manager)

    with pytest.raises(KeyError):
        tool.execute(9999)
