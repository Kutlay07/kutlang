from pathlib import Path
from typing import Protocol


class SearchVisibility(Protocol):

    def is_visible(self, path: Path) -> bool:
        ...