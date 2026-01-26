import re
from enum import Enum
from functools import wraps
from typing import Callable, Any

from commons.util.singleton import Singleton


class ProtoType(Enum):
    COMPONENT = 1
    SERVICE = 2
    REPOSITORY = 3

class ComponentProxy:
    pass

class ComponentDescriptor:
    pass

class ComponentRegistry(metaclass=Singleton):
    class State(Enum):
        SCANNING = 1
        INITIALIZING = 2
        POST_CONSTRUCTION = 3
        PRE_DESTRUCTION = 4
        DESTROYED = 5

    def __init__(self):
        self._state = ComponentRegistry.State.SCANNING

    def __iadd__(self, component: ComponentProxy) -> 'ComponentRegistry':
        return self

    def __getattr__(self, descriptor: ComponentDescriptor) -> ComponentProxy:
        pass

    @property
    def state(self) -> 'ComponentRegistry.State':
        return self._state

    def initialize_components(self) -> None:
        pass

    def post_construct_components(self) -> None:
        pass

    def pre_destruct_components(self) -> None:
        pass


def component(name: str | Callable | type[Any] = None, *, prototype: ProtoType = ProtoType.COMPONENT):
    def decorate(obj: Callable | type[Any]):
        print(f"Decorate: {obj.__name__} normalized_name: {to_lower_snake_case(obj.__name__)})")
        if isinstance(obj, type):
            return obj

        elif callable(obj):
            @wraps(obj)
            def wrapper(*args, **kwargs):
                return obj(*args, **kwargs)

            return wrapper

        else:
            raise TypeError


    if callable(name) and not isinstance(name, type):
        return decorate(name)

    if isinstance(name, type):
        return decorate(name)

    return decorate

_PATTERN_CAMEL_CASE_1 = re.compile(r"(.)([A-Z][a-z]+)")
_PATTERN_CAMEL_CASE_2 = re.compile(r"([a-z0-9])([A-Z])")

def to_lower_snake_case(text: str) -> str:
    if "_" in text and text.islower():
        return text

    s1 = _PATTERN_CAMEL_CASE_1.sub(r"\1_\2", text)
    s2 = _PATTERN_CAMEL_CASE_2.sub(r"\1_\2", s1)

    return s2.lower()

@component
class FooAsClass:
    pass

@component(name="custom_name")
class BarAsClass:
    pass

@component
def foo_as_function():
    pass

@component(name="custom_method_name")
def bar_as_function():
    pass
