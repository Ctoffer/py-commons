from dataclasses import dataclass

from commons.config.typed_config import load_config


@dataclass(frozen=True)
class ConfigAttribute:
    host: str
    port: int = 8080
    path: str | None = None


@dataclass
class NestedConfig:
    attribute_1 : ConfigAttribute
    attribute_2 : ConfigAttribute = ConfigAttribute(host="my_host")


nested_config = load_config("sample_config.yml", type_=NestedConfig)
print(nested_config)