from pathlib import Path

from ..base_tool import BaseTool


class DeleteFileTool(BaseTool):
    @property
    def name(self) -> str:
        return "delete_file"

    @property
    def description(self) -> str:
        return "Delete a file"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to delete.",
                },
            },
            "required": ["path"],
            "additionalProperties": False,
        }

    def execute(self, path: str) -> str:
        file = Path(path)

        if not file.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        file.unlink()

        return f"Successfully deleted {path}"