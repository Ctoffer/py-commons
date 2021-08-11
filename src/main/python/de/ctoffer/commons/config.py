import functools
import re
from inspect import signature
from types import SimpleNamespace

from singleton import singleton, classproperty


@singleton
class Config:
    def __init__(self):
        self._primitive = SimpleNamespace(**{"number": 7})

    @classproperty
    @classmethod
    def instance(cls):
        return None

    @property
    def primitive2(self):
        return self._primitive


class KwargBinding:
    def __init__(self, func):
        self._func_call = func.__call__
        self._func_name = func.__name__
        self._func_doc = func.__doc__
        self._resolve_values = list()

    @property
    def __doc__(self):
        return self._func_doc

    @property
    def __name__(self):
        return self._func_name

    def __call__(self, *args, **kwargs):
        for name, (source, default) in self._resolve_values:
            try:
                kwargs[name] = source()
            except:
                kwargs[name] = default

        self._func_call(*args, **kwargs)

    def __setitem__(self, name, value):
        source, default = value
        self._resolve_values.append((name, (source, default)))


def value(source, target, default=None):
    def outer_wrapper(func):
        if type(func) != KwargBinding:
            binding = KwargBinding(func)
            setattr(func, "__kwarg_binding", binding)
        else:
            binding = func

        binding[target] = (source, default)

        return binding

    return outer_wrapper


@value(source=lambda: Config.instance.primitive2.number, target="number", default=-1)
@value(source=lambda: Config.instance.primitive2.y, target="y", default=-1)
def my_function(a, b, number=None, y=None):
    print("a", a, "b", b, "number", number, y)


def main():
    my_function(7, b=3)


if __name__ == '__main__':
    main()
