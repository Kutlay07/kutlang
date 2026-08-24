from pathlib import Path

from ..base_tool import BaseTool


class EditFileTool(BaseTool):
    @property
    def name(self) -> str:
        return "edit_file"

    @property
    def description(self) -> str:
        return "Replace text in a file"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to edit.",
                },
                "old_text": {
                    "type": "string",
                    "description": "Text to replace.",
                },
                "new_text": {
                    "type": "string",
                    "description": "Replacement text.",
                },
            },
            "required": ["path", "old_text", "new_text"],
            "additionalProperties": False,
        }

    def execute(
        self,
        path: str,
        old_text: str,
        new_text: str,
    ) -> str:
        file = Path(path)
        content = file.read_text(encoding="utf-8")

        if old_text not in content:
            raise ValueError("Text to replace was not found in the file")

        file.write_text(
            content.replace(old_text, new_text, 1),
            encoding="utf-8",
        )

        return f"Successfully edited {path}"