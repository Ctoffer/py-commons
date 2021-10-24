from collections.abc import Sequence
from dataclasses import dataclass
from math import inf as infinity
from typing import Any, Callable, TypeVar

from commons.creational.singleton import singleton
from commons.util.project import load_resource, ProjectManager


class Container:
    pass


def container(
        sequence,
        frozen: bool = True,
        unique: bool = False,
        min_size: int = 0,
        max_size: int = None
):
    # TODO (Christopher): return a parser with this configuration, which converts a given sequence
    #      1. check size of given sequence [min_size,max_size]
    #      2. convert each entry [sequence.generic]
    #         2.1. check if class has specialized __init__
    #         2.2. if not add it
    #         2.3. call it with list element
    #      3. select data structure [frozen, unique]
    #      4. convert
    return Container()


class Unit:
    pass


def unit(type_hint, non_null: bool = True):
    # TODO (Christopher): Create a parser for this configuration
    #   1. check if type_hint has specialized __init__
    #   2. if not add it
    #   3. convert input
    return Unit()


def ensure_init(type_hint):
    pass


def create_init(annotations: dict) -> Callable[[Any, ...], None]:
    # TODO (Christopher):
    #     return an __init__ implementation which matches the __annotations__
    #     For each annotation present provide an conversion function taking a kwarg and returned correctly parsed
    #     object
    pass


def type_to_parser(type_hint: Any) -> Callable[..., Any]:
    if type_hint in (int, float, bool, str):
        return lambda element: element
    elif isinstance(type_hint, Container) or isinstance(type_hint, Unit):
        return lambda element: type_hint(element)
    else:
        raise ValueError(f"Unknown type_hint '{type_hint}'.")


def config(file, *path, as_singleton=True):
    def enhance_type(cls):
        def __init__(self):
            complete_path = [file] + list(path)
            complete_path[-1] = complete_path[-1] + ".yaml"
            attributes = load_resource(*complete_path)

            initialize = create_init(cls.__annotations__)
            initialize(self, attributes)

        cls.__init__ = __init__

        if as_singleton:
            result = singleton(cls)
        else:
            result = cls

        return result

    return enhance_type


@dataclass(frozen=True)
class BooleanOperation:
    x: bool
    y: bool
    xor: bool


@dataclass(frozen=True)
class NestedConfigFragment:
    demo_list: container(Sequence[BooleanOperation])
    flat_attr: str


@config("my_config")
class MyConfig:
    global_attr: int
    nested_attr: unit(NestedConfigFragment)


ProjectManager.instance.configure(__file__)
global_config = MyConfig.instance
