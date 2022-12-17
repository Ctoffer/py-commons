from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum
from typing import Type, Any, TypeVar, Callable, Union

T = TypeVar('T')


class ArgumentFrequency(Enum):
    OPTIONAL = '?'
    ZERO_OR_MORE = '*'
    ONE_OR_MORE = '+'


@dataclass
class Argument:
    name: str
    help_text: str
    type: Type[T]
    required: bool
    mapping: Callable[[str], T]
    validation: Callable[[T], bool]
    display_name: str
    number_of_arguments: Union[int, ArgumentFrequency]
    default: T
    dialog: InputDialog[T]


@dataclass
class PositionalArgument(Argument):
    pass


@dataclass
class NamedArgument(Argument):
    short_name: str


@dataclass
class Flag(NamedArgument):
    represents_true: bool


def add_argument(
        destination_of_binding: str,
        parser: ArgumentParser,
        argument: Argument
):
    if type(argument) not in (Flag, NamedArgument, PositionalArgument):
        raise ValueError(f"Unsupported type '{type(argument)}'")

    args = list()
    kwargs = dict()

    if type(argument) == NamedArgument:
        args.append(f"-{argument.short_name}")

    args.append(f"{argument.name}" if type(argument) == PositionalArgument else f"--{argument.name}")

    kwargs["dest"] = destination_of_binding
    kwargs["help"] = argument.help_text
    kwargs["nargs"] = argument.number_of_arguments.value \
        if type(argument.number_of_arguments) == ArgumentFrequency \
        else argument.number_of_arguments
    kwargs["metavar"] = argument.display_name
    kwargs["required"] = argument.required

    if type(argument) == Flag:
        kwargs["action"] = "store_true" if argument.represents_true else "store_false"

    parser.add_argument(
        *args, **kwargs
    )
