from pathlib import Path

from ..sync_base_tool import SyncBaseTool


class GetCurrentDirectoryTool(SyncBaseTool):
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