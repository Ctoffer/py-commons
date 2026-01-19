import dataclasses
import logging
from collections.abc import KeysView
from pathlib import Path
from typing import Any

import yaml

log = logging.getLogger(__name__)

def load_config[T](
        path: str | Path,
        type_: type[T],
        strict: bool = False
) -> T:
    """
    Loads a configuration YAML file.

    The loaded file is converted in the specified type. The specified type must be a dataclass.
    :param path: The path of the configuration file.
    :param type_: The type representing the contents of the configuration file. Must be a dataclass.
    :param strict: Flag to determine if extra attributes in the configuration file should be considered a warning or an error.
    :return: The loaded dataclass representing the requested configuration.
    """
    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    if not dataclasses.is_dataclass(type_):
        raise TypeError(f"Configuration type '{type_}' is not a dataclass.")

    try:
        configuration_raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        result = _resolve_dataclass(
            dictionary=configuration_raw,
            type_=type_,
            strict=strict
        )
        return result

    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in {path}! ({exc})")


def _resolve_dataclass[T](
        dictionary: dict[str, Any],
        type_: type[T],
        strict: bool = False,
        parameter_name: str = ""
) -> T:
    """
    Creates an instance of a dataclass based on a given dictionary.

    Some of the attributes of the dictionary might be themselves dataclass instances which are then parsed
    recursively.
    :param dictionary: Dictionary containing field names and values.
    :param type_: The requested type of this dataclass.
    :param strict: Flag determines if unknown keys are considered a warning or an error.
    :param parameter_name: Name of the parameter in the configuration. Nested attributes are designated by a dot-joined name.
    :return:
    """
    annotations = type_.__annotations__
    defaults = {key: getattr(type_, key) for key in annotations if hasattr(type_, key)}
    kwargs = dict()

    _validate_keys(
        parameter_name,
        annotations.keys(),
        dictionary.keys(),
        strict
    )

    for key in annotations:
        field_type = annotations[key]
        if key in dictionary:
            value = dictionary[key]

            # FIXME: Partial data loading - currently only WHOLE instances can overwrite the default
            if dataclasses.is_dataclass(field_type):
                value = _resolve_dataclass(
                    value,
                    field_type,
                    strict,
                    (parameter_name + "." if parameter_name else "") + key
                )
            # TODO custom handling for data types etc.

        elif key in defaults:
            value = defaults[key]
        else:
            raise ValueError(f"Field '{key}' of type '{type_}' is required!")

        if not isinstance(value, field_type):
            raise ValueError(f"Field '{key}' of type '{field_type}' is required, but found type '{type(value)}'")
        kwargs[key] = value

    return type_(**kwargs)


def _validate_keys(
        parameter_name: str,
        expected_keys: KeysView,
        actual_keys: KeysView,
        strict: bool = False
):
    """
    Validates the actual keys do not contain keys specified by the expected keys.

    :param parameter_name: The name of the current field path.
    :param expected_keys: The expected keys.
    :param actual_keys: The actual keys.
    :param strict: Flag determines if unknown keys are considered a warning or an error.
    :raises ValueError: If there is a key not defined by expected_keys and strict=true.
    """
    unknown_keys = actual_keys - expected_keys
    if unknown_keys:
        message = f"key='{parameter_name}' unmatched_attributes='{unknown_keys}'"

        if strict:
            log.error(message)
            raise ValueError(f"There are unknown keys in the configuration at '{parameter_name}'")
        else:
            log.warning(message)
