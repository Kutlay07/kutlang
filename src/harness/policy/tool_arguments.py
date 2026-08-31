from dataclasses import dataclass
from collections.abc import Mapping


@dataclass(frozen=True)
class ToolArguments:
    arguments: Mapping[str, object]
    
    def __post_init__(self) -> None:
        for key, value in self.arguments.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("argument key must not be empty")
            
            self._validate_value(value)
            
    @classmethod
    def _validate_value(cls, value: object) -> None:
        if value is None or isinstance(value, (str, int, float, bool)):
            return
        
        if isinstance(value, list):
            for item in value:
                cls._validate_value(item)
            return
        
        if isinstance(value, Mapping):
            for key, item in value.items():
                if not isinstance(key, str) or not key.strip():
                    raise ValueError("argument key must not be empty")
                cls._validate_value(item)
            return
        
        raise TypeError("argument value must be JSON-compatible")