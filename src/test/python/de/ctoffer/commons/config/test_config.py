
from dataclasses import dataclass
from typing import Sequence

from commons.config.config import Primitive, Container, config, Unit
from commons.util.project import ProjectManager


@dataclass
class BooleanOperation:
    x: bool
    y: bool
    xor: bool


@dataclass
class NestedConfigFragment:
    demo_list: Sequence[BooleanOperation]
    primitive_list: Sequence[int]
    array_2d: Sequence[Sequence[int]]
    flat_attr: str


@config("config", "my_config")
class MyConfig:
    global_attr: int
    default_attr: Primitive(float, optional=True, empty=3.5)
    nested_attr: NestedConfigFragment


ProjectManager.instance.configure(__file__).test_mode()
global_config = MyConfig.instance
print(global_config.global_attr)
print(global_config.default_attr)
print(global_config.nested_attr.demo_list[0])
print(global_config.nested_attr.primitive_list)
print(global_config.nested_attr.array_2d)