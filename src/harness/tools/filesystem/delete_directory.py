from harness.security.workspace_boundary import WorkspaceBoundary

from ..base_tool import BaseTool


class DeleteDirectoryTool(BaseTool):
    
    def __init__(self, workspace_boundary: WorkspaceBoundary):
        self.workspace_boundary = workspace_boundary
    
    @property
    def name(self) -> str:
        return "delete_directory"
    
    @property
    def description(self) -> str:
        return "Delete an empty directory"
    
    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the empty directory to delete.",
                },
            },
            "required": ["path"],
            "additionalProperties": False,
        }
        
    def execute(self, path: str) -> str:
        validated_path = self.workspace_boundary.validate(path)
        
        if not validated_path.is_dir():
            raise FileNotFoundError(
                f"Directory not found: {path}"
            )
            
        validated_path.rmdir()
        
        return f"Successfully deleted directory {path}"