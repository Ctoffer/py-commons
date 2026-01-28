from enum import Enum
from typing import Any, Callable, get_type_hints

from commons.terrarium.component.descriptor import ComponentDescriptor
from commons.terrarium.component.descriptor_factory import ComponentDescriptorFactory
from commons.terrarium.component.proxy import ComponentProxy
from commons.util.singleton import Singleton


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
            return potential_matches[0].instance
        elif potential_matches:
            candidates = [candidate for candidate in potential_matches if candidate.primary]

            # one primary component found
            if len(candidates) == 1:
                return candidates[0].instance
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


def proxy_of_type[T](type_: type[T], name: str, primary: bool = False) -> 'ComponentProxy':
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
    return result


def proxy_of_callable[T](
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