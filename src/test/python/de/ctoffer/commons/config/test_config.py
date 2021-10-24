
from dataclasses import dataclass
from typing import Sequence

from commons.config.config import Primitive, Container, config
from commons.util.project import ProjectManager


@dataclass(frozen=True)
class BooleanOperation:
    x: bool
    y: bool
    xor: bool


@dataclass(frozen=True)
class NestedConfigFragment:
    demo_list: Container(Sequence[BooleanOperation])
    flat_attr: str


@config("config", "my_config")
class MyConfig:
    global_attr: int
    default_attr: Primitive(float, optional=True, empty=3.5)
    # nested_attr: unit(NestedConfigFragment)


ProjectManager.instance.configure(__file__).test_mode()
global_config = MyConfig.instance
print(global_config.global_attr)
print(global_config.default_attr)
