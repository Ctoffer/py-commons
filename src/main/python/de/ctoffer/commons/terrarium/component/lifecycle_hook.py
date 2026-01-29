from typing import Protocol, runtime_checkable

from commons.terrarium.component.registry_state import TerrariumState

@runtime_checkable
class PostInit(Protocol):
    def __post_init__(self) -> None:
        pass

@runtime_checkable
class PreDestroy(Protocol):
    def __pre_destroy__(self) -> None:
        pass

@runtime_checkable
class EntryPoint(Protocol):
    def main(self) -> None:
        pass