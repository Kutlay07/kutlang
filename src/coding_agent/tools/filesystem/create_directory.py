from pathlib import Path

from ..base_tool import BaseTool


class CreateDirectoryTool(BaseTool):
    @property
    def name(self) -> str:
        return "create_directory"

    @property
    def description(self) -> str:
        return "Create a directory"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path of the directory to create.",
                },
            },
            "required": ["path"],
            "additionalProperties": False,
        }

    def execute(self, path: str) -> str:
        Path(path).mkdir(parents=True, exist_ok=False)

        return f"Successfully created directory {path}"