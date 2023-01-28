import abc
import logging
import sys
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from functools import wraps, partial, update_wrapper
from inspect import signature
from typing import TypeVar, Callable, Generic, List, Any, Union, Type, Dict, Tuple

from commons.util.singleton import Singleton

S = TypeVar('S')
R = TypeVar('R')
E = TypeVar('E', bound=Exception)


class LoggerCache(metaclass=Singleton):
    def __init__(self):
        self._cache = dict()
        self._logger_factory = logging.getLogger

    @property
    def logger_factory(
            self
    ) -> Callable[[str], logging.Logger]:
        return self._logger_factory

    @logger_factory.setter
    def logger_factory(
            self,
            logger_factory: Callable[[str], logging.Logger]
    ):
        self._logger_factory = logger_factory
        # TODO (Ctoffer): Maybe use wrapper around logger to dynamically change logging behaviour after setting?

    def __getitem__(self, item):
        if item not in self._cache:
            logger = self._logger_factory(item)
            self._cache[item] = logger
            logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            stream_handler = logging.StreamHandler(stream=sys.stdout)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

        return self._cache[item]


@dataclass
class FunctionParameters:
    args: List[Any]
    kwargs: Dict[str, Any]


class LogLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


class FunctionLifeCycle(Enum):
    Entry = 0
    Exit = 1
    Exception = 2


def for_each(elements: List[S], action: Callable[[S], None]):
    for i in elements:
        action(i)


def apply_to(
        callables: List[Callable[[S], R]],
        value: S,
        until: Callable[[R], bool] = lambda o: False
):
    for c in callables:
        if until(c(value)):
            break


class AnalyzableFunction:
    def __init__(self, func):
        update_wrapper(self, func)
        self._original_function = func
        self._all_param_handler = list()
        self._single_param_handler = defaultdict(list)
        self._result_handler = list()
        self._exception_handler = defaultdict(list)

    def add_param_handler(
            self,
            handler: Callable[[FunctionParameters], None]
    ):
        self._all_param_handler.append(handler)

    def add_single_param_handler(
            self,
            param: Union[str, int],
            handler: Callable[[Any], None]
    ):
        self._single_param_handler[param].append(handler)

    def add_result_handler(
            self,
            handler: Callable[[Any], None]
    ):
        self._result_handler.append(handler)

    def add_exception_handler(
            self,
            error_type: Type[E],
            handler: Callable[[E], bool]
    ):
        self._exception_handler[error_type].append(handler)

    def __call__(self, *args, **kwargs):
        try:
            apply_to(self._all_param_handler[::-1], value=FunctionParameters(args=args, kwargs=kwargs))
            arguments = signature(self._original_function).bind(*args, **kwargs).arguments

            for key, handler in list(self._single_param_handler.items())[::-1]:
                apply_to(handler, arguments[key])

            result = self._original_function(*args, **kwargs)
            apply_to(self._result_handler[::-1], value=result)
            return result

        except Exception as e:
            apply_to(self._exception_handler[type(e)][::-1], value=e, until=lambda o: o)
            raise e


def analyzable_function(func: Callable) -> AnalyzableFunction:
    if type(func) is not AnalyzableFunction:
        result = AnalyzableFunction(func)
    else:
        result = func

    return result


def log(
        func=None,
        *,
        level: LogLevel = LogLevel.DEBUG,
        life_cycle: FunctionLifeCycle = FunctionLifeCycle.Entry,
        to_line: Callable[[Union[FunctionParameters, Any, E]], str] = lambda o: str(o),
        error_type: Type[E] = BaseException
):
    if not func:
        return partial(log, level=level, life_cycle=life_cycle, to_line=to_line)

    result = analyzable_function(func)

    logger = LoggerCache()[func.__module__]
    log_function = getattr(logger, level.name.lower())

    if life_cycle == FunctionLifeCycle.Entry:
        add_handler = result.add_param_handler
    elif life_cycle == FunctionLifeCycle.Exit:
        add_handler = result.add_result_handler
    elif life_cycle == FunctionLifeCycle.Exception:
        add_handler = partial(result.add_exception_handler, error_type=error_type)
    else:
        raise ValueError(f"Unsupported lifecycle operation: {life_cycle}")

    add_handler(lambda data: log_function(to_line(data)))

    return result


class Scope(Enum):
    Parameter = 0
    Return = 1


class Check(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __call__(self, value) -> bool:
        raise NotImplementedError

    def __str__(self):
        return str(type(self).__name__)


class NotEmpty(Check):
    def __call__(self, value) -> bool:
        return bool(value)


class StrictTypeChecker(Check):
    def __init__(self, type):
        self._type = type

    def __call__(self, value):
        return type(value) == self._type


StrictTypeCheck = lambda t: lambda: StrictTypeChecker(t)


def constraint(
        func=None,
        *,
        scope: Scope,
        enforce=Union[Check, Callable[[Any], Check], Tuple[Check, ...]],
        applies_to: str = None,
        strict: bool = True
):
    if not func:
        return partial(constraint, scope=scope, enforce=enforce, applies_to=applies_to, strict=strict)

    if type(enforce) != tuple:
        enforce = (enforce,)
    enforce = [enforce_type() for enforce_type in enforce]

    result = analyzable_function(func)
    logger = LoggerCache()[func.__module__]

    logging_prefix = "Result" if applies_to is None else f"Parameter '{applies_to}'"

    def handle_param(value):
        for enforcer in enforce:
            if not enforcer(value):
                text = f"{logging_prefix} does not match constraint '{enforcer}'"

                if strict:
                    raise ValueError(text)
                else:
                    logger.error(text)

    if scope == Scope.Parameter:
        if applies_to is None:
            raise ValueError("Name of the parameter was not provided in 'applies_to'")

        result.add_single_param_handler(param=applies_to, handler=handle_param)

    elif scope == Scope.Return:
        if applies_to is not None:
            raise ValueError("When scope return is selected no 'applies_to' can be provided")

        result.add_result_handler(handler=handle_param)

    return result


def decorator(func=None, *, parameter1="default param1", parameter2="default param2"):
    """Decorator template

    :param func:
    :param parameter1:
    :param parameter2:
    :return:
    """
    print("decorator", func, parameter1, parameter2)

    if not func:
        print("partial")
        return partial(decorator, parameter1=parameter1, parameter2=parameter2)

    @wraps(func)
    def wrapper(*args, **kwargs):
        print("wrapper", f"'{parameter1}'", f"'{parameter2}'", args, kwargs)
        return func(*args, **kwargs)

    return wrapper


@log(
    level=LogLevel.INFO,
    to_line=lambda o: f"First parameter: '{o.kwargs['param1']}', Second parameter: '{o.kwargs['param2']}'"
)
@log(
    level=LogLevel.INFO,
    life_cycle=FunctionLifeCycle.Exit,
    to_line=lambda r: f"result: '{r}'"
)
@log
@constraint(scope=Scope.Parameter, applies_to="param1", enforce=NotEmpty, strict=False)
@constraint(scope=Scope.Parameter, applies_to="param1", enforce=StrictTypeCheck(str), strict=False)
@constraint(scope=Scope.Parameter, applies_to="param2", enforce=(StrictTypeCheck(str), NotEmpty), strict=False)
@constraint(scope=Scope.Return, enforce=(StrictTypeCheck(str), NotEmpty), strict=False)
# @measure_time
def bar(param1, param2="oho"):
    print("Inside bar", param1, param2)
    return param1 + param2


bar(param1="", param2="")