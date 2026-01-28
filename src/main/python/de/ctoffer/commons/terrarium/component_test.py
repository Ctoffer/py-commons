from commons.terrarium import component
from commons.terrarium.component.descriptor_factory import ComponentDescriptorFactory
from commons.terrarium.component.registry import ComponentRegistry


@component
class FooAsClass:
    pass


@component(name="custom_name")
class BarAsClass:
    pass

class MyClass:
    pass

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

def main():
    registry = ComponentRegistry()
    registry.initialize_components()
    my_class = registry[ComponentDescriptorFactory.of(type_=MyClass, name="foo_as_function")]
    print(my_class.my_argument)

if __name__ == '__main__':
    main()