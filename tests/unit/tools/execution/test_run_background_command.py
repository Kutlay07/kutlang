import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from coding_agent.tools.execution.process_manager import (
    ManagedProcess,
    ProcessManager,
)
from coding_agent.tools.execution.run_background_command import (
    RunBackgroundCommandTool,
)


def test_run_background_command_starts_process(tmp_path):
    manager = MagicMock(spec=ProcessManager)
    process = MagicMock()
    process.pid = 1234

    stdout_file = MagicMock()
    stderr_file = MagicMock()

    with patch(
        "coding_agent.tools.execution.run_background_command.tempfile.NamedTemporaryFile",
        side_effect=[stdout_file, stderr_file],
    ), patch(
        "coding_agent.tools.execution.run_background_command.subprocess.Popen",
        return_value=process,
    ) as popen:
        stdout_file.name = str(tmp_path / "stdout.txt")
        stderr_file.name = str(tmp_path / "stderr.txt")

        tool = RunBackgroundCommandTool(manager)

        result = tool.execute("python server.py")

    assert result == "Started process: 1234"

    manager.add.assert_called_once()

    managed = manager.add.call_args.args[0]

    assert isinstance(managed, ManagedProcess)
    assert managed.process is process
    assert managed.stdout_path == Path(stdout_file.name)
    assert managed.stderr_path == Path(stderr_file.name)


def test_run_background_command_uses_process_group(tmp_path):
    manager = MagicMock(spec=ProcessManager)
    process = MagicMock()
    process.pid = 1234

    stdout_file = MagicMock()
    stderr_file = MagicMock()

    stdout_file.name = str(tmp_path / "stdout.txt")
    stderr_file.name = str(tmp_path / "stderr.txt")

    with patch(
        "coding_agent.tools.execution.run_background_command.tempfile.NamedTemporaryFile",
        side_effect=[stdout_file, stderr_file],
    ), patch(
        "coding_agent.tools.execution.run_background_command.subprocess.Popen",
        return_value=process,
    ) as popen:
        tool = RunBackgroundCommandTool(manager)

        tool.execute("python server.py")

    popen.assert_called_once_with(
        "python server.py",
        shell=True,
        stdout=stdout_file,
        stderr=stderr_file,
        text=True,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
    )
