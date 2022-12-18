import argparse
from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum
from typing import Type, Any, TypeVar, Callable, Union, Dict, List, Tuple

from commons.console.cli.dialog import InputDialog

T = TypeVar('T')


class ArgumentFrequency(Enum):
    OPTIONAL = '?'
    ZERO_OR_MORE = '*'
    ONE_OR_MORE = '+'


@dataclass
class Argument:
    name: str
    type: Type[T]
    display_name: str
    number_of_arguments: Union[int, ArgumentFrequency]
    validation: Callable[[T], bool] = ...
    mapping: Callable[[str], T] = ...
    on_mapping_failed: Callable[[Union[Exception, Tuple[Exception]], str, T], T] = ...
    required: bool = False
    default: T = ...
    dialog: InputDialog[T] = None
    help_text: str = ""


@dataclass
class PositionalArgument(Argument):
    pass


@dataclass
class NamedArgument(Argument):
    short_name: Union[None, str] = None


@dataclass
class Flag(NamedArgument):
    represents_true: bool = True


def add_argument(
        destination_of_binding: str,
        parser: ArgumentParser,
        argument: Argument
):
    if type(argument) not in (Flag, NamedArgument, PositionalArgument):
        raise ValueError(f"Unsupported type '{type(argument)}'")

    args = prepare_names(argument)
    kwargs = dict()

    kwargs["dest"] = destination_of_binding
    kwargs["help"] = argument.help_text
    kwargs["nargs"] = argument.number_of_arguments.value \
        if type(argument.number_of_arguments) == ArgumentFrequency \
        else argument.number_of_arguments
    kwargs["metavar"] = argument.display_name
    kwargs["required"] = argument.required

    add_action(kwargs, argument)

    parser.add_argument(
        *args, **kwargs
    )


def prepare_names(
        argument: Union[NamedArgument, Argument]
) -> List[str]:
    args = list()
    if type(argument) == NamedArgument:
        short_name = argument.short_name
        if short_name is None:
            short_name = argument.name[0]

        args.append(f"-{short_name}")

    args.append(f"{argument.name}" if type(argument) == PositionalArgument else f"--{argument.name}")
    return args


def add_action(
        kwargs: Dict[str, Any],
        argument: Union[Argument, Flag]
):
    class ActionProxy(argparse.Action):
        def __init__(
                self,
                **kwargs
        ):
            super().__init__(**kwargs)
            self._validation = argument.validation
            self._mapping = argument.mapping

        def __call__(
                self,
                current_parser: argparse.ArgumentParser,
                namespace: argparse.Namespace,
                values,
                option_string=None
        ):
            # TODO (Ctoffer): Handle all cases.
            if self._validation is not ... and self._validation(values):
                result = self._mapping(values)
            elif self._validation is ... and self._mapping is not ...:
                result = self._mapping(values)
            elif self.default is not ...:
                result = self.default
            else:
                raise ValueError(f"Could not parse {option_string} [{argument.type}] with value {values} ")

            setattr(namespace, self.dest, result)

    if type(argument) == Flag:
        kwargs["action"] = "store_true" if argument.represents_true else "store_false"
    else:
        kwargs["action"] = ActionProxy
