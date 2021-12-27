from dataclasses import dataclass
from typing import Sequence

from commons.config.config import Primitive, config
from commons.util.project import configure_project


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
    instance: 'MyConfig'

    global_attr: int
    default_attr: Primitive(float, optional=True, empty=3.5)
    nested_attr: NestedConfigFragment


configure_project(__file__, test_mode=True)
global_config = MyConfig.instance
print(global_config.global_attr)
print(global_config.default_attr)
print(global_config.nested_attr.demo_list[0])
print(global_config.nested_attr.primitive_list)
print(global_config.nested_attr.array_2d)


@config("config", "conf_text_[0]", as_singleton=False)
class MyConfig2:
    text: str


print(MyConfig2(0).text)
print(MyConfig2(1).text)


@config("config", "conf_text_{id}", as_singleton=False)
class MyConfig2:
    text: str


print(MyConfig2(id=0).text)
print(MyConfig2(id=1).text)


@dataclass
class GrandParentConfig:
    attr_1: int
    attr_3: int


@dataclass
class ParentConfig(GrandParentConfig):
    attr_2: int


@config("config", "child_[0]_config", as_singleton=False)
class ChildConfig(ParentConfig):
    attr_4: str


child_config = ChildConfig(1)
child_config.attr_1 = 5
print(child_config.attr_1, child_config.attr_2, child_config.attr_3, child_config.attr_4)
