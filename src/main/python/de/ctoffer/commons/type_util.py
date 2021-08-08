import functools
from inspect import signature


class Constraint:
    @classmethod
    def from_tuple(cls, tup):
        def equals(a):
            if not (value == a):
                raise ValueError(f"Constraint actual:{a} == expected:{value} not met!")

        def greater_or_equals_than(a):
            if not (a >= value):
                raise ValueError(f"Constraint actual:{a} >= expected:{value} not met!")

        def less_than(a):
            if not (a < value):
                raise ValueError(f"Constraint actual:{a} < expected:{value} not met!")

        operation, value = tup

        if operation == "==":
            return equals
        elif operation == ">=":
            return greater_or_equals_than
        elif operation == "<":
            return less_than


class TypeChecker:
    def __init__(self, function):
        self._function = function
        self._return_checker = None
        self._return_constraints = tuple()
        self._parameter_checkers = dict()

    @property
    def __name__(self):
        return self._function.__name__

    @property
    def __doc__(self):
        return self._function.__doc__

    def __call__(self, *args, **kwargs):
        for key, value in signature(self._function).bind(*args, **kwargs).arguments.items():
            if key in self._parameter_checkers:
                self._parameter_checkers[key](value)

        value = self._function(*args, **kwargs)

        if self._return_checker is not None:
            self._return_checker(value)

            for constraint in self._return_constraints:
                constraint(value)

        return value

    def set_return_checker(self, return_checker):
        if self._return_checker is not None:
            raise ValueError(f"Function '{self.__name__}' can only have one return type checker.")
        self._return_checker = return_checker

    def set_return_constraints(self, return_constraints):
        self._return_constraints = tuple(map(Constraint.from_tuple, return_constraints))

    def add_parameter_checker(self, key, parameter_checker):
        self._parameter_checkers[key] = parameter_checker


def returns(return_type: type, constraints: tuple = ()):
    def wrapper(func):
        def return_checker(value):
            if type(value) != return_type:
                raise TypeError(f"Expected '{func.__name__}' to return object of type '{return_type.__name__}',"
                                f" but got '{type(value).__name__}'!")

        if not hasattr(func, "__type_checker__"):
            type_checker = TypeChecker(func)
            setattr(func, "__type_checker__", type_checker)
            func.__call__ = type_checker.__call__

        type_checker = getattr(func, "__type_checker__")

        type_checker.set_return_checker(return_checker)
        type_checker.set_return_constraints(constraints)

        return func

    return wrapper


@returns(int, constraints=((">=", 0), ("<", 100)))
def foo(a, b=-1, *args) -> int:
    """
    Some demo function.

    :param a: first arg
    :param b: second arg
    :param args: more args
    :return: sum of all args
    """
    return a + b * sum(args)


print(foo(3, 4, 2, 3))
print(foo.__call__)
