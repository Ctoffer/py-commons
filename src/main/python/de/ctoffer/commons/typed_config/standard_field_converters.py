import dataclasses
import datetime
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
        target_type: Any,
        requested_type: type[T]
):
    origin = get_origin(target_type)

    # PEP 604 unions: str | None
    if origin is UnionType:
        return all(
            isinstance(arg, type) and issubclass(arg, requested_type)
            for arg in get_args(target_type)
            if arg is not type(None)
        )

    if isinstance(target_type, type):
        return issubclass(target_type, requested_type)

    return False


TrivialType = int | float | bool | str | Any


class TrivialFieldConverter(FieldConverter[TrivialType]):
    def accepts_target_type(self, type_: type[TrivialType]) -> bool:
        return any(compliant_type_check(type_, t) for t in get_args(TrivialType))

    def __call__(self, value: Any, context: ConversionContext) -> TrivialType | None:
        if value is None:
            return None

        allowed_types = get_args(TrivialType)
        if type(value) not in allowed_types:
            message = FieldConverter._create_error_message(
                context,
                f"Expected type in {allowed_types}, but is '{type(value)}"
            )
            raise ValueError(message)
        return value


class ListFieldConverter(FieldConverter[list[T]]):
    def accepts_target_type(self, type_: type[T]) -> bool:
        return type_ is list or get_origin(type_) is list

    def __call__(self, value: Any, context: ConversionContext) -> list[T] | None:
        tp = context.target_type
        if get_origin(tp) is list:
            (elem_type,) = get_args(tp)
        else:
            elem_type = Any

        from commons.typed_config.converter_registry import ConverterRegistry
        registry = ConverterRegistry()

        if elem_type in (Any, object):
            return value
        else:
            return [
                registry(item, ListFieldConverter._copy_context(i, elem_type, context))
                for i, item in enumerate(value)
            ]

    @staticmethod
    def _copy_context[T](i: int, target_type: type[T], context: ConversionContext) -> ConversionContext:
        parent_name = context.canonical_field_name
        field_name = f"[{i}]"

        return ConversionContext(
            source_file=context.source_file,
            target_type=target_type,
            strict=context.strict,
            field_name=field_name,
            canonical_field_name=(parent_name + "." if parent_name != '<root>' else "") + field_name
        )


class DictFieldConverter(FieldConverter[dict[str, T]]):
    def accepts_target_type(self, type_: type[T]) -> bool:
        return type_ is dict or get_origin(type_) is dict

    def __call__(self, value: Any, context: ConversionContext) -> dict[str, T] | None:
        tp = context.target_type
        if get_origin(tp) is dict:
            key_type, value_type = get_args(tp)
        else:
            key_type = str
            value_type = Any

        if key_type != str:
            message = FieldConverter._create_error_message(
                context,
                f'Key type must be str, but is {key_type}'
            )
            raise ValueError(message)

        from commons.typed_config.converter_registry import ConverterRegistry
        registry = ConverterRegistry()

        if value_type in (Any, object):
            return value
        else:
            return {
                key: registry(val, DictFieldConverter._copy_context(key, value_type, context))
                for key, val in value.items()
            }

    @staticmethod
    def _copy_context[T](field_name: str, target_type: type[T], context: ConversionContext) -> ConversionContext:
        parent_name = context.canonical_field_name

        return ConversionContext(
            source_file=context.source_file,
            target_type=target_type,
            strict=context.strict,
            field_name=field_name,
            canonical_field_name=(parent_name + "." if parent_name != '<root>' else "") + field_name
        )


DateTimeDescriptor = dict[str, Any] | str
DateTimeType = datetime.datetime | datetime.date | datetime.time


class DatetimeFieldConverter(FieldConverter[DateTimeType]):
    def accepts_target_type(
            self,
            type_: type[DateTimeType]
    ) -> bool:
        if get_origin(type_) is UnionType:
            return any(
                compliant_type_check(target, requested_type)
                for requested_type in get_args(type_)
                for target in get_args(DateTimeType)
            )
        else:
            return any(
                compliant_type_check(target, type_)
                for target in  get_args(DateTimeType)
            )

    def __call__(
            self,
            value: Any,
            context: ConversionContext
    ) -> DateTimeType | None:
        target_type = context.target_type

        source_type = type(value)
        if source_type is None:
            return None

        if get_origin(target_type) is UnionType:
            raise ValueError("The typing must be precisely one of the datetime types and not a UnionType.")

        if issubclass(target_type, datetime.datetime):
            return DatetimeFieldConverter._parse_datetime(value, context)
        elif issubclass(target_type, datetime.date):
            return DatetimeFieldConverter._parse_date(value, context)
        elif issubclass(target_type, datetime.time):
            return DatetimeFieldConverter._parse_time(value, context)
        else:
            message = FieldConverter._create_error_message(
                context,
                f"Type '{target_type}' not supported!"
            )
            raise ValueError(message)

    @staticmethod
    def _parse_datetime(
            value: DateTimeDescriptor,
            context: ConversionContext
    ) -> datetime.datetime:
        source_type = type(value)
        result: datetime.datetime

        if source_type == dict:
            result = datetime.datetime(
                year=value['year'],
                month=value['month'],
                day=value['day'],
                hour=value.get('hour', 0),
                minute=value.get('minute', 0),
                second=value.get('second', 0),
                microsecond=value.get('microsecond', 0),
            )
        elif source_type == str:
            result = datetime.datetime.fromisoformat(value)
        elif source_type == datetime.datetime:
            result = value
        else:
            raise DatetimeFieldConverter._source_type_error(
                source_type,
                datetime.datetime,
                context
            )

        return result

    @staticmethod
    def _source_type_error(
            source_type: type[Any],
            target_type: type[Any],
            context: ConversionContext
    ):
        message = FieldConverter._create_error_message(
            context,
            f"Source type '{source_type}' can't be converted to '{target_type}'!"
        )
        return ValueError(message)

    @staticmethod
    def _parse_date(
            value: DateTimeDescriptor,
            context: ConversionContext
    ) -> datetime.date:
        source_type = type(value)
        result: datetime.date

        if source_type == dict:
            result = datetime.date(
                year=value['year'],
                month=value['month'],
                day=value['day']
            )
        elif source_type == str:
            result = datetime.date.fromisoformat(value)
        else:
            raise DatetimeFieldConverter._source_type_error(
                source_type,
                datetime.date,
                context
            )

        return result

    @staticmethod
    def _parse_time(
            value: DateTimeDescriptor,
            context: ConversionContext
    ) -> datetime.time:
        source_type = type(value)
        result: datetime.time

        if source_type == dict:
            result = datetime.time(
                hour=value.get('hour', 0),
                minute=value.get('minute', 0),
                second=value.get('second', 0),
                microsecond=value.get('microsecond', 0)
            )
        elif source_type == str:
            result = datetime.time.fromisoformat(value)
        else:
            raise DatetimeFieldConverter._source_type_error(
                source_type,
                datetime.time,
                context
            )

        return result