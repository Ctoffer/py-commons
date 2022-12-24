import argparse
import pathlib
from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum
from typing import Type, Any, TypeVar, Callable, Union, Dict, List, Tuple, Set, Iterable, get_args, get_origin

from commons.console.cli.argparse_actions import PathMapperAction, StrMapperAction, BoolMapperAction, FloatMapperAction, \
    IntMapperAction, IntSetMapperAction, FloatSetMapperAction, BoolSetMapperAction, StrSetMapperAction, \
    PathSetMapperAction, IntTupleMapperAction, FloatTupleMapperAction, BoolTupleMapperAction, StrTupleMapperAction, \
    PathTupleMapperAction, IntListMapperAction, FloatListMapperAction, BoolListMapperAction, StrListMapperAction, \
    PathListMapperAction
from commons.console.cli.dialog import InputDialog
from commons.util.typing_support import expand_type_combinations

T = TypeVar('T')
SupportedBaseTypes = Union[int, float, bool, str, pathlib.Path]

SUPPORTED_TYPES = expand_type_combinations((
    int, float, bool, str, pathlib.Path, List[SupportedBaseTypes], Set[SupportedBaseTypes], Tuple[SupportedBaseTypes]
))

SUPPORTED_TYPE_ACTIONS = {
    int: IntMapperAction,
    float: FloatMapperAction,
    bool: BoolMapperAction,
    str: StrMapperAction,
    pathlib.Path: PathMapperAction,

    Set[int]: IntSetMapperAction,
    Set[float]: FloatSetMapperAction,
    Set[bool]: BoolSetMapperAction,
    Set[str]: StrSetMapperAction,
    Set[pathlib.Path]: PathSetMapperAction,

    Tuple[int]: IntTupleMapperAction,
    Tuple[float]: FloatTupleMapperAction,
    Tuple[bool]: BoolTupleMapperAction,
    Tuple[str]: StrTupleMapperAction,
    Tuple[pathlib.Path]: PathTupleMapperAction,

    List[int]: IntListMapperAction,
    List[float]: FloatListMapperAction,
    List[bool]: BoolListMapperAction,
    List[str]: StrListMapperAction,
    List[pathlib.Path]: PathListMapperAction,
}


class ArgumentFrequency(Enum):
    OPTIONAL = '?'
    ZERO_OR_MORE = '*'
    ONE_OR_MORE = '+'


@dataclass
class Argument:
    name: str
    type: Type[T]
    number_of_arguments: Union[None, int, ArgumentFrequency] = None
    display_name: str = None
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
    if type(argument) != Flag:
        kwargs["nargs"] = argument.number_of_arguments.value \
            if type(argument.number_of_arguments) == ArgumentFrequency \
            else argument.number_of_arguments
        kwargs["metavar"] = argument.display_name
    if type(argument) != PositionalArgument:
        kwargs["required"] = argument.required

    add_action(kwargs, argument)

    parser.add_argument(
        *args, **kwargs
    )


def prepare_names(
        argument: Union[NamedArgument, Argument]
) -> List[str]:
    args = list()
    if type(argument) == PositionalArgument:
        return args

    elif type(argument) == NamedArgument:
        short_name = argument.short_name
        if short_name is None:
            short_name = argument.name[0]

        args.append(f"-{short_name}")

    if argument.display_name is ...:
        argument.display_name = argument.name

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
            self._on_mapping_failed = argument.on_mapping_failed

        def __call__(
                self,
                current_parser: argparse.ArgumentParser,
                namespace: argparse.Namespace,
                values,
                option_string=None
        ):
            def mapper(value):
                if self._mapping is not ...:
                    try:
                        r = self._mapping(value)
                    except Exception as error:
                        if self._on_mapping_failed is not ...:
                            r = self._on_mapping_failed(error, value, self.default)
                        else:
                            r = None
                else:
                    raise ValueError(f"No mapper configured for {option_string}")

                return r

            if self._validation is not ... and self._validation(values):
                result = mapper(values)
            elif self._validation is ... and self._mapping is not ...:
                result = mapper(values)
            elif self.default is not ...:
                result = self.default
            else:
                raise ValueError(f"Could not parse {option_string} [{argument.type}] with value {values} ")

            setattr(namespace, self.dest, result)

    if type(argument) == Flag:
        kwargs["action"] = "store_true" if argument.represents_true else "store_false"
    elif argument.mapping is ... and argument.type in SUPPORTED_TYPES:
        kwargs["action"] = SUPPORTED_TYPE_ACTIONS[argument.type]
    else:
        kwargs["action"] = ActionProxy
