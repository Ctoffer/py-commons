import argparse
from dataclasses import dataclass
from typing import Type, TypeVar, Union, Callable, Dict, List, Tuple

T = TypeVar('T')


@dataclass
class PositionalArgument:
    type: Type[T]
    default: T = ...
    description: str = ""
    nargs: Union[int, str] = ...


@dataclass
class Argument:
    type: Type[T]
    short: str
    long: str
    default: T = ...
    description: str = ""
    nargs: Union[int, str] = ...
    required: bool = False


@dataclass(init=False, frozen=False)
class CliInternalData:
    name: str
    description: str
    subcommands: Dict[str, Callable]
    grouped_arguments: Dict[str, List[Tuple[str, Union[PositionalArgument, Argument]]]]
    create_subparser: Callable
    parser: argparse.ArgumentParser
