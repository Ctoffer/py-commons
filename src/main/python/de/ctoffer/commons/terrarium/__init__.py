import importlib
import pkgutil
import re
from contextlib import AbstractContextManager
from types import ModuleType
from typing import Callable, Self

from commons.terrarium.component.descriptor import ComponentDescriptor
from commons.terrarium.component.descriptor_factory import ComponentDescriptorFactory
from commons.terrarium.component.registry import TerrariumComponentRegistry, proxy_of_type, proxy_of_callable


def component[T](
        name: str | Callable[[...], T] | type[T] = None,
        *,
        primary: bool = False
):
    def decorate(obj: Callable[[...], T] | type[T]):
        normalized_name = name if type(name) == str else _to_lower_snake_case(obj.__name__)
        print(f"Decorate: {obj.__name__} normalized_name: {normalized_name})")
        registry = TerrariumComponentRegistry()

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


def component_scan(*args: ModuleType):
    for module in args:
        for _, module_name, is_pkg in pkgutil.walk_packages(
                module.__path__,
                module.__name__ + '.',
        ):
            importlib.import_module(module_name)


class Terrarium(AbstractContextManager[Self]):

    def __init__(self, packages: tuple[ModuleType, ...]):
        self._registry: TerrariumComponentRegistry = TerrariumComponentRegistry()
        self._packages: tuple[ModuleType, ...] = packages

    def __enter__(self) -> Self:
        component_scan(*self._packages)
        self._registry.initialize_components()
        self._registry.post_init_components()
        return self

    def __exit__(self, exc_type, exc_value, traceback, /):
        self._registry.pre_destruct_components()
        pass

    def __getitem__[T](self, descriptor: type[T] | str | ComponentDescriptor) -> T:
        if isinstance(descriptor, str):
            descriptor = ComponentDescriptorFactory.of(name=descriptor)
        elif isinstance(descriptor, type):
            descriptor = ComponentDescriptorFactory.of(type_=descriptor)

        return self._registry[descriptor]