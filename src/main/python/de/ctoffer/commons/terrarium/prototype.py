import re
from collections import deque
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from idlelib.window import registry
from typing import Callable, Any
from xml.etree.ElementTree import canonicalize

from typing import get_type_hints, get_args, get_origin

from commons.util.singleton import Singleton


class ProtoType(Enum):
    COMPONENT = 1
    SERVICE = 2
    REPOSITORY = 3


@dataclass(frozen=True)
class ComponentDescriptor:
    type_: type[Any]
    name: str

    def match_score(self, key: 'ComponentDescriptor'):
        score = 0

        if self.type_ == key.type_:
            score += 100
        elif issubclass(key.type_, self.type_):
            score += 50

        if self.name == key.name:
            score += 25

        return score


class ComponentProxy:
    _CACHE: dict[tuple[str, type[Any]], 'ComponentProxy'] = dict()

    @staticmethod
    def of_type[T](type_: type[T], name: str, primary: bool = False) -> 'ComponentProxy':
        if (name, type_) in ComponentProxy._CACHE:
            raise ValueError(f"There is already a component proxy for the type and name: {(type_, name)}")

        annotations = type_.__annotations__
        dependencies = [
            ComponentDescriptor(type_=annotation_type, name=name)
            for name, annotation_type in annotations.items()
        ]

        result = ComponentProxy(
            name=name,
            type_=type_,
            dependencies=dependencies,
            initializer=type_,
            primary=primary
        )
        ComponentProxy._CACHE[(name, type_)] = result
        return result

    @staticmethod
    def of_callable[T](
            obj: Callable[[...], T],
            name: str,
            primary: bool = False
    ) -> 'ComponentProxy':
        type_hints = get_type_hints(obj)
        if not type_hints:
            raise ValueError(f"There is no type hints defined for {obj}")

        if "return" not in type_hints:
            raise ValueError(f"There is no return type hint defined for {obj}")

        return_type = type_hints["return"]
        dependencies = [ComponentDescriptorFactory.of(type_=t, name=name) for name, t in type_hints.items() if name != "return"]

        def init() -> T:
            from prototype import ComponentRegistry

            registry = ComponentRegistry()
            components = {descriptor.name: registry[descriptor] for descriptor in dependencies}
            return obj(**components)

        return ComponentProxy(
            name=name,
            type_=return_type,
            dependencies=dependencies,
            initializer=init,
            primary=primary
        )

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

class ComponentDescriptorFactory:
    @staticmethod
    def full(component_proxy: 'ComponentProxy') -> 'ComponentDescriptor':
        return ComponentDescriptor(
            type_=component_proxy.type_,
            name=component_proxy.name
        )

    @staticmethod
    def of(*, type_: type = None, name: str = None) -> 'ComponentDescriptor':
        return ComponentDescriptor(
            type_=type_,
            name=name
        )


class ComponentRegistry(metaclass=Singleton):
    class State(Enum):
        SCANNING = 1
        INITIALIZING = 2
        INITIALIZED = 3
        POST_CONSTRUCTING = 4
        POST_CONSTRUCTED = 5
        PRE_DESTROYING = 6
        DESTROYED = 5

    _state: 'ComponentRegistry.State'
    _proxies: dict[ComponentDescriptor, ComponentProxy]
    _children: dict[ComponentDescriptor, list[ComponentDescriptor]]
    _init_order: list[ComponentProxy]

    def __init__(self):
        self._state = ComponentRegistry.State.SCANNING
        self._proxies = dict()
        self._children = dict()
        self._init_order = list()

    def __iadd__(
            self,
            component_proxy: ComponentProxy
    ) -> 'ComponentRegistry':
        descriptor = ComponentDescriptorFactory.full(component_proxy)
        self._proxies[descriptor] = component_proxy
        self._children[descriptor] = component_proxy.dependencies
        return self

    def __getitem__(
            self,
            descriptor: ComponentDescriptor
    ) -> Any:
        # direct match
        if descriptor in self._proxies:
            return self._proxies[descriptor].instance

        # try to find best fit
        potential_matches = self._find_closest_matches(descriptor)

        # exact match
        if len(potential_matches) == 1:
            return potential_matches[0]._instance
        elif potential_matches:
            candidates = [candidate for candidate in potential_matches if candidate.primary]

            # one primary component found
            if len(candidates) == 1:
                return candidates[0]._instance
            elif candidates:
                raise ValueError(
                    f"There must be exactly 1 primary, instead found: {candidates}")  # TODO custom exception
            else:
                raise ValueError(f"There must be exactly 1 candidate or a primary, instead found: {potential_matches}")
        else:
            raise ValueError(f"Could not find any component with descriptor: {descriptor}")

    def _find_closest_matches(
            self,
            descriptor: ComponentDescriptor
    ) -> list[ComponentProxy]:
        potential_matches: list[tuple[int, ComponentProxy]] = list()
        for key, value in self._proxies.items():
            score = descriptor.match_score(key)
            if score > 0:
                potential_matches.append((score, value))

        if not potential_matches:
            raise ValueError(f"No candidate found for descriptor {descriptor}")

        potential_matches = sorted(potential_matches, key=lambda x: -x[0])
        max_score = potential_matches[0][0]
        return [candidate for score, candidate in potential_matches if score == max_score]

    @property
    def state(self) -> 'ComponentRegistry.State':
        return self._state

    def initialize_components(self) -> None:
        self._state = ComponentRegistry.State.INITIALIZING
        queue = [(descriptor, list(self._children[descriptor])) for descriptor in self._proxies]
        queue = sorted(queue, key=lambda x: len(x[1]))

        while queue:
            descriptor, children = queue.pop(0)

            if len(children) > 0:
                raise ValueError(f"Can't initialize component '{descriptor}' because of unresolved dependencies: {children}")

            component_proxy: ComponentProxy = self._proxies[descriptor]
            component_proxy.initialize()

            for remaining_descriptor, remaining_children in queue:
                if descriptor in remaining_children:
                    remaining_children.remove(descriptor)


        self._state = ComponentRegistry.State.INITIALIZED

    def post_construct_components(self) -> None:
        for proxy in self._init_order:
            method_name = "__post_construct__"
            if hasattr(proxy, method_name):
                post_construct = getattr(proxy, method_name)
                post_construct()

    def pre_destruct_components(self) -> None:
        for proxy in self._init_order[::-1]:
            method_name = "__pre_destruct__"
            if hasattr(proxy, method_name):
                pre_destruct = getattr(proxy, method_name)
                pre_destruct()


def component[T](
        name: str | Callable[[...], T] | type[T] = None,
        *,
        prototype: ProtoType = ProtoType.COMPONENT,
        primary: bool = False
):
    def decorate(obj: Callable[[...], T] | type[T]):
        normalized_name = to_lower_snake_case(obj.__name__)
        print(f"Decorate: {obj.__name__} normalized_name: {to_lower_snake_case(obj.__name__)})")
        registry = ComponentRegistry()

        if isinstance(obj, type):
            registry += ComponentProxy.of_type(obj, name=normalized_name, primary=primary)
        elif callable(obj):
            registry += ComponentProxy.of_callable(obj, name=normalized_name, primary=primary)
        else:
            raise TypeError

        return obj

    if isinstance(name, type):
        return decorate(name)
    elif callable(name):
        return decorate(name)
    else:
        return decorate


_PATTERN_CAMEL_CASE_1 = re.compile(r"(.)([A-Z][a-z]+)")
_PATTERN_CAMEL_CASE_2 = re.compile(r"([a-z0-9])([A-Z])")


def to_lower_snake_case(text: str) -> str:
    if "_" in text and text.islower():
        return text

    s1 = _PATTERN_CAMEL_CASE_1.sub(r"\1_\2", text)
    s2 = _PATTERN_CAMEL_CASE_2.sub(r"\1_\2", s1)

    return s2.lower()


@component
class FooAsClass:
    pass


@component(name="custom_name")
class BarAsClass:
    pass

class MyClass:
    pass

@component
class MyArgument:
    pass

@component
def foo_as_function(my_argument: MyArgument) -> MyClass:
    instance = MyClass()
    instance.my_argument = my_argument
    return instance

@component(primary=True)
def foo_as_function_primary() -> MyClass:
    return MyClass()

@component(name="custom_method_name")
def bar_as_function() -> MyClass:
    pass

def main():
    registry = ComponentRegistry()
    registry.initialize_components()
    print(registry)

if __name__ == '__main__':
    main()