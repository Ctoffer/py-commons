from collections.abc import Sequence
from dataclasses import dataclass
from math import inf as infinity

from commons.creational.singleton import singleton
from commons.util.project import load_resource, ProjectManager


def container(sequence, frozen: bool = False, unique: bool = False, min_size: int = 0, max_size: int = None):
    # TODO (Christopher): return a parser with this configuration, which converts a given sequence
    #      1. check size of given sequence [min_size,max_size]
    #      2. convert each entry [sequence.generic]
    #         2.1. check if class has specialized __init__
    #         2.2. if not add it
    #         2.3. call it with list element
    #      3. select data structure [frozen, unique]
    #      4. convert
    pass


def create_init(annotations: dict):
    # TODO (Christopher):
    #     return an __init__ implementation which matches the __annotations__
    #     For each annotation present provide an conversion function taking a kwarg and returned correctly parsed
    #     object
    pass


def type_to_parser():
    # TODO (Christopher):
    #     decide on given type_hint which parser is most appropriate
    #     primitives
    #     container
    #     fragment?
    pass


def config(file, *path, as_singleton=True):
    def enhance_type(cls):
        print(cls.__annotations__)

        # TODO(Christopher): Create new init loading the resource
        def __init__(self, **kwargs):
            complete_path = [file] + list(path)
            complete_path[-1] = complete_path[-1] + ".yaml"
            attributes = load_resource(*complete_path)

            for name, value in cls.__annotations__.items():
                print(name, attributes[name], value)

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
    demo_list: Sequence[BooleanOperation]
    flat_attr: str


@config("my_config")
class MyConfig:
    global_attr: int
    nested_attr: NestedConfigFragment


ProjectManager.instance.configure(__file__)
global_config = MyConfig.instance
