"""
from coding_agent.tools.execution.run_command import RunCommandTool


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
"""