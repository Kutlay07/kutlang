from pathlib import Path

from ..base_tool import BaseTool


class FileExistsTool(BaseTool):
    @property
    def name(self) -> str:
        return "file_exists"

    @property
    def description(self) -> str:
        return "Check whether a file exists"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to check.",
                },
            },
            "required": ["path"],
            "additionalProperties": False,
        }

    def execute(self, path: str) -> str:
        return str(Path(path).is_file()).lower()