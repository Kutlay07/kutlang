from harness.security.workspace_boundary import WorkspaceBoundary

from ..sync_base_tool import SyncBaseTool


class AppendFileTool(SyncBaseTool):
    
    def __init__(self, workspace_boundary: WorkspaceBoundary):
        self.workspace_boundary = workspace_boundary
    
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
        validated_path = self.workspace_boundary.validate(path)
        with validated_path.open("a", encoding="utf-8") as file:
            file.write(content)

        return f"Successfully appended content to {path}"