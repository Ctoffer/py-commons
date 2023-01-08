from dataclasses import dataclass
from types import MethodType
from typing import Iterable, Type, Callable, TypeVar

from commons.console.cli.dto import CliInternalData
from commons.console.cli.parser import ArgParser, ParsedArguments

T = TypeVar('T')


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

        parser = ArgParser(
            name=self.name,
            short_info=self.description
        )
        sub_commands = self.subcommands

        def construct_parseable_arguments(nested_parser: ArgParser):
            if hasattr(cls, "__annotations__"):
                listed_args = cls.__annotations__.items()
                for name_to_bind, argument in listed_args:
                    nested_parser.add_argument(name_to_bind, argument)

            if sub_commands:
                for subcommand_type in sub_commands:
                    subcommand_type.__cli__.create_subparser(
                        nested_parser.add_subparser(
                            subcommand_type.__cli__.name,
                            short_info=subcommand_type.__cli__.description
                        )
                    )

        cli_data.create_subparser = construct_parseable_arguments
        construct_parseable_arguments(parser)
        cli_data.parser = parser
        old_init = cls.__init__

        cls.__init__ = create_constructed_init(cli_data, old_init)

        return cls


def create_constructed_init(
        cli_data,
        old_init
):
    def constructed_init(
            instance,
            parsed_arguments: ParsedArguments,
            parent=None
    ):
        if parent:
            instance.parent = parent
        else:
            instance.parent = None

        instance.name = cli_data.name
        instance.description = cli_data.description
        instance.available_subcommands = cli_data.subcommands

        for attribute, value in parsed_arguments.args.items():
            setattr(instance, attribute, value)

        old_init(instance)

        if parsed_arguments.sub is not None:
            subcommand_type = type(instance).__cli__.subcommands[parsed_arguments.sub_name]
            subcommand_instance = subcommand_type(
                parsed_arguments=parsed_arguments.sub,
                parent=instance
            )
            instance.__cli_run__ = subcommand_instance.__cli_run__
        else:
            def call_proxy(self):
                instance.__call__()

                result = [instance]
                p = self.parent
                while p is not None:
                    result.append(p)
                    p = p.parent
                return result

            instance.__cli_run__ = MethodType(call_proxy, instance)

    return constructed_init


