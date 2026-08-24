from pathlib import Path

from ..base_tool import BaseTool


class DeleteDirectoryTool(BaseTool):
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
        directory = Path(path)
        
        if not directory.is_dir():
            raise FileNotFoundError(
                f"Directory not found: {path}"
            )
            
        directory.rmdir()
        
        return f"Successfully deleted directory {path}"