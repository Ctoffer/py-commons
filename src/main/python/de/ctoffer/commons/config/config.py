import re
from collections.abc import Sequence
from collections.abc import Sequence as AbcSequence
from dataclasses import dataclass, is_dataclass
from typing import Any, Callable, get_origin, get_args

from commons.creational.singleton import singleton
from commons.util.project import load_resource


@dataclass
class Parameter:
    optional: bool = False
    empty: Any = None

    def __call__(self, value):
        raise NotImplementedError


class Primitive(Parameter):
    def __init__(self, type_hint, optional: bool = False, empty: Any = None):
        self._type_hint = type_hint
        super().__init__(optional=optional, empty=empty)

    def __call__(self, value):
        return value


class Container(Parameter):
    __containers = {
        (False, False): list,
        (True, False): tuple,
        (False, True): set,
        (True, True): frozenset
    }

    def __init__(
            self,
            sequence,
            frozen: bool = True,
            unique: bool = False,
            min_size: int = 0,
            max_size: int = None,
            optional: bool = False
    ):
        if get_origin(sequence) is not AbcSequence:
            raise ValueError("A Container can only be created for a Sequence[T]")

        generic_arguments = get_args(sequence)
        if len(generic_arguments) == 0:
            raise ValueError("A container requires a Sequence[T] with defined T.")

        self._elem_type = _type_to_parser(generic_arguments[0])
        self._desired_container = Container.__containers[frozen, unique]
        self._min_size = min_size
        self._max_size = max_size
        super().__init__(optional=optional, empty=self._desired_container())

    def __call__(self, sequence: Sequence):
        if len(sequence) < self._min_size:
            raise ValueError("Not enough elements provided.")
        if self._max_size is not None and self._max_size < len(sequence):
            raise ValueError("Too much elements provided.")

        return self._desired_container(self._elem_type(sequence_element) for sequence_element in sequence)


def _type_to_parser(type_hint: Any) -> Parameter:
    if isinstance(type_hint, Parameter):
        return type_hint
    elif type_hint in (int, float, bool, str):
        return Primitive(type_hint)
    elif get_origin(type_hint) is AbcSequence:
        return Container(type_hint)
    elif is_dataclass(type_hint):
        return Unit(type_hint)
    else:
        raise ValueError(f"Unknown type_hint '{type_hint}'.")


class Unit(Parameter):
    def __init__(self, type_hint, non_null: bool = True, optional: bool = False):
        self._type_hint = _ensure_init(type_hint)
        self._non_null = non_null
        super().__init__(optional=optional, empty=None)

    def __call__(self, unit: dict):
        if unit is None and self._non_null:
            raise ValueError("Non-null constraint violated.")

        return self._type_hint(**unit)


def _ensure_init(type_hint):
    if not hasattr(type_hint, "__auto_configured_init__"):
        type_hint.__init__ = _create_init(type_hint.__annotations__)
        setattr(type_hint, "__auto_configured_init__", True)

    return type_hint


def _create_init(annotations: dict) -> Callable[[Any, dict], None]:
    mappers = {key: _type_to_parser(value) for key, value in annotations.items()}

    def __init__(self, **kwargs):
        used_keys = set(kwargs.keys())

        for key, mapper in mappers.items():
            if mapper.optional and key not in kwargs:
                setattr(self, key, mapper.empty)
            elif not mapper.optional and key not in kwargs:
                raise ValueError(f"Mandatory attribute '{key}' is missing.")
            else:
                used_keys.remove(key)
                setattr(self, key, mapper(kwargs[key]))

        if used_keys:
            # TODO (Christopher): Use a logger instead.
            print(f"[WARNING] During initialization of {type(self)} configured properties {used_keys} were not used.")

    return __init__


def config(file, *path, as_singleton=True):
    def resolve_path_segment(path_segment: str, args: tuple, kwargs: dict) -> str:
        indices = re.findall(r'[(\d+)]', path_segment)
        indices = [int(index) for index in indices]
        for index in indices:
            path_segment = path_segment.replace(f"[{index}]", f"{args[index]}")

        keys = re.findall(r'{(.*)}', path_segment)
        for key in keys:
            path_segment = path_segment.replace(f"{{{key}}}", f"{kwargs[key]}")

        return path_segment

    def enhance_type(cls):
        def __init__(self, *args, **kwargs):
            if as_singleton and (args or kwargs):
                raise ValueError("A singleton does not support dynamic paths")

            complete_path = [file] + list(path)
            complete_path = [resolve_path_segment(segment, args, kwargs) for segment in complete_path]
            complete_path[-1] = complete_path[-1] + ".yaml"
            attributes = load_resource(*complete_path)

            initialize = _create_init(cls.__annotations__)
            initialize(self, **attributes)

        cls.__init__ = __init__
        # TODO (Christopher): Config should modify class to behave like frozen dataclass after init

        if as_singleton:
            result = singleton(cls)
        else:
            result = cls

        return result

    return enhance_type
