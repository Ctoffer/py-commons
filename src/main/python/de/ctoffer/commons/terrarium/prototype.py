def component():
    pass


@component
class Foo:
    pass

@component(name="custom_name")
class Bar:
    pass
