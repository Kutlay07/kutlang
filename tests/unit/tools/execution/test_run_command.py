import subprocess
from unittest.mock import MagicMock, patch

import pytest

from harness.tools.execution.run_command import RunCommandTool


pytestmark = pytest.mark.slow


def test_run_command_executes_command():
    tool = RunCommandTool()

    result = tool.execute(
        command="python -c \"print('hello')\""
    )

    assert result == (
        "Exit code: 0\n"
        "STDOUT:\n"
        "hello\n"
        "STDERR:\n"
    )


def test_run_command_returns_stderr():
    tool = RunCommandTool()

    result = tool.execute(
        command="python -c \"import sys; sys.stderr.write('error')\""
    )

    assert result == (
        "Exit code: 0\n"
        "STDOUT:\n"
        "STDERR:\n"
        "error"
    )


def test_run_command_returns_exit_code():
    tool = RunCommandTool()

    result = tool.execute(
        command="python -c \"raise SystemExit(3)\""
    )

    assert "Exit code: 3" in result


def test_run_command_handles_timeout():
    tool = RunCommandTool()

    result = tool.execute(
        command="python -c \"import time; time.sleep(2)\"",
        timeout=1,
    )

    assert result == "Command timed out after 1 seconds"


def test_run_command_handles_execution_error():
    tool = RunCommandTool()

    result = tool.execute(
        command="this-command-does-not-exist-12345"
    )

    assert "Exit code:" in result
    assert "STDERR:" in result


def test_run_command_times_out():
    tool = RunCommandTool()

    result = tool.execute(
        command="python -c \"import time; time.sleep(10)\"",
        timeout=1,
    )

    assert result == "Command timed out after 1 seconds"


def test_run_command_accepts_timeout():
    tool = RunCommandTool()

    result = tool.execute(
        command="python -c \"print('hello')\"",
        timeout=5,
    )

    assert result == (
        "Exit code: 0\n"
        "STDOUT:\n"
        "hello\n"
        "STDERR:\n"
    )


def test_run_command_handles_nonzero_exit_code():
    tool = RunCommandTool()

    result = tool.execute(
        command="python -c \"raise SystemExit(42)\""
    )

    assert "Exit code: 42" in result


def test_run_command_combines_stdout_and_stderr():
    tool = RunCommandTool()

    result = tool.execute(
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


def test_run_command_uses_process_group_on_windows():
    process = MagicMock()
    process.communicate.return_value = ("hello\n", "")
    process.returncode = 0

    with patch(
        "harness.tools.execution.run_command.subprocess.Popen",
        return_value=process,
    ) as popen:
        tool = RunCommandTool()

        result = tool.execute("python -c \"print('hello')\"")

    if __import__("os").name == "nt":
        popen.assert_called_once_with(
            "python -c \"print('hello')\"",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )

    assert result == (
        "Exit code: 0\n"
        "STDOUT:\n"
        "hello\n"
        "STDERR:\n"
    )


def test_run_command_kills_process_tree_on_timeout():
    process = MagicMock()
    process.communicate.side_effect = [
        subprocess.TimeoutExpired("python", 1),
        ("", ""),
    ]
    process.poll.return_value = None

    with patch(
        "harness.tools.execution.run_command.subprocess.Popen",
        return_value=process,
    ), patch(
        "harness.tools.execution.run_command.subprocess.run",
    ) as run:
        tool = RunCommandTool()

        result = tool.execute("python -c \"import time; time.sleep(10)\"", 1)

    if __import__("os").name == "nt":
        run.assert_called_once_with(
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

    process.communicate.assert_any_call(timeout=1)
    process.communicate.assert_any_call()

    assert result == "Command timed out after 1 seconds"
