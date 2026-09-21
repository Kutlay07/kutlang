from pathlib import Path

from harness.security.search_visibility import SearchVisibility
from harness.security.workspace_boundary import (
    WorkspaceBoundary,
    WorkspaceBoundaryViolation,
)
from harness.tools.output_budget import OutputBudget

from ..sync_base_tool import SyncBaseTool


class GlobTool(SyncBaseTool):

    def __init__(
        self, 
        workspace_boundary: WorkspaceBoundary,
        search_visibility: SearchVisibility,
        output_budget: OutputBudget,
        ):
        self.workspace_boundary = workspace_boundary
        self.search_visibility = search_visibility
        self.output_budget = output_budget

    @property
    def name(self) -> str:
        return "glob"

    @property
    def description(self) -> str:
        return "Fast file pattern matching relative to the workspace root."

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Pattern to search for, such as '**/*.py' or 'src/*.ts'.",
                },
            },
            "required": ["pattern"],
            "additionalProperties": False,
        }

    def execute(self, pattern: str) -> str:
        pattern_path = Path(pattern)

        if pattern_path.is_absolute() or ".." in pattern_path.parts:
            raise WorkspaceBoundaryViolation(
                f"Glob pattern is outside the workspace boundary: {pattern}"
            )

        workspace_root = self.workspace_boundary.root
        paths = list(workspace_root.glob(pattern))

        results = [
            str(path.relative_to(workspace_root))
            for path in paths
            if self.search_visibility.is_visible(path)
        ]

        lines = self.output_budget.enforce(sorted(results))
        return "\n".join(lines)