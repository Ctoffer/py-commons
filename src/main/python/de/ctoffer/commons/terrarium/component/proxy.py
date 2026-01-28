from typing import Callable, Any

from commons.terrarium.component.descriptor import ComponentDescriptor


class ComponentProxy:
    def __init__[T](
            self,
            name: str,
            type_: type[T],
            dependencies: list[ComponentDescriptor],
            initializer: Callable[[], T],
            primary: bool = False,
    ):
        self._name = name
        self._type_ = type_
        self._dependencies = dependencies
        self._primary = primary
        self._initializer = initializer
        self._instance = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def type_(self) -> type[Any]:
        return self._type_

    @property
    def dependencies(self) -> list[ComponentDescriptor]:
        return self._dependencies

    @property
    def primary(self) -> bool:
        return self._primary

    def initialize(self) -> 'ComponentProxy':
        if self._instance is None:
            self._instance = self._initializer()

        return self._instance

    @property
    def instance(self):
        return self._instance