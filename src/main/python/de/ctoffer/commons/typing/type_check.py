from inspect import signature


class Constraint:
    @classmethod
    def create(cls, value):

        if type(value) == tuple:
            operation, value = value
            result = Constraint._from_tuple(operation, value)
        elif type(value) == str:
            result = Constraint._from_string(value)
        else:
            raise TypeError(f"Expected tuple or str, but got '{value}'")

        return result

    @staticmethod
    def _from_tuple(operation, value):
        def equals(a):
            if not (value == a):
                raise ValueError(f"Constraint actual:{a} == expected:{value} not met!")

        def greater_or_equals_than(a):
            if not (a >= value):
                raise ValueError(f"Constraint actual:{a} >= expected:{value} not met!")

        def less_than(a):
            if not (a < value):
                raise ValueError(f"Constraint actual:{a} < expected:{value} not met!")

        if operation == "==":
            return equals
        elif operation == ">=":
            return greater_or_equals_than
        elif operation == "<":
            return less_than

    @staticmethod
    def _from_string(value):
        def positive(a):
            if not (a > 0):
                raise ValueError(f"Constraint positive with value {a} not met!")

        def negative(a):
            if not (a < 0):
                raise ValueError(f"Constraint negative with value {a} not met!")

        def non_positive(a):
            if a > 0:
                raise ValueError(f"Constraint non-positive with value {a} not met!")

        def non_negative(a):
            if a < 0:
                raise ValueError(f"Constraint non-negative with value {a} not met!")

        def non_none(a):
            if a is None:
                raise ValueError(f"Constraint non-none not met!")

        def non_empty(a):
            if a is None or (hasattr(a, "len") and len(a) == 0):
                raise ValueError(f"Constraint non-empty sequence with value {a} is not met!")

        lookup = {
            "positive": positive,
            "negative": negative,
            "non-positive": non_positive,
            "non-negative": non_negative,
            "non_none": non_none,
            "non_empty": non_empty
        }

        return lookup[value]


class TypeChecker:
    def __init__(self, function):
        self._function = function
        self._return_checker = None
        self._return_constraints = tuple()
        self._parameter_checkers = dict()
        self._parameter_constraints = dict()

    @property
    def __name__(self):
        return self._function.__name__

    @property
    def __doc__(self):
        return self._function.__doc__

    def __call__(self, *args, **kwargs):
        for name, value in signature(self._function).bind(*args, **kwargs).arguments.items():
            if name in self._parameter_checkers:
                self._parameter_checkers[name](value)

            if name in self._parameter_constraints:
                for constraint in self._parameter_constraints[name]:
                    constraint(value)

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
        self._return_constraints = tuple(map(Constraint.create, return_constraints))

    def add_parameter_checker(self, key, parameter_checker):
        self._parameter_checkers[key] = parameter_checker

    def add_paramater_constraints(self, key, constraints):
        self._parameter_constraints[key] = tuple(map(Constraint.create, constraints))


def retrieves(name, param_type: type, constraints: tuple = ()):
    def wrapper(func):
        def param_checker(value):
            if type(value) != param_type:
                raise TypeError(
                    f"Expected '{func.__name__}' to retrieve object of type '{param_type.__name__}'"
                    f" for parameter '{name}', but got '{type(value).__name__}'!"
                )

        if type(func) != TypeChecker:
            type_checker = TypeChecker(func)
            setattr(func, "__type_checker__", type_checker)
        else:
            type_checker = func

        type_checker.add_parameter_checker(name, param_checker)
        type_checker.add_paramater_constraints(name, constraints)

        return type_checker

    return wrapper


def returns(return_type: type, constraints: tuple = ()):
    def wrapper(func):
        def return_checker(value):
            if type(value) != return_type:
                raise TypeError(f"Expected '{func.__name__}' to return object of type '{return_type.__name__}',"
                                f" but got '{type(value).__name__}'!")

        if type(func) != TypeChecker:
            type_checker = TypeChecker(func)
            setattr(func, "__type_checker__", type_checker)
        else:
            type_checker = func

        type_checker.set_return_checker(return_checker)
        type_checker.set_return_constraints(constraints)

        return func

    return wrapper


@retrieves("a", int, constraints=("positive",))
@retrieves("b", int, constraints=("non-negative", ))
@returns(int, constraints=("non-negative", ("<", 100)))
def foo(a, b=-1, *args) -> int:
    """
    Some demo function.

    :param a: first arg
    :param b: second arg
    :param args: more args
    :return: sum of all args
    """
    return a + b * sum(args)


print(foo(3, -2, 2, 3))
