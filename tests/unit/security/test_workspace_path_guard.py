from pathlib import Path
import pytest

from harness.security.workspace_path_guard import (
    WorkspacePathGuard,
    WorkspaceBoundaryViolation,
)


def test_workspace_path_guard_allows_path_inside_workspace(tmp_path):
    guard = WorkspacePathGuard(tmp_path)

    file_path = tmp_path / "src" / "main.py"
    file_path.parent.mkdir()
    file_path.write_text("hello", encoding="utf-8")

    result = guard.validate("src/main.py")

    assert result == file_path.resolve()


def test_workspace_path_guard_rejects_path_outside_workspace(tmp_path):
    guard = WorkspacePathGuard(tmp_path)

    outside_path = tmp_path.parent / "outside.txt"

    with pytest.raises(WorkspaceBoundaryViolation):
        guard.validate(str(outside_path))


def test_workspace_path_guard_rejects_path_traversal(tmp_path):
    guard = WorkspacePathGuard(tmp_path)

    with pytest.raises(WorkspaceBoundaryViolation):
        guard.validate("../outside.txt")