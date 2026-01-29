import custom_components
from commons.terrarium import Terrarium, component
from commons.terrarium.component.lifecycle_hook import EntryPoint
from custom_components.non_components import MyClass


@component
class TheMain(EntryPoint):
    foo_as_function: MyClass

    def main(self):
        print("EXECUTE MAIN")
        print(self.foo_as_function.my_argument)

if __name__ == '__main__':
    Terrarium.run(packages=(custom_components, ))
