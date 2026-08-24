from pathlib import Path

from ..base_tool import BaseTool


class AppendFileTool(BaseTool):
    @property
    def name(self) -> str:
        return "append_file"

    @property
    def description(self) -> str:
        return "Append content to the end of a file"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file.",
                },
                "content": {
                    "type": "string",
                    "description": "Content to append to the file.",
                },
            },
            "required": ["path", "content"],
            "additionalProperties": False,
        }

    def execute(self, path: str, content: str) -> str:
        with Path(path).open("a", encoding="utf-8") as file:
            file.write(content)

        return f"Successfully appended content to {path}"