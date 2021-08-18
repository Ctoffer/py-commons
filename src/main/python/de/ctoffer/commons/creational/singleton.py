class ClassPropertyDescriptor(object):
    """ Descriptor for properties at class-level instead of object-level.

    This descriptor only implements the getter part of class-level properties.
    """

    def __init__(self, function_getter):
        """ Initialize descriptor with getter function.

        :param function_getter: the function which should be used as __get__ of an attribute
        """
        self._function_getter = function_getter

    def __get__(self, obj, clazz=None):
        """ Implements the get of the attribute.

        :param obj: Always None because descriptor works on class level.
        :param clazz: The class this descriptor is used for.
        :return: The result of the specified getter function.
        """

        return self._function_getter.__get__(obj, clazz)()


def classproperty(func):
    """ Simple function decorator for the ClassPropertyDescriptor.

    :param func: The function which should be used as getter for an (imaginary) attribute at class level.
    :return: The decorated descriptor implementing the getter.
    """

    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return ClassPropertyDescriptor(func)


def singleton(cls=None):
    """ Decorator for classes to enforce singleton semantics.

    Example::
        @singleton
        class Foo:
            def __init__(self):
                self._name = "Hello"

            @classmethod
            def foo(cls) -> str:
                return "bar"

            @property
            def name(self) -> str:
                return self._name

            @name.setter
            def name(self, name: str):
                self._name = name

        print("foo()", Foo.foo())
        print("name", Foo.instance.name)
        Foo.instance.name = "World"
        print("name", Foo.instance.name)


    :param cls: Class which should be used as a singleton.
    :return: The given class, but enhanced with singleton semantics
    """

    def transform_to_singleton():
        """ Helper function to enforce singleton semantics.

        Overrides __new__ and __init__ of class to block manual instantiation.
        Add classproperty 'instance' to instantiate the singleton.

        :return:
        """
        _instance = None
        old_new = cls.__new__

        def new_call(self):
            """ Raises to inform user that they should use 'instance' property.

            :param self: Dummy self to mimmic python arguments.
            :raises NotImplementedError: Always raises this exception.
            """
            raise NotImplementedError("Singletons can only be instantiated via 'instance' property."
                                      "Refer to the documentation for more information.")

        def instance(clz):
            """ Implementation of the instance property - before it becomes a property.

            This function implements a lazy-init singleton creation with a no-args __init__ of the decorated
            class.

            :param clz: The class which has this property.
            :return: A runtime unique instance.
            """
            nonlocal _instance
            if _instance is None:
                _instance = old_new(clz)
                clz.__init__(_instance)
                clz.__init__ = new_call

            return _instance

        setattr(cls, "instance", classproperty(instance))
        cls.__new__ = new_call
        return cls

    def wrapper(clazz):
        """ Wrapper function if the decorator is called with emtpy args.

        :param clazz: Class which should be used as a singleton.
        :return: The given class, but enhanced with singleton semantics
        """
        nonlocal cls
        cls = clazz
        return transform_to_singleton()

    if cls is None:
        return wrapper
    else:
        return transform_to_singleton()
