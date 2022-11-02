import argparse
from dataclasses import dataclass
from typing import TypeVar, Type, Union, Iterable, Callable, Any, Dict, List, Tuple

from commons.console.cli_dto import PositionalArgument, Argument, CliInternalData

T = TypeVar('T')


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
        cli_data = CliInternalData()
        cls.__cli__ = cli_data
        cli_data.name = self.name
        cli_data.description = self.description

        if self.subcommands:
            cli_data.subcommands = {subcommand.__cli__.name: subcommand for subcommand in self.subcommands}
        else:
            cli_data.subcommands = dict()

        parser = argparse.ArgumentParser(
            prog=self.name,
            add_help=False,
            description=self.description
        )
        sub_commands = self.subcommands

        def construct_parseable_arguments(nested_parser, parent=""):
            parent_chain = "->".join((parent, cli_data.name)) if parent else cli_data.name
            nested_parser.set_defaults(**{"__parent_chain__": parent_chain})

            if hasattr(cls, "__annotations__"):
                listed_args = cls.__annotations__.items()

                groups = group_arguments(listed_args)
                cli_data.grouped_arguments = groups

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
                    subcommand_type.__cli__.create_subparser(
                        sub_parser.add_parser(
                            subcommand_type.__cli__.name
                        ), parent_chain
                    )

        cli_data.create_subparser = construct_parseable_arguments
        construct_parseable_arguments(parser)
        cli_data.parser = parser
        old_init = cls.__init__

        def constructed_init(instance, namespace: Union[argparse.Namespace, Dict[str, Any]], parent=None):
            if parent:
                instance.parent = parent
            instance.name = cli_data.name
            instance.description = cli_data.description
            instance.available_subcommands = cli_data.subcommands

            layer_name = type(instance).__cli__.name
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
                subcommand_type = type(instance).__cli__.subcommands[reduced_chain[0]]
                subcommand_instance = subcommand_type(
                    namespace=reduced_scope,
                    parent=instance
                )
                instance.__cli_run__ = subcommand_instance.__cli_run__
            else:
                instance.__cli_run__ = instance.__call__

        cls.__init__ = constructed_init
        cls.cli_help = lambda slf: cli_data.parser.format_help().split('\n')

        return cls
