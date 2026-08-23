from unittest.mock import MagicMock, patch
import subprocess

from coding_agent.tools.execution.process_manager import ProcessManager
from coding_agent.tools.execution.run_background_command import (
    RunBackgroundCommandTool,
)


def test_run_background_command_starts_process():
    manager = MagicMock(spec=ProcessManager)
    process = MagicMock()
    process.pid = 1234

    with patch(
        "coding_agent.tools.execution.run_background_command.subprocess.Popen",
        return_value=process,
    ):
        tool = RunBackgroundCommandTool(manager)

        result = tool.execute("python server.py")

    assert result == "Started process: 1234"
    manager.add.assert_called_once_with(process)


def test_run_background_command_uses_background_process():
    manager = MagicMock(spec=ProcessManager)
    process = MagicMock()
    process.pid = 1234

    with patch(
        "coding_agent.tools.execution.run_background_command.subprocess.Popen",
        return_value=process,
    ) as popen:
        tool = RunBackgroundCommandTool(manager)

        tool.execute("python server.py")

    popen.assert_called_once_with(
        "python server.py",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )