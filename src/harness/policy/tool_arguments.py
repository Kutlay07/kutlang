import math
from dataclasses import dataclass
from collections.abc import Mapping
from types import MappingProxyType



def freeze(args):
    if isinstance(args, Mapping):
        return MappingProxyType({k: freeze(v) for k, v in args.items()})
    
    if isinstance(args, (bool, str, int, float, type(None))):
        return args
    
    if isinstance(args, list):
        return tuple(freeze(item) for item in args)


@dataclass(frozen=True)
class ToolArguments:
    
    arguments: Mapping[str, object]
    
    def __post_init__(self) -> None:
        seen = set()
        for key, value in self.arguments.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("argument key must not be empty")
            
            self._validate_value(value, seen)
            
        object.__setattr__(self, "arguments", freeze(self.arguments))


    @classmethod
    def _validate_value(cls, value: object, seen) -> None:
        if isinstance(value, float):
            if math.isfinite(value):
                return
            else:
                raise TypeError("value can't be non-finite")
            
        if value is None or isinstance(value, (str, int, bool)):
            return
        
        if isinstance(value, list):
            current_id = id(value)
            
            if current_id in seen:
                raise TypeError
            seen.add(current_id)
            
            try:
                for item in value:
                    cls._validate_value(item, seen)
            finally:
                seen.remove(current_id)
            return
        
        if isinstance(value, Mapping):
            current_id = id(value)
            
            if current_id in seen:
                raise TypeError
            
            seen.add(current_id)
            
            try:
                for key, item in value.items():
                    if not isinstance(key, str) or not key.strip():
                        raise ValueError("argument key must not be empty")
                    cls._validate_value(item, seen)
            finally:
                seen.remove(current_id)
            return
        
        raise TypeError("argument value must be JSON-compatible")