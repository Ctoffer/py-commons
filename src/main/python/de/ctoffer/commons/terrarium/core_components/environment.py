from commons.terrarium import component

from sys import argv
from os import environ

from commons.terrarium.component.lifecycle_hook import PostInit

@component
class Environment(PostInit):
    def __init__(self):
        self._environment: dict[str, str] = dict(environ)
        self._arguments: tuple[str, ...] = tuple(argv)
        self._profile: str = ""

        if "terrarium.profile" in environ:
            self._profile = environ.get("terrarium.profile")

    @property
    def environment(self) -> dict[str, str]:
        return self._environment

    @property
    def arguments(self) -> tuple[str, ...]:
        return self._arguments

    @property
    def profile(self) -> str:
        return self._profile