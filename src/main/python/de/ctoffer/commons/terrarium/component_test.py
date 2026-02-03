from dataclasses import dataclass

import custom_components
from commons.terrarium import Terrarium
from commons.terrarium.component.auto_configuration import auto_configuration
from commons.terrarium.core_components.environment import Environment
from custom_components.non_components import MyClass


@auto_configuration(path="partial_config.yml")
@dataclass
class PartialAttribute1Config:
    language: str
    location: str


def main(foo_as_function: MyClass, environment: Environment):
    print("EXECUTE MAIN")
    print(foo_as_function.my_argument)
    print(environment.active_profiles)

    instance = terra[PartialAttribute1Config]
    print(instance)


if __name__ == '__main__':
    Terrarium.start(packages=(custom_components,), main=main)