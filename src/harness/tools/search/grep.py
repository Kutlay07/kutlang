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


MAX_LINE_CHARS = 250


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
                    "description": "File pattern to restrict the search, relative to the workspace root. Defaults to '**/*' to search all files.",
                },
                "before": {
                    "type": "integer",
                    "description": "The number of lines of context to include BEFORE each match.",
                    "minimum": 0,
                },
                "after": {
                    "type": "integer",
                    "description": "The number of lines of context to include AFTER each match.",
                    "minimum": 0,
                },
                "max_results": {
                    "type": "integer",
                    "description": "The number of matches the tool will return.",
                    "minimum": 0,
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        }

    def execute(
        self,
        query: str,
        pattern: str = "**/*",
        before: int = 0,
        after: int = 0,
        max_results: int | None = None,
    ) -> str:

        if before < 0:
            raise ValueError("before must be >= 0")

        if after < 0:
            raise ValueError("after must be >= 0")

        if max_results is not None and max_results < 0:
            raise ValueError("max_results must be >= 0")

        if max_results == 0:
            return ""

        pattern_path = Path(pattern)

        if pattern_path.is_absolute() or ".." in pattern_path.parts:
            raise WorkspaceBoundaryViolation(
                f"Outside boundary: {pattern}"
            )

        workspace_root = self.workspace_boundary.root

        command = [
            "rg",
            "--json",
            "-B", str(before),
            "-A", str(after),
            "-g", pattern,
            "-e", query,
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
            
            events = [
                json.loads(line)
                for line in process.stdout.splitlines()
            ]

            selected_matches = []

            for event in events:
                if event["type"] != "match":
                    continue

                selected_matches.append(event)

                if (
                    max_results is not None
                    and len(selected_matches) >= max_results
                ):
                    break

            selected_match_positions = {
                (
                    event["data"]["path"]["text"],
                    event["data"]["line_number"],
                )
                for event in selected_matches
            }

            selected_ranges = {}

            for event in selected_matches:
                data = event["data"]
                path = data["path"]["text"]
                line_number = data["line_number"]

                start = max(1, line_number - before)
                end = line_number + after

                selected_ranges.setdefault(path, []).append((start, end))

            final_lines = []

            for event in events:
                if event["type"] not in {"match", "context"}:
                    continue

                data = event["data"]
                path = Path(data["path"]["text"])

                if not self.search_visibility.is_visible(path):
                    continue

                line_number = data["line_number"]
                path_key = data["path"]["text"]

                if event["type"] == "match":
                    if (path_key, line_number) not in selected_match_positions:
                        continue
                else:
                    ranges = selected_ranges.get(path_key, [])

                    if not any(
                        start <= line_number <= end
                        for start, end in ranges
                    ):
                        continue

                line = data["lines"]["text"].rstrip("\r\n")

                if len(line) > MAX_LINE_CHARS:
                    line = line[:MAX_LINE_CHARS] + " [line truncated]"

                final_lines.append(
                    f"{path}:{line_number}:{line}"
                )

            lines = self.output_budget.enforce(final_lines)
            return "\n".join(lines)

        except FileNotFoundError:
            raise RuntimeError(
                "ripgrep (rg) binary is not installed on the system"
            )