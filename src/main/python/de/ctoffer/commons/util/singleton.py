from typing import Any, Type, TypeVar, Generic

T = TypeVar('T')


class Singleton(type):
    """Metaclass which enables singleton pattern for a class.

    This metaclass modifies the creation of an object of a given class.
    For each class an instance is cached in the internal `_instances` dictionary.

    In case an instance was already constructed it is reused.
    In case this is the first instance a new instance is created (forwards parameters to the __init__)
    and caches this instance.
    Therefore, using parameters during object creation might not result in intended behavior!
    """
    _instances = {}

    def __call__(
            cls: Type[T],
            *args: Any,
            **kwargs: Any
    ) -> Type[T]:
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

