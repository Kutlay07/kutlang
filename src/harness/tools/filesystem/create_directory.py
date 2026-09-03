from harness.security.workspace_boundary import WorkspaceBoundary

from ..base_tool import BaseTool


class CreateDirectoryTool(BaseTool):
    
    def __init__(self, workspace_boundary: WorkspaceBoundary):
        self.workspace_boundary = workspace_boundary
        
    @property
    def name(self) -> str:
        return "create_directory"

    @property
    def description(self) -> str:
        return "Create a directory"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path of the directory to create.",
                },
            },
            "required": ["path"],
            "additionalProperties": False,
        }

    def execute(self, path: str) -> str:
        validated_path = self.workspace_boundary.validate(path)
        validated_path.mkdir(parents=True, exist_ok=False)

        return f"Successfully created directory {path}"