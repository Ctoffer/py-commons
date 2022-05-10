from dataclasses import dataclass
from typing import Union, Iterable, Type, Dict, Any, Tuple, TypeVar, Generic


class Command:
    def __init__(
            self,
            name: str,
            version: str = "1.0",
            mixin_standard_help_options: bool = False,
            subcommands: Tuple = ()
    ):
        pass

    def __call__(self, *args, **kwargs):
        return args[0]


class SubCommand:
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        return args[0]


T = TypeVar('T')


class ParentCommand(Generic[T]):
    pass


class Option:
    def __init__(self, names: Union[str, Iterable[str]], description: str, default_value: str):
        pass


class Parameters:
    def __init__(self, param_label: str, description: str, default_value: str):
        pass


def execute_command(command_object: Any, argv: Dict[str, Any]):
    print(command_object, argv)
