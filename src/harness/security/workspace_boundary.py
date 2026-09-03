from pathlib import Path
from typing import Protocol


class WorkspaceBoundary(Protocol):
    def validate(self, path: str) -> Path:
        ...


class WorkspaceBoundaryViolation(Exception):
    ...