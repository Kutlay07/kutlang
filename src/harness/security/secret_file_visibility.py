from fnmatch import fnmatch
from pathlib import Path

from harness.policy.risk_patterns import SENSITIVE_TARGET_PATTERNS
from harness.security.search_visibility import SearchVisibility


class SecretFileVisibility(SearchVisibility):

    def is_visible(self, path: Path) -> bool:
        for pattern in SENSITIVE_TARGET_PATTERNS:
            if fnmatch(path.name, pattern):
                return False
        return True