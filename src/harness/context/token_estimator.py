import unicodedata


def estimate_tokens(content: str) -> int:
    wide = sum(unicodedata.east_asian_width(ch) in ("W", "F") for ch in content)

    narrow = len(content) - wide
    return max(1, narrow // 4 + wide)
