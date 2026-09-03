from harness.security.workspace_boundary import WorkspaceBoundary

from ..base_tool import BaseTool


class DeleteFileTool(BaseTool):
    
    def __init__(self, workspace_boundary: WorkspaceBoundary):
        self.workspace_boundary = workspace_boundary
    
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
        validated_path = self.workspace_boundary.validate(path)

        if not validated_path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        validated_path.unlink()

        return f"Successfully deleted {path}"