from collections import Counter
from math import log2

from harness.observability.redaction.entropy_detector import EntropyDetector


class DefaultEntropyDetector(EntropyDetector):
    def entropy(self, value: str) -> float:
        total = len(value)
        
        if total <= 1:
            return 0.0
        
        _log2 = log2
        frequencies = Counter(value).values()
        
        sum_freq_log = sum(
            f * _log2(f)
            for f in frequencies
        )
        
        return _log2(total) - (sum_freq_log / total)