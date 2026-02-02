from commons.terrarium import component

from sys import argv
from os import environ

from commons.terrarium.component.lifecycle_hook import PostInit

@component
class Environment(PostInit):
    def __init__(self):
        self._environment: dict[str, str] = dict()
        self._arguments: tuple[str, ...] = tuple()
        self._active_profiles: tuple[str] = tuple()


    def __post_init__(self):
        self._environment = dict(environ)
        self._arguments = tuple(argv)

        if "terrarium.active_profiles" in environ:
            self._active_profiles = tuple(environ.get("terrarium.active_profiles").split(','))


    @property
    def environment(self) -> dict[str, str]:
        return self._environment

    @property
    def arguments(self) -> tuple[str, ...]:
        return self._arguments

    @property
    def active_profiles(self) -> tuple[str, ...]:
        return self._active_profiles