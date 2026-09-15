from typing import Protocol


class SecretRedactor(Protocol):
    
    def redact(self, text: str) -> str:
        ...