import importlib
import pkgutil

from contextlib import AbstractContextManager
from types import ModuleType
from typing import Callable, Self, Any, get_type_hints

import commons.terrarium.core_components
from commons.terrarium.component.descriptor import ComponentDescriptor
from commons.terrarium.component.descriptor_factory import ComponentDescriptorFactory
from commons.terrarium.component.lifecycle_hook import EntryPoint
from commons.terrarium.component.registry import TerrariumComponentRegistry, proxy_of_type, proxy_of_callable
from commons.terrarium.utils import to_lower_snake_case


def component[T](
        name: str | Callable[[...], T] | type[T] = None,
        *,
        primary: bool = False
):
    def decorate(obj: Callable[[...], T] | type[T]):
        normalized_name = name if type(name) == str else to_lower_snake_case(obj.__name__)
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
        component_scan(core_components)
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

    @staticmethod
    def start(
            packages: tuple[ModuleType, ...],
            main: Callable[[], None] | Callable[[Any, ...], None] = None):
        with Terrarium(packages=packages) as terra:
            if main is None:
                my_class = terra[EntryPoint]
                my_class.main()
            else:
                type_hints = get_type_hints(main)
                main_parameters = dict()
                for param_name, param_type in type_hints.items():
                    if param_name == "return":
                        print("Warning: Return type of main function is ignored!")
                        continue
                    resolved_parameter = terra[ComponentDescriptorFactory.of(name=param_name, type_=param_type)]
                    main_parameters[param_name] = resolved_parameter

                main(**main_parameters)
