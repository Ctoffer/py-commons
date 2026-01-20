from dataclasses import dataclass
from pathlib import Path

from commons.typed_config import load_config


@dataclass(frozen=True)
class ConfigAttribute:
    host: str
    port: int = 8080
    path: Path | None = None
    extra_attribute: str | None = None


@dataclass
class NestedConfig:
    attribute_1 : ConfigAttribute
    attribute_2 : ConfigAttribute = ConfigAttribute(host="my_host")

@dataclass
class Pair:
    x: int
    y: int

# nested_config = load_config("sample_config.yml", type_=NestedConfig)
# print(nested_config)

pair_data = load_config("pairs.yml", type_=list[Pair])
print(len(pair_data), pair_data, pair_data[4].y)