from pathlib import Path

from ..base_tool import BaseTool


class GetCurrentDirectoryTool(BaseTool):
    @property
    def name(self) -> str:
        return "get_current_directory"

    @property
    def description(self) -> str:
        return "Get the current working directory"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }

    def execute(self) -> str:
        return str(Path.cwd())