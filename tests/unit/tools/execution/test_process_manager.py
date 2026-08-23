from unittest.mock import MagicMock, patch

import pytest

from coding_agent.tools.execution.process_manager import ProcessManager
from coding_agent.tools.execution.run_background_command import RunBackgroundCommandTool


def test_process_manager_stores_process():
    manager = ProcessManager()
    process = MagicMock()
    process.pid = 1234

    manager.add(process)

    assert manager.get(1234) is process


def test_process_manager_raises_for_unknown_process():
    manager = ProcessManager()

    with pytest.raises(KeyError):
        manager.get(9999)


def test_process_manager_removes_process():
    manager = ProcessManager()
    process = MagicMock()
    process.pid = 1234

    manager.add(process)
    manager.remove(1234)

    with pytest.raises(KeyError):
        manager.get(1234)


def test_process_manager_shares_process_between_tools():
    manager = ProcessManager()

    process = MagicMock()
    process.pid = 1234

    manager.add(process)

    assert manager.get(1234) is process

    manager.remove(1234)

    with pytest.raises(KeyError):
        manager.get(1234)


def test_background_process_can_be_retrieved_by_shared_manager():
    manager = ProcessManager()

    process = MagicMock()
    process.pid = 1234

    with patch(
        "coding_agent.tools.execution.run_background_command.subprocess.Popen",
        return_value=process,
    ):
        run_tool = RunBackgroundCommandTool(manager)

        result = run_tool.execute("python server.py")

    process_id = int(result.removeprefix("Started process: "))

    assert manager.get(process_id) is process