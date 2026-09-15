from enum import Enum


class TrustLevel(str, Enum):
    TRUSTED = "trusted"
    UNTRUSTED = "untrusted"
    UNKNOWN = "unknown"