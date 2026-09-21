import json
import subprocess
from pathlib import Path

from harness.security.search_visibility import SearchVisibility
from harness.security.workspace_boundary import (
    WorkspaceBoundary,
    WorkspaceBoundaryViolation,
)
from harness.tools.output_budget import OutputBudget

from ..sync_base_tool import SyncBaseTool


class GrepTool(SyncBaseTool):
    
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
        return "grep"

    @property
    def description(self) -> str:
        return "Search for specific text content or patterns inside files within the workspace."

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The text string or regex pattern to search for inside the files (e.g., 'def execute', 'TODO').",
                },
                "pattern": {
                    "type": "string",
                    "description": "File pattern to restrict the search ,relative to the workspace root. Defaults to '**/*' to search all files."
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        }


    def execute(self, query: str, pattern: str = "**/*") -> str:
        if Path(pattern).is_absolute() or ".." in Path(pattern).parts:
            raise WorkspaceBoundaryViolation(f"Outside boundary: {pattern}")

        workspace_root = self.workspace_boundary.root

        command = [
            "rg",
            "--json",
            "-g", pattern,
            "-e",
            query,
        ]

        try:
            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                cwd=workspace_root,
            )
            
            if process.returncode == 1:
                return ""
            if process.returncode == 2:
                raise RuntimeError(process.stderr.strip())
            if not process.stdout:
                return ""

            final_lines = []
            for line in process.stdout.splitlines():
                event = json.loads(line)

                if event["type"] != "match":
                    continue

                data = event["data"]

                path = Path(data["path"]["text"])

                if not self.search_visibility.is_visible(path):
                    continue

                line_number = data["line_number"]
                line = data["lines"]["text"].rstrip("\r\n")
                

                final_lines.append(f"{path}:{line_number}:{line}")

            lines = self.output_budget.enforce(final_lines)
            return "\n".join(lines)

        except FileNotFoundError:
            raise RuntimeError("ripgrep (rg) binary is not installed on the system.")