from pathlib import Path

from ..base_tool import BaseTool


class ReadFileRangeTool(BaseTool):
    @property
    def name(self) -> str:
        return "read_file_range"

    @property
    def description(self) -> str:
        return "Read a specific range of lines from a file"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read.",
                },
                "start_line": {
                    "type": "integer",
                    "description": "First line to read, starting from 1.",
                },
                "end_line": {
                    "type": "integer",
                    "description": "Last line to read, inclusive.",
                },
            },
            "required": ["path", "start_line", "end_line"],
            "additionalProperties": False,
        }

    def execute(
        self,
        path: str,
        start_line: int,
        end_line: int,
    ) -> str:
        if start_line < 1:
            raise ValueError("start_line must be at least 1")

        if end_line < start_line:
            raise ValueError("end_line must be greater than or equal to start_line")

        lines = Path(path).read_text(encoding="utf-8").splitlines()

        return "\n".join(lines[start_line - 1:end_line])