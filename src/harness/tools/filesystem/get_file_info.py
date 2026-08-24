from pathlib import Path

from ..base_tool import BaseTool


class GetFileInfoTool(BaseTool):
    @property
    def name(self) -> str:
        return "get_file_info"

    @property
    def description(self) -> str:
        return "Get basic information about a file or directory"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file or directory.",
                },
            },
            "required": ["path"],
            "additionalProperties": False,
        }

    def execute(self, path: str) -> str:
        target = Path(path)

        if not target.exists():
            raise FileNotFoundError(f"Path not found: {path}")

        if target.is_file():
            return (
                f"type: file\n"
                f"size: {target.stat().st_size}"
            )

        if target.is_dir():
            return (
                f"type: directory\n"
                f"size: {target.stat().st_size}"
            )

        return "type: other"