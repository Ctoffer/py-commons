from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Callable

from commons.config.typed_config import load_config
from commons.terrarium import Terrarium


def auto_configuration(
        path: str | Path
) -> Callable:
    @wraps
    def wrapper[T](type_definition: type[T]) -> T:
        config = load_config(
            path=path,
            type_=type_definition,
            strict=True
        )

        return config

    return wrapper


@auto_configuration(path="partial_config.yml")
@dataclass
class PartialAttribute1Config:
    language: str
    location: str


with Terrarium(packages=()) as terra:
    instance = terra[PartialAttribute1Config]
    print(instance)