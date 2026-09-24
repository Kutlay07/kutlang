from pathlib import Path
from typing import Protocol


class WorkspaceBoundary(Protocol):

    @property
    def root(self) -> Path:
        ...

    def validate(self, path: str) -> Path:
        ...


class WorkspaceBoundaryViolation(Exception):
    ...