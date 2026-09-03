import pytest

from harness.security.workspace_boundary import WorkspaceBoundaryViolation
from harness.security.workspace_path_guard import WorkspacePathGuard


def test_allows_path_inside_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    source = workspace / "src"
    source.mkdir()

    file = source / "main.py"
    file.touch()

    boundary = WorkspacePathGuard(workspace)
    result = boundary.validate("src/main.py")

    assert result == file.resolve()


def test_refuse_exiting_workspace_via_traversal(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    secret = tmp_path / "secret.txt"
    secret.touch()

    boundary = WorkspacePathGuard(workspace)

    with pytest.raises(WorkspaceBoundaryViolation):
        boundary.validate("../secret.txt")


def test_refuse_absolute_path_if_its_out_of_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    secret = tmp_path / "secret.txt"
    secret.touch()

    boundary = WorkspacePathGuard(workspace)

    with pytest.raises(WorkspaceBoundaryViolation):
        boundary.validate(str(secret))


def test_refuse_escaping_out_of_workspace_via_symlink(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    outside = tmp_path / "outside"
    outside.mkdir()

    secret = outside / "secret.txt"
    secret.touch()

    link = workspace / "link"
    link.symlink_to(outside, target_is_directory=True)

    boundary = WorkspacePathGuard(workspace)

    with pytest.raises(WorkspaceBoundaryViolation):
        boundary.validate("link/secret.txt")