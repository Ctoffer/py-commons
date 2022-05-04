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


def _type_to_parser(type_hint: Any, frozen: bool = False) -> Parameter:
    if isinstance(type_hint, Parameter):
        return type_hint
    elif type_hint in (int, float, bool, str):
        return Primitive(type_hint)
    elif get_origin(type_hint) is AbcSequence:
        return Container(type_hint, frozen=frozen)
    elif is_dataclass(type_hint):
        return Unit(type_hint, frozen=frozen)
    else:
        raise ValueError(f"Unknown type_hint '{type_hint}'.")


class Unit(Parameter):
    def __init__(self, type_hint, non_null: bool = True, optional: bool = False, frozen=False):
        self._type_hint = _ensure_init(type_hint, frozen=frozen)
        self._non_null = non_null
        super().__init__(optional=optional, empty=None)

    def __call__(self, unit: dict):
        if unit is None and self._non_null:
            raise ValueError("Non-null constraint violated.")

        return self._type_hint(**unit)


def _ensure_init(type_hint, frozen=False):
    def __setattr__(self, name, value):
        raise AttributeError(
            f"Can not set field '{name}' "
            f"to value '{value}' "
            f"on {type(self).__name__}@{hex(id(self))} "
            f"since Config objects are frozen."
        )

    if not hasattr(type_hint, "__auto_configured_init__"):
        # FIXME (Christopher): super_annotations is empty, this might lead to conflicts if the dataclass has parents
        setattr(type_hint, "__init__", _create_init(type_hint.__annotations__, dict(), frozen=frozen))
        setattr(type_hint, "__auto_configured_init__", True)

        if frozen:
            setattr(type_hint, "__setattr__", __setattr__)

    return type_hint


def _create_init(annotations: dict, super_annotations: dict, frozen: bool = False) -> Callable[[Any, dict], None]:
    mappers = {key: _type_to_parser(value, frozen=frozen) for key, value in annotations.items()}

    def __init__(self, **kwargs):
        if super_annotations:
            super(type(self), self).__init__(
                **{key: value for key, value in kwargs.items() if key in super_annotations}
            )

        kwargs = {key: value for key, value in kwargs.items() if key in annotations}
        used_keys = set(kwargs.keys())
        properties = dict()

        for key, mapper in mappers.items():
            if mapper.optional and key not in kwargs:
                value = mapper.empty
                properties[key] = value
            elif not mapper.optional and key not in kwargs:
                raise ValueError(f"Mandatory attribute '{key}' is missing.")
            else:
                used_keys.remove(key)
                value = mapper(kwargs[key])
                properties[key] = value

        if used_keys:
            # TODO (Christopher): Use a logger instead.
            print(f"[WARNING] During initialization of {type(self)} configured properties {used_keys} were not used.")

        object.__setattr__(self, "_key", properties)
        for key, value in properties.items():
            object.__setattr__(self, key, value)

    return __init__


def extend_dict(d1: dict, d2: dict) -> None:
    for key, value in d2.items():
        if key not in d1:
            d1[key] = value


def config(file, *path, as_singleton=True, frozen=False):
    hash_code_proto = 0

    def resolve_path_segment(path_segment: str, args: tuple, kwargs: dict) -> str:
        indices = re.findall(r'[(\d+)]', path_segment)
        indices = [int(index) for index in indices]
        for index in indices:
            path_segment = path_segment.replace(f"[{index}]", f"{args[index]}")

        keys = re.findall(r'{(.*)}', path_segment)
        for key in keys:
            path_segment = path_segment.replace(f"{{{key}}}", f"{kwargs[key]}")

        return path_segment

    def resolve_path(some_path: list, args: tuple, kwargs: dict):
        complete_path = [resolve_path_segment(segment, args, kwargs) for segment in some_path]
        complete_path[-1] = complete_path[-1] + ".yaml"
        return complete_path

    def handle_superclasses(cls, complete_path: list, attributes: dict, annotations: dict, args: tuple, kwargs: dict):
        super_classes = cls.mro()
        nested_resource_path = complete_path[:-1]
        number_of_super_classes = 0

        while super_classes[1] != object:
            number_of_super_classes += 1
            if "..parent" not in attributes:
                raise ValueError(
                    "No parent configuration found. "
                    "Use '..parent' to specify a path relative to your configuration."
                )

            for elem in attributes["..parent"].split("/"):
                if elem == "..":
                    del nested_resource_path[-1]
                else:
                    nested_resource_path.append(elem)

            del attributes["..parent"]

            if "..parent" in attributes and super_classes[2] == object:
                raise ValueError(f"Missing parent class for configuration '{''.join(nested_resource_path)}'.")

            nested_resource_path = resolve_path(nested_resource_path, args, kwargs)

            extend_dict(annotations, super_classes[1].__annotations__)
            extend_dict(attributes, load_resource(*nested_resource_path))

            del super_classes[0]
            nested_resource_path = nested_resource_path[:-1]

        return number_of_super_classes

    def enhance_type(cls):
        original_setattr = cls.__setattr__

        nonlocal hash_code_proto
        hash_code = hash_code_proto
        hash_code_proto += 1

        def __init__(self, *args, **kwargs):
            if as_singleton and (args or kwargs):
                raise ValueError("A singleton does not support dynamic paths")

            complete_path = resolve_path([file] + list(path), args, kwargs)
            attributes = load_resource(*complete_path)
            annotations = cls.__annotations__
            if 'instance' in annotations and annotations['instance'] in str(cls):
                del annotations['instance']

            old_annotations = dict(annotations)
            number_of_super_classes = handle_superclasses(cls, complete_path, attributes, annotations, args, kwargs)
            super_annotations = {key: value for key, value in annotations.items() if key not in old_annotations}
            annotations = old_annotations

            initialize = _create_init(annotations, super_annotations, frozen=frozen)
            initialize(self, **attributes)

        def __setattr__(self, name, value):
            if frozen:
                raise AttributeError(
                    f"Can not set field '{name}' "
                    f"to value '{value}' "
                    f"on {type(self).__name__}@{hex(id(self))} "
                    f"since Config objects are frozen."
                )
            else:
                original_setattr(self, name, value)

        def __hash__(self) -> int:
            return hash_code

        def __eq__(self, other: Any) -> bool:
            if isinstance(other, type(self)):
                result_flag = self._key.items() == other._key.items()
            else:
                result_flag = False

            return result_flag

        cls.__init__ = __init__
        cls.__setattr__ = __setattr__

        if frozen:
            cls.__hash__ = __hash__
            cls.__eq__ = __eq__

        if as_singleton:
            result = singleton(cls)
        else:
            result = cls

        return result

    return enhance_type
