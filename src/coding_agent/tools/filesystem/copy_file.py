from pathlib import Path
import shutil

from ..base_tool import BaseTool


class CopyFileTool(BaseTool):
    @property
    def name(self) -> str:
        return "copy_file"

    @property
    def description(self) -> str:
        return "Copy a file to a different path"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "Path to the file to copy.",
                },
                "destination": {
                    "type": "string",
                    "description": "Destination path for the copy.",
                },
            },
            "required": ["source", "destination"],
            "additionalProperties": False,
        }

    def execute(self, source: str, destination: str) -> str:
        file = Path(source)

        if not file.is_file():
            raise FileNotFoundError(f"File not found: {source}")

        shutil.copy2(source, destination)

        return f"Successfully copied {source} to {destination}"