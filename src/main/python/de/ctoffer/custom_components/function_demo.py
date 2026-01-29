from typing import Any

from commons.terrarium import component
from custom_components.class_demo import MyArgument
from custom_components.non_components import MyClass


@component
def foo_as_function(my_argument: MyArgument) -> MyClass:
    instance = MyClass()
    instance.my_argument = my_argument
    return instance


@component(primary=True)
def foo_as_function_primary() -> MyClass:
    instance = MyClass()
    instance.my_argument = "PRIMARY"
    return instance


@component(name="custom_function_name")
def bar_as_function() -> MyClass:
    pass
