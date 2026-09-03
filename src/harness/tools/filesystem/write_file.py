from harness.security.workspace_boundary import WorkspaceBoundary

from ..base_tool import BaseTool


class WriteFileTool(BaseTool):
    
    def __init__(self, workspace_boundary: WorkspaceBoundary):
        self.workspace_boundary = workspace_boundary
    
    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write content to a file"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to write.",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file.",
                },
            },
            "required": ["path", "content"],
            "additionalProperties": False,
        }

    def execute(self, path: str, content: str) -> str:
        validated_path = self.workspace_boundary.validate(path)
        validated_path.write_text(content, encoding="utf-8")
        return f"Successfully wrote to {path}"