from pathlib import Path

from ..base_tool import BaseTool


class MoveFileTool(BaseTool):
    @property
    def name(self) -> str:
        return "move_file"

    @property
    def description(self) -> str:
        return "Move a file to a different path"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "Path to the file to move.",
                },
                "destination": {
                    "type": "string",
                    "description": "Destination path for the file.",
                },
            },
            "required": ["source", "destination"],
            "additionalProperties": False,
        }

    def execute(self, source: str, destination: str) -> str:
        file = Path(source)

        if not file.is_file():
            raise FileNotFoundError(f"File not found: {source}")

        file.rename(destination)

        return f"Successfully moved {source} to {destination}"