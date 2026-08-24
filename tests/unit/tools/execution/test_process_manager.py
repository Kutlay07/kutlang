from pathlib import Path
from unittest.mock import MagicMock

from harness.tools.execution.process_manager import (
    ManagedProcess,
    ProcessManager,
)


def make_managed_process(pid: int = 1234) -> ManagedProcess:
    process = MagicMock()
    process.pid = pid

    return ManagedProcess(
        process=process,
        stdout_path=Path("stdout.txt"),
        stderr_path=Path("stderr.txt"),
    )


def test_process_manager_stores_process():
    manager = ProcessManager()
    managed = make_managed_process()

    manager.add(managed)

    assert manager.get(1234) is managed


def test_process_manager_raises_for_unknown_process():
    manager = ProcessManager()

    try:
        manager.get(9999)
    except KeyError:
        pass
    else:
        raise AssertionError("Expected KeyError")


def test_process_manager_removes_process():
    manager = ProcessManager()
    managed = make_managed_process()

    manager.add(managed)

    removed = manager.remove(1234)

    assert removed is managed

    try:
        manager.get(1234)
    except KeyError:
        pass
    else:
        raise AssertionError("Expected KeyError")


def test_process_manager_shares_process_between_tools():
    manager = ProcessManager()
    managed = make_managed_process()

    manager.add(managed)

    assert manager.get(1234) is managed


def test_background_process_can_be_retrieved_by_shared_manager():
    manager = ProcessManager()
    managed = make_managed_process(5678)

    manager.add(managed)

    retrieved = manager.get(5678)

    assert retrieved.process is managed.process
    assert retrieved.stdout_path == Path("stdout.txt")
    assert retrieved.stderr_path == Path("stderr.txt")
