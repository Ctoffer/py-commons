from commons.terrarium import component


@component
class FooAsClass:
    pass


@component(name="custom_name")
class BarAsClass:
    pass

@component
class MyArgument:
    def __str__(self):
        return "MyArgument"