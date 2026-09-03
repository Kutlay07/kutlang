from pathlib import Path

from harness.security.workspace_boundary import WorkspaceBoundaryViolation


class WorkspacePathGuard:
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()
        
    def validate(self, path: str) -> Path:
        resolved = (self.workspace_root / path).resolve()
        
        if not resolved.is_relative_to(self.workspace_root):
            raise WorkspaceBoundaryViolation("Path is outside the workspace boundary")
        
        return resolved