from enum import Enum


class RiskLevel(str, Enum):
    LOW = ("low", 1)
    MEDIUM = ("medium", 2)
    HIGH = ("high", 3)
    CRITICAL = ("critical", 4)
    
    def __new__(cls, string_val, numeric_val):
        obj = str.__new__(cls, string_val)
        obj._value_ = string_val
        
        obj.score = numeric_val
        return obj
    
    """to compare and use max(), min(), sort() functions"""
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.score < other.score
        return NotImplemented
    
    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.score <= other.score
        return NotImplemented
    
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.score > other.score
        return NotImplemented
    
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.score >= other.score
        return NotImplemented