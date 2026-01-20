import dataclasses
import logging
from abc import ABCMeta, abstractmethod
from dataclasses import is_dataclass, dataclass
from pathlib import Path
from types import UnionType
from typing import Any, KeysView, get_origin, get_args

from typing import TypeVar, Generic

log = logging.getLogger(__name__)
T = TypeVar('T')


@dataclass(frozen=True)
class ConversionContext(Generic[T]):
    source_file: Path
    field_name: str
    canonical_field_name: str
    target_type: type[T]
    strict: bool = False


class FieldConverter(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    def accepts_target_type(self, type_: type[T]) -> bool:
        pass

    @abstractmethod
    def __call__(self, value: Any, context: ConversionContext) -> T:
        pass

    @staticmethod
    def _create_error_message(context: ConversionContext, message: str) -> str:
        return f"file='{context.source_file}' field={context.canonical_field_name} target_type={context.target_type} message='{message}'"


class DataclassFieldConverter(FieldConverter[T]):
    def accepts_target_type(self, type_: type[T]) -> bool:
        return is_dataclass(type_)

    def __call__(self, value: Any, context: ConversionContext) -> T:
        if not isinstance(value, dict):
            message = FieldConverter._create_error_message(
                context,
                f"Expected type dict, but is '{type(value)}"
            )
            raise ValueError(message)

        return DataclassFieldConverter._resolve_dataclass(value, context)

    @staticmethod
    def _resolve_dataclass[T](
            dictionary: dict[str, Any],
            context: ConversionContext
    ) -> T:
        type_: type[T] = context.target_type
        parameter_name: str = context.field_name
        strict = context.strict

        annotations = type_.__annotations__
        defaults = {key: getattr(type_, key) for key in annotations if hasattr(type_, key)}
        kwargs = dict()

        DataclassFieldConverter._validate_keys(
            parameter_name,
            annotations.keys(),
            dictionary.keys(),
            strict
        )

        for key in annotations:
            field_type = annotations[key]

            field_context = ConversionContext(
                source_file=context.source_file,
                field_name=key,
                canonical_field_name=(parameter_name + "." if parameter_name != '<root>' else "") + key,
                target_type=field_type,
                strict=strict,
            )

            if key in dictionary:
                value = dictionary[key]

                # FIXME: Partial data loading - currently only WHOLE instances can overwrite the default

                if dataclasses.is_dataclass(field_context.target_type):
                    default_dict = defaults.get(key)
                    default_dict = {} if default_dict is None else dataclasses.asdict(default_dict)
                    default_dict.update(value)
                    value = default_dict

                from commons.typed_config.converter_registry import ConverterRegistry
                value = ConverterRegistry()(value, field_context)

            elif key in defaults:
                value = defaults[key]
            else:
                raise ValueError(f"Field '{key}' of type '{type_}' is required!")

            if not isinstance(value, field_type):
                raise ValueError(f"Field '{key}' of type '{field_type}' is required, but found type '{type(value)}'")
            kwargs[key] = value

        return type_(**kwargs)

    @staticmethod
    def _validate_keys(
            parameter_name: str,
            expected_keys: KeysView,
            actual_keys: KeysView,
            strict: bool = False
    ):
        unknown_keys = actual_keys - expected_keys
        if unknown_keys:
            message = f"key='{parameter_name}' unmatched_attributes='{unknown_keys}'"

            if strict:
                log.error(message)
                raise ValueError(f"There are unknown keys in the configuration at '{parameter_name}'")
            else:
                log.warning(message)


class PathFieldConverter(FieldConverter[Path]):
    def accepts_target_type(self, type_: type[Path]) -> bool:
        return compliant_type_check(type_, Path)

    def __call__(self, value: Any, context: ConversionContext) -> Path | None:
        if value is None:
            return None

        if not (isinstance(value, str) or isinstance(value, Path)):
            message = FieldConverter._create_error_message(
                context,
                f"Expected type str or Path, but is '{type(value)}"
            )
            raise ValueError(message)

        return Path(value)

def compliant_type_check(
        tp: Any,
        type_: type[T]
):
    origin = get_origin(tp)

    # PEP 604 unions: str | None
    if origin is UnionType:
        return all(
            isinstance(arg, type) and issubclass(arg, type_)
            for arg in get_args(tp)
            if arg is not type(None)
        )

    if isinstance(tp, type):
        return issubclass(tp, type_)

    return False

TrivialType = int | float | bool | str

class TrivialFieldConverter(FieldConverter[TrivialType]):
    def accepts_target_type(self, type_: type[TrivialType]) -> bool:
        return any(compliant_type_check(type_, t) for t in get_args(TrivialType))

    def __call__(self, value: Any, context: ConversionContext) -> TrivialType | None:
        if value is None:
            return None

        if type(value) not in (int, float, bool, str):
            message = FieldConverter._create_error_message(
                context,
                f"Expected type in (int, float, bool, str), but is '{type(value)}"
            )
            raise ValueError(message)
        return value
