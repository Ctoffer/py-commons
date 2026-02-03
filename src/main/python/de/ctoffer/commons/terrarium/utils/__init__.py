import re

_PATTERN_CAMEL_CASE_1 = re.compile(r"(.)([A-Z][a-z]+)")
_PATTERN_CAMEL_CASE_2 = re.compile(r"([a-z0-9])([A-Z])")


def to_lower_snake_case(text: str) -> str:
    if "_" in text and text.islower():
        return text

    s1 = _PATTERN_CAMEL_CASE_1.sub(r"\1_\2", text)
    s2 = _PATTERN_CAMEL_CASE_2.sub(r"\1_\2", s1)

    return s2.lower()
