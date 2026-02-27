import re
from typing import Tuple
#### REGEX PATTERNS ####

REGEX_PATTERNS = {
    "page": r"/(?<=\<\!)(.+)\>([\s\S]+?)<\!/mg",
}


def _compile_pattern(pattern_key: str) -> Tuple[str, int]:
    pattern = REGEX_PATTERNS.get(pattern_key)
    if pattern is None:
        raise KeyError(f"Unknown pattern key: {pattern_key}")

    match = re.match(r"^/(.*?)/([a-z]*)$", pattern)
    if not match:
        return pattern, re.DOTALL

    body, flags_text = match.groups()
    flags = 0
    if "i" in flags_text:
        flags |= re.IGNORECASE
    if "m" in flags_text:
        flags |= re.MULTILINE
    if "s" in flags_text:
        flags |= re.DOTALL
    return body, flags

def clean_page(string: str) -> str:
    matches = list(re.finditer(r"\d+", string))
    if not matches:
        raise ValueError("Expected at least one number in string.")
    max_match = max(matches, key=lambda match: int(match.group(0)))
    return max_match.group(0)
