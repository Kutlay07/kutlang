import shutil

from harness.security.workspace_boundary import WorkspaceBoundary

from ..base_tool import BaseTool


class CopyFileTool(BaseTool):
    
    def __init__(self, workspace_boundary: WorkspaceBoundary):
        self.workspace_boundary = workspace_boundary
    
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
        validated_source = self.workspace_boundary.validate(source)
        validated_destination = self.workspace_boundary.validate(destination)
        
        if not validated_source.is_file():
            raise FileNotFoundError(f"File not found: {source}")
        
        shutil.copy2(validated_source, validated_destination)
        
        return f"Successfully copied {source} to {destination}"