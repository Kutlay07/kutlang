from unittest.mock import MagicMock

import pytest

from coding_agent.tools.execution.get_process_output import (
    GetProcessOutputTool,
)
from coding_agent.tools.execution.process_manager import ProcessManager


def test_get_process_output_returns_stdout_and_stderr():
    manager = MagicMock(spec=ProcessManager)
    process = MagicMock()

    process.communicate.return_value = (
        "hello\n",
        "error",
    )

    manager.get.return_value = process

    tool = GetProcessOutputTool(manager)

    result = tool.execute(1234)

    assert result == (
        "STDOUT:\n"
        "hello\n"
        "STDERR:\n"
        "error"
    )

    manager.get.assert_called_once_with(1234)
    manager.remove.assert_called_once_with(1234)


def test_get_process_output_raises_for_unknown_process():
    manager = MagicMock(spec=ProcessManager)
    manager.get.side_effect = KeyError(9999)

    tool = GetProcessOutputTool(manager)

    with pytest.raises(KeyError):
        tool.execute(9999)