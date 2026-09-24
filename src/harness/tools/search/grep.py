from collections import deque
import json
import subprocess
from pathlib import Path
from typing import Iterator

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
        return (
            "Search for specific text content or patterns inside files within "
            "the workspace. Respects .gitignore rules and skips hidden files "
            "and directories; sensitive file names (e.g. .env, *.pem) are "
            "filtered from the results."
        )

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
                    "description": "File pattern to restrict the search, relative to the workspace root. Defaults to '**/*' to search all non-hidden, non-gitignored files.",
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
        self._validate_arguments(before, after, max_results)

        if max_results == 0:
            return ""

        self._validate_pattern(pattern)
        workspace_root = self.workspace_boundary.root
        command = self._build_command(query, pattern, before, after)
        stdout = self._run_ripgrep(command, workspace_root)

        remaining = max_results
        pending_after = 0
        recent = deque(maxlen=before)
        lines = []

        for event in self._parse_events(stdout):
            event_type = event["type"]
            
            if event_type not in {"match", "context"}:
                continue

            data = event["data"]
            path = Path(data["path"]["text"])

            if not self.search_visibility.is_visible(path):
                continue

            if event_type == "match":
                if pending_after > 0:
                    lines.append(self._format_line(data))
                    pending_after -= 1
                elif remaining is None or remaining > 0:
                    lines.extend(recent)
                    recent.clear()
                    lines.append(self._format_line(data))

                    if remaining is not None:
                        remaining -= 1
                    
                    pending_after = after

            else:
                if pending_after > 0:
                    lines.append(self._format_line(data))
                    pending_after -= 1
                else:
                    recent.append(self._format_line(data))

            if remaining == 0 and pending_after == 0:
                break

        return "\n".join(self.output_budget.enforce(lines))


    def _validate_arguments(
        self,
        before,
        after,
        max_results,
        ):
        if before < 0:
            raise ValueError("before must be >= 0")

        if after < 0:
            raise ValueError("after must be >= 0")

        if max_results is not None and max_results < 0:
            raise ValueError("max_results must be >= 0")


    def _run_ripgrep(
        self,
        command: list[str],
        workspace_root: Path,
    ) -> Iterator[str]:
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=workspace_root,
            )
        except FileNotFoundError:
            raise RuntimeError(
                "ripgrep (rg) binary is not installed on the system"
            )

        def stream() -> Iterator[str]:
            try:
                for line in process.stdout:
                    yield line

                # Natural end: rg finished on its own. Enforce the
                # returncode contract (1 = no matches, 2 = bad usage).
                stderr_text = process.stderr.read()
                returncode = process.wait()

                if returncode == 2:
                    raise RuntimeError(stderr_text.strip())
            finally:
                # Reached on natural end OR on early close (break/GeneratorExit).
                if process.poll() is None:      # process still alive?
                    process.kill()
                process.wait()                  # reap it in every case

        return stream()


    def _build_command(
        self,
        query: str,
        pattern: str,
        before: int,
        after: int,
        ) -> list[str]:
        return [
            "rg",
            "--json",
            "-B", str(before),
            "-A", str(after),
            "-g", pattern,
            "-e", query,
            # Explicit search path: without it, rg's behavior depends on
            # stdin (reads stdin when it is a pipe, searches the directory
            # only when stdin is a TTY). "." makes the search deterministic.
            ".",
        ]


    def _parse_events(
        self,
        stdout,
    ) -> Iterator:
        
        for line in stdout:
            event = json.loads(line)
            
            data = event.get("data")
            if data is None or "path" not in data:
                continue

            path_text = data["path"]["text"]
            data["path"]["text"] = self._strip_search_prefix(path_text)

            yield event


    def _strip_search_prefix(self, path_text: str) -> str:
        if path_text.startswith("./") or path_text.startswith(".\\"):
            return path_text[2:]

        return path_text


    def _validate_pattern(
        self,
        pattern: str
    ) -> None:
        pattern_path = Path(pattern)
        
        if pattern_path.is_absolute() or ".." in pattern_path.parts:
            raise WorkspaceBoundaryViolation(
                f"Outside boundary: {pattern}"
            )


    def _format_line(self, data) -> str:
        path = data["path"]["text"]
        line_number = data["line_number"]
        line = data["lines"]["text"].rstrip("\r\n")
        
        if len(line) > MAX_LINE_CHARS:
            line = line[:MAX_LINE_CHARS] + " [line truncated]"

        return f"{path}:{line_number}:{line}"