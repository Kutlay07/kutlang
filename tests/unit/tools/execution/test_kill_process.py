from unittest.mock import MagicMock

import pytest

from coding_agent.tools.execution.kill_process import KillProcessTool
from coding_agent.tools.execution.process_manager import ProcessManager


def test_kill_process_terminates_process():
    manager = MagicMock(spec=ProcessManager)
    process = MagicMock()

    manager.get.return_value = process

    tool = KillProcessTool(manager)

    result = tool.execute(1234)

    process.terminate.assert_called_once_with()
    manager.get.assert_called_once_with(1234)
    manager.remove.assert_called_once_with(1234)

    assert result == "Successfully terminated process: 1234"


def test_kill_process_raises_for_unknown_process():
    manager = MagicMock(spec=ProcessManager)
    manager.get.side_effect = KeyError(9999)

    tool = KillProcessTool(manager)

    with pytest.raises(KeyError):
        tool.execute(9999)


def test_kill_process_removes_process_after_termination():
    manager = MagicMock(spec=ProcessManager)
    process = MagicMock()

    manager.get.return_value = process

    tool = KillProcessTool(manager)

    tool.execute(1234)

    process.terminate.assert_called_once()
    manager.remove.assert_called_once_with(1234)