import custom_components
from commons.terrarium import Terrarium, component
from commons.terrarium.component.lifecycle_hook import EntryPoint
from custom_components.xxx import MyClass


@component
class TheMain(EntryPoint):
    foo_as_function: MyClass

    def main(self):
        print("EXECUTE MAIN")
        print(self.foo_as_function.my_argument)

if __name__ == '__main__':
    with Terrarium(packages=(custom_components,)) as terra:
        my_class = terra[EntryPoint]
        my_class.main()