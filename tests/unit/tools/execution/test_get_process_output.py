from pathlib import Path
from unittest.mock import MagicMock

import pytest

from coding_agent.tools.execution.get_process_output import (
    GetProcessOutputTool,
)
from coding_agent.tools.execution.process_manager import (
    ManagedProcess,
    ProcessManager,
)


def test_get_process_output_returns_stdout_and_stderr(tmp_path):
    manager = MagicMock(spec=ProcessManager)
    process = MagicMock()

    stdout_path = tmp_path / "stdout.txt"
    stderr_path = tmp_path / "stderr.txt"

    stdout_path.write_text("hello\n", encoding="utf-8")
    stderr_path.write_text("error", encoding="utf-8")

    managed = ManagedProcess(
        process=process,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
    )

    manager.get.return_value = managed

    tool = GetProcessOutputTool(manager)

    result = tool.execute(1234)

    process.wait.assert_called_once_with()

    assert result == (
        "STDOUT:\n"
        "hello\n"
        "STDERR:\n"
        "error"
    )

    manager.get.assert_called_once_with(1234)
    manager.remove.assert_called_once_with(1234)

    assert not stdout_path.exists()
    assert not stderr_path.exists()


def test_get_process_output_cleans_up_when_read_fails(tmp_path):
    manager = MagicMock(spec=ProcessManager)
    process = MagicMock()

    stdout_path = tmp_path / "stdout.txt"
    stderr_path = tmp_path / "stderr.txt"

    stdout_path.write_text("hello", encoding="utf-8")
    stderr_path.write_text("error", encoding="utf-8")

    managed = ManagedProcess(
        process=process,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
    )

    manager.get.return_value = managed

    tool = GetProcessOutputTool(manager)

    stdout_path.unlink()

    with pytest.raises(FileNotFoundError):
        tool.execute(1234)

    manager.remove.assert_called_once_with(1234)

    assert not stderr_path.exists()


def test_get_process_output_raises_for_unknown_process():
    manager = MagicMock(spec=ProcessManager)
    manager.get.side_effect = KeyError(9999)

    tool = GetProcessOutputTool(manager)

    with pytest.raises(KeyError):
        tool.execute(9999)
