from pathlib import Path

import yaml

from commons.typed_config.converter_registry import ConverterRegistry
from commons.typed_config.standard_field_converters import ConversionContext


def load_config[T](
        path: str | Path,
        type_: type[T],
        strict: bool = False
) -> T:
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
