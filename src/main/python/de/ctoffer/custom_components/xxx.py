from typing import Any

from commons.terrarium import component


@component
class FooAsClass:
    pass


@component(name="custom_name")
class BarAsClass:
    pass

class MyClass:
    my_argument: Any

@component
class MyArgument:
    def __str__(self):
        return "MyArgument"

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