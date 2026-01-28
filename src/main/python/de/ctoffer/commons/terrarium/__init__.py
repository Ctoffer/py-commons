import re
from typing import Callable

from commons.terrarium.component.registry import ComponentRegistry, proxy_of_type, proxy_of_callable


def component[T](
        name: str | Callable[[...], T] | type[T] = None,
        *,
        primary: bool = False
):
    def decorate(obj: Callable[[...], T] | type[T]):
        normalized_name = name if type(name) == str else _to_lower_snake_case(obj.__name__)
        print(f"Decorate: {obj.__name__} normalized_name: {normalized_name})")
        registry = ComponentRegistry()

        if isinstance(obj, type):
            registry += proxy_of_type(obj, name=normalized_name, primary=primary)
        elif callable(obj):
            registry += proxy_of_callable(obj, name=normalized_name, primary=primary)
        else:
            raise TypeError

        return obj

    if isinstance(name, type):
        return decorate(name)
    elif callable(name):
        return decorate(name)
    else:
        return decorate


_PATTERN_CAMEL_CASE_1 = re.compile(r"(.)([A-Z][a-z]+)")
_PATTERN_CAMEL_CASE_2 = re.compile(r"([a-z0-9])([A-Z])")


def _to_lower_snake_case(text: str) -> str:
    if "_" in text and text.islower():
        return text

    s1 = _PATTERN_CAMEL_CASE_1.sub(r"\1_\2", text)
    s2 = _PATTERN_CAMEL_CASE_2.sub(r"\1_\2", s1)

    return s2.lower()
