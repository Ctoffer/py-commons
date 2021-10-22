from collections.abc import Sequence
from dataclasses import dataclass
from math import inf as infinity

from commons.creational.singleton import singleton


def config(file, as_singleton=True):
    def enhance_type(cls):
        print(cls.__annotations__)

        # TODO(Christopher): Create new init loading the resource

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
    demo_list: Sequence[BooleanOperation]
    flat_attr: str


@config("my_config")
class MyConfig:
    global_attr: int
    nested_attr: NestedConfigFragment


global_config = MyConfig.instance