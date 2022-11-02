import argparse
import sys
from dataclasses import dataclass
from typing import TypeVar, Type, Union, Iterable, Callable, Any, Dict, List, Tuple

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


def transfer_non_empty_attribute(dictionary: Dict[str, Any], data: Any, attribute_name: str, empty: Any = ...) -> None:
    if hasattr(data, attribute_name):
        attribute = getattr(data, attribute_name)

        if attribute is not empty:
            dictionary[attribute_name] = attribute


def group_arguments(
        listed_args: List[Tuple[str, Union[PositionalArgument, Argument]]]
) -> Dict[str, List[Tuple[str, Union[PositionalArgument, Argument]]]]:
    grouped_args = {
        "optional": list(),
        "required": list(),
        "required_named": list()
    }

    for attribute_name, argument_description in listed_args:
        tup = (attribute_name, argument_description)

        if isinstance(argument_description, Argument) and argument_description.required:
            listing = grouped_args["required_named"]
        elif isinstance(argument_description, PositionalArgument) or argument_description.required:
            listing = grouped_args["required"]
        else:
            listing = grouped_args["optional"]

        listing.append(tup)

    return grouped_args


def add_argument_group_to_parser(
        parser: argparse.ArgumentParser,
        args: List[Tuple[str, Union[PositionalArgument, Argument]]],
        parent_chain: str
):
    for attribute_name, argument_description in args:
        requested_type = argument_description.type
        is_meta_list = hasattr(requested_type, "_gorg") and requested_type._gorg is List

        kwargs = {
            "dest": parent_chain + "." + attribute_name,
            "metavar": attribute_name,
            "type": requested_type.__args__[0] if is_meta_list else requested_type,
            "help": argument_description.description,
        }

        transfer_non_empty_attribute(kwargs, argument_description, "required")
        transfer_non_empty_attribute(kwargs, argument_description, "default")
        transfer_non_empty_attribute(kwargs, argument_description, "nargs")

        if isinstance(argument_description, PositionalArgument):
            parser.add_argument(
                **kwargs
            )
        else:
            parser.add_argument(
                "-" + argument_description.short,
                "--" + argument_description.long,
                **kwargs
            )


@dataclass
class Command:
    name: str
    subcommands: Iterable[Type[Callable]] = None
    description: str = ""

    def __call__(self, cls: Type[T]) -> Type[T]:
        cls.__cli_name__ = self.name
        cls.__cli_description__ = self.description

        if self.subcommands:
            cls.__cli_subcommands__ = {subcommand.__cli_name__: subcommand for subcommand in self.subcommands}
        else:
            cls.__cli_subcommands__ = dict()

        parser = argparse.ArgumentParser(
            prog=self.name,
            add_help=False,
            description=self.description
        )
        sub_commands = self.subcommands

        def construct_parseable_arguments(nested_parser, parent=""):
            parent_chain = "->".join((parent, cls.__cli_name__)) if parent else cls.__cli_name__
            nested_parser.set_defaults(**{"__parent_chain__": parent_chain})

            if hasattr(cls, "__annotations__"):
                listed_args = cls.__annotations__.items()

                groups = group_arguments(listed_args)
                cls.__cli_grouped_arguments__ = groups

                add_argument_group_to_parser(
                    parser=nested_parser.add_argument_group("required named arguments"),
                    args=groups["required_named"],
                    parent_chain=parent_chain
                )
                add_argument_group_to_parser(
                    parser=nested_parser.add_argument_group("optional arguments"),
                    args=groups["optional"],
                    parent_chain=parent_chain
                )
                add_argument_group_to_parser(
                    parser=nested_parser.add_argument_group("required arguments"),
                    args=groups["required"],
                    parent_chain=parent_chain
                )

            if sub_commands:
                sub_parser = nested_parser.add_subparsers(title="sub commands", help="Available subcommands.")
                for subcommand_type in sub_commands:
                    subcommand_type.__cli_create_subparser__(
                        sub_parser.add_parser(
                            subcommand_type.__cli_name__
                        ), parent_chain
                    )

        cls.__cli_create_subparser__ = construct_parseable_arguments
        construct_parseable_arguments(parser)
        cls.__cli_parser__ = parser
        old_init = cls.__init__

        def constructed_init(instance, namespace: Union[argparse.Namespace, Dict[str, Any]], parent=None):
            if parent:
                instance.parent = parent
            instance.name = cls.__cli_name__
            instance.description = cls.__cli_description__
            instance.available_subcommands = cls.__cli_subcommands__

            layer_name = type(instance).__cli_name__
            if isinstance(namespace, argparse.Namespace):
                namespace = dict(**namespace.__dict__)
                namespace["__parent_chain__"] = namespace["__parent_chain__"].split("->")

            chain = namespace["__parent_chain__"]
            del namespace["__parent_chain__"]

            if layer_name != chain[0]:
                raise ValueError

            reduced_scope = dict()
            for key, value in namespace.items():
                if key.startswith(layer_name) and "->" not in key:
                    scope, attribute = key.split(".")
                    setattr(instance, attribute, value)
                else:
                    reduced_scope["->".join(key.split("->")[1:])] = value

            reduced_chain = chain[1:]
            reduced_scope["__parent_chain__"] = reduced_chain
            old_init(instance)

            if len(reduced_chain) >= 1:
                subcommand_type = type(instance).__cli_subcommands__[reduced_chain[0]]
                subcommand_instance = subcommand_type(
                    namespace=reduced_scope,
                    parent=instance
                )
                instance.__cli_run__ = subcommand_instance.__cli_run__
            else:
                instance.__cli_run__ = instance.__call__

        cls.__init__ = constructed_init
        cls.cli_help = lambda slf: cls.__cli_parser__.format_help().split('\n')

        return cls


def run_command(command: Type[Callable], args: List[str] = None, interactive: bool = False):
    @Command(
        name="",
        subcommands=(command,),
        description="Nameless transparent command wrapper. Contains no functionality."
    )
    class WrapperCommand:
        def __call__(self):
            pass

    if args is None:
        args = sys.argv

    result = WrapperCommand.__cli_parser__.parse_args(args[1:])

    if not result.__parent_chain__.startswith(command.__cli_name__):
        raise ValueError("Parsed arguments did not contain root-parent command.")
    elif interactive:
        _run_interactive(command(result))
    else:
        return command(result).__cli_run__()


def _run_interactive(command: Callable):
    print(command.name)

    global_context = {
        "active": True
    }

    while global_context["active"]:
        user_input = input("(" + command.name + ") >: ")
        args = _parse(user_input)
        print(args)

        if args:
            if args[0] == "exit":
                global_context["active"] = False
            elif args[0] in ("?", "help"):
                print(" " * 9, command.description)
                print(" " * 9)

                print(" " * 9, "Available Subcommands")
                for subcommand in command.available_subcommands:
                    print(" " * 12, subcommand)
                print(" " * 9)

                print(" " * 9, "Arguments")
                for group, args in type(command).__cli_grouped_arguments__.items():
                    print(" " * 12, group.replace('_', ' ').title() + " Arguments")
                    for bound_name, arg in args:
                        if isinstance(arg, PositionalArgument):
                            print(" " * 15, bound_name)
                        else:
                            print(" " * 15, "-" + arg.short + ", --" + arg.long)
                    print(" " * 12)


def _parse(user_input: str) -> List[str]:
    escaped = False
    quoted = False
    buffer = ""
    result = list()

    for char in user_input:
        if escaped:
            escaped = False
            buffer += char
        elif quoted and char == '"':
            quoted = False
        elif char == ' ':
            if quoted:
                buffer += char
            else:
                result.append(buffer)
                buffer = ""
        elif char == '"':
            quoted = True
        elif char == '\\':
            escaped = True
        else:
            buffer += char

    if buffer:
        result.append(buffer)

    return result
