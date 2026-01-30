import custom_components
from commons.terrarium import Terrarium
from custom_components.non_components import MyClass


def main(foo_as_function: MyClass):
    print("EXECUTE MAIN")
    print(foo_as_function.my_argument)


if __name__ == '__main__':
    Terrarium.start(packages=(custom_components,), main=main)