from pathlib import Path
from typing import Callable

from commons.config.typed_config import load_config
from commons.terrarium import TerrariumComponentRegistry, proxy_of_type, to_lower_snake_case, ComponentDescriptorFactory
from commons.terrarium.component.proxy import ComponentProxy
from commons.terrarium.core_components.environment import Environment


def auto_configuration(
        path: str | Path
) -> Callable:
    def wrapper[T](type_definition: type[T]) -> T:
        def init() -> T:
            environment = registry[Environment]
            profile = environment.profile

            config = load_config(
                path=path.format(profile=profile),
                type_=type_definition,
                strict=True
            )
            return config

        registry = TerrariumComponentRegistry()
        registry += ComponentProxy(
            name=to_lower_snake_case(type_definition.__name__),
            type_=type_definition,
            initializer=init,
            dependencies=[ComponentDescriptorFactory.full(proxy_of_type(Environment, "environment", False)),],
            primary=False
        )

        return type_definition

    return wrapper
