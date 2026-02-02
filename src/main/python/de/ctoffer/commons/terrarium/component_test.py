import custom_components
from commons.terrarium import Terrarium
from commons.terrarium.core_components.environment import Environment
from custom_components.non_components import MyClass


def main(foo_as_function: MyClass, environment: Environment):
    print("EXECUTE MAIN")
    print(foo_as_function.my_argument)
    print(environment.active_profiles)


if __name__ == '__main__':
    Terrarium.start(packages=(custom_components,), main=main)