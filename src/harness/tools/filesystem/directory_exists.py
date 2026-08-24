from pathlib import Path

from ..base_tool import BaseTool


class DirectoryExistsTool(BaseTool):
    @property
    def name(self) -> str:
        return "directory_exists"

    @property
    def description(self) -> str:
        return "Check whether a directory exists"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the directory to check.",
                },
            },
            "required": ["path"],
            "additionalProperties": False,
        }

    def execute(self, path: str) -> str:
        return str(Path(path).is_dir()).lower()