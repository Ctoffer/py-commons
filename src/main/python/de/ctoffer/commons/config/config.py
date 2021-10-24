from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Callable, Union

from commons.creational.singleton import singleton
from commons.util.project import load_resource, ProjectManager

@dataclass
class Parameter:
    optional: bool = False
    empty: Any = None


class Primitive(Parameter):
    def __init__(self, type_hint, optional: bool = False, empty: Any = None):
        self._type_hint = type_hint
        super().__init__(optional=optional, empty=empty)

    def __call__(self, value):
        return value


class Container(Parameter):
    pass


class Unit(Parameter):
    pass


def container(
        sequence,
        frozen: bool = True,
        unique: bool = False,
        min_size: int = 0,
        max_size: int = None,
        optional: bool = False
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


def unit(type_hint, non_null: bool = True, optional: bool = False):
    # TODO (Christopher): Create a parser for this configuration
    #   1. check if type_hint has specialized __init__
    #   2. if not add it
    #   3. convert input
    return Unit()


def ensure_init(type_hint):
    pass


def create_init(annotations: dict) -> Callable[[Any, ...], None]:
    mappers = {key: type_to_parser(value) for key, value in annotations.items()}

    def __init__(self, **kwargs):
        used_keys = set(kwargs.keys())

        for key, mapper in mappers.items():
            if mapper.optional and key not in kwargs:
                setattr(self, key, mapper.empty)
            elif not mapper.optional and key not in kwargs:
                raise ValueError(f"Mandatory attribute '{key}' is missing.")
            else:
                used_keys.remove(key)
                setattr(self, key, mapper(kwargs[key]))

        if used_keys:
            # TODO (Christopher): Use a logger instead.
            print(f"[WARNING] During initialization of {type(self)} configured properties {used_keys} were not used.")

    return __init__


def type_to_parser(type_hint: Any) -> Parameter:
    if type_hint in (int, float, bool, str):
        return Primitive(type_hint)
    elif isinstance(type_hint, Parameter):
        return type_hint
    else:
        raise ValueError(f"Unknown type_hint '{type_hint}'.")


def config(file, *path, as_singleton=True):
    def enhance_type(cls):
        def __init__(self):
            complete_path = [file] + list(path)
            complete_path[-1] = complete_path[-1] + ".yaml"
            attributes = load_resource(*complete_path)

            initialize = create_init(cls.__annotations__)
            initialize(self, **attributes)

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


@config("config", "my_config")
class MyConfig:
    global_attr: int
    default_attr: Primitive(float, optional=True, empty=3.5)
    # nested_attr: unit(NestedConfigFragment)


ProjectManager.instance.configure(__file__)
global_config = MyConfig.instance
print(global_config.global_attr)
print(global_config.default_attr)
