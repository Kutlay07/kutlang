from typing import Protocol


class EntropyDetector(Protocol):
    
    def entropy(self, value: str) -> float:
        ...