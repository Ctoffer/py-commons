from pathlib import Path
from typing import Callable

from commons.config.typed_config import load_config
from commons.terrarium import TerrariumComponentRegistry
from commons.terrarium.component.registry import proxy_of_instance


def auto_configuration(
        path: str | Path
) -> Callable:
    def wrapper[T](type_definition: type[T]) -> T:
        config = load_config(
            path=path,
            type_=type_definition,
            strict=True
        )
        print("register via auto_configuration")
        registry = TerrariumComponentRegistry()
        registry += proxy_of_instance(config)

        return type_definition

    return wrapper


