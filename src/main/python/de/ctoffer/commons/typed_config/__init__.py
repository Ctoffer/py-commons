from pathlib import Path

import yaml

from commons.typed_config.converter_registry import ConverterRegistry
from commons.typed_config.standard_field_converters import ConversionContext


def load_config[T](
        path: str | Path,
        type_: type[T],
        strict: bool = False
) -> T:
    """
    Loads a configuration from a YAML file.

    The requested type determines which FieldConverter to use as an entry point.
    There are default field converters for:
    - dataclass
    - datetime.datetime, datetime.date, datetime.time
    - enum
    - list[T]
    - dict[str, T]
    - Path
    - int, float, bool, str and None
    Use precise type-specifications and keep UnionTypes to a minimum for the type detection.
    A UnionType with None should be fine in most cases.
    If a default for a dataclass is given, properties can be overwritten partially by a given configuration.

    Args:
        path: Path to the YAML file.
        type_: The requested type after loading the file.
        strict: If True exceptions are raised during inconsistencies between provided data and the requested class structure.
                   Otherwise, warnings are logged.

    Returns:
        Instance populated with the configured data.
    """
    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    registry = ConverterRegistry()
    context = ConversionContext(
        source_file=path,
        field_name="<root>",
        canonical_field_name="<root>",
        target_type=type_,
        strict=strict
    )

    try:
        configuration_raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        return registry(
            configuration_raw,
            context
        )
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in {path}! ({exc})")
