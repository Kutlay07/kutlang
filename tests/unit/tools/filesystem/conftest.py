from pathlib import Path

import pytest

from harness.security.workspace_path_guard import WorkspacePathGuard


@pytest.fixture
def workspace_boundary(tmp_path: Path):
    return WorkspacePathGuard(tmp_path)