from pathlib import Path

import pytest

from harness.security.workspace_path_guard import WorkspacePathGuard
from harness.tools.output_budget import OutputBudget


@pytest.fixture
def workspace_boundary(tmp_path: Path):
    return WorkspacePathGuard(tmp_path)

@pytest.fixture
def output_budget():
    return OutputBudget(max_chars=20000)