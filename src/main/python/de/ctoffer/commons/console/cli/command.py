from dataclasses import dataclass
from types import MethodType
from typing import Iterable, Type, Callable, TypeVar, Any, Dict

from commons.console.cli.dto import CliInternalData
from commons.console.cli.parser import ArgParser, ParsedArguments

T = TypeVar('T')


def command(
        *,
        name: str,
        subcommands: Iterable[Type[Callable]] = None,
        description: str = ""
):
    return Command(name=name, subcommands=subcommands, description=description)


@dataclass
class Command:
    name: str
    subcommands: Iterable[Type[Callable]] = None
    description: str = ""

    def __call__(
            self,
            cls: Type[T]
    ) -> Type[T]:
        cli_internal_data = self._create_cli_internal_data()
        cls.__cli__ = cli_internal_data

        self._setup_subcommand_mapping(cli_internal_data)
        self._setup_create_subparser(cls, cli_internal_data)
        self._setup_parser(cli_internal_data)

        old_init = cls.__init__
        cls.__init__ = create_constructed_init(cli_internal_data, old_init)

        return cls

    def _create_cli_internal_data(
            self
    ) -> CliInternalData:
        cli_internal_data = CliInternalData()
        cli_internal_data.name = self.name
        cli_internal_data.description = self.description
        return cli_internal_data

    def _setup_subcommand_mapping(
            self,
            cli_internal_data: CliInternalData
    ):
        if self.subcommands:
            cli_internal_data.subcommands = self._subcommands_to_dict()
        else:
            cli_internal_data.subcommands = dict()

    def _subcommands_to_dict(self) -> Dict[str, Type[Any]]:
        return {cli_data(subcommand).name: subcommand for subcommand in self.subcommands}

    def _setup_create_subparser(
            self,
            cls: Type[T],
            cli_internal_data: CliInternalData
    ):
        construct_parseable_arguments = create_construct_parsable_arguments(
            cls=cls,
            sub_commands=self.subcommands
        )
        cli_internal_data.create_subparser = construct_parseable_arguments

    def _setup_parser(
            self,
            cli_internal_data: CliInternalData
    ):
        parser = ArgParser(
            name=self.name,
            short_info=self.description
        )
        cli_internal_data.create_subparser(parser)
        cli_internal_data.parser = parser


def cli_data(
        obj: Any
) -> CliInternalData:
    if not hasattr(obj, "__cli__"):
        raise ValueError(f"Object '{obj}' has no attribute __cli__ storing cli data.")

    if type(obj.__cli__) != CliInternalData:
        raise ValueError(f"Object '{obj}' has an attribute __cli__ which isn not of type CliInternalData.")

    return obj.__cli__


def create_constructed_init(
        data: CliInternalData,
        old_init: Callable[[Any], None]
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

        instance.name = data.name
        instance.description = data.description
        instance.available_subcommands = data.subcommands

        for attribute, value in parsed_arguments.args.items():
            setattr(instance, attribute, value)

        old_init(instance)

        if parsed_arguments.sub is not None:
            subcommand_type = cli_data(type(instance)).subcommands[parsed_arguments.sub_name]
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


def create_construct_parsable_arguments(
        cls: Type[T],
        sub_commands: Iterable[Type[Any]]
) -> Callable[[ArgParser], None]:
    def construct_parseable_arguments(nested_parser: ArgParser):
        if hasattr(cls, "__annotations__"):
            listed_args = cls.__annotations__.items()
            for name_to_bind, argument in listed_args:
                nested_parser.add_argument(name_to_bind, argument)

        if sub_commands:
            for subcommand_type in sub_commands:
                cli = cli_data(subcommand_type)
                cli.create_subparser(
                    nested_parser.add_subparser(
                        cli.name,
                        short_info=cli.description
                    )
                )

    return construct_parseable_arguments


def create_dialog_run(
        cls: Type[T]
):
    cli = cli_data(cls)
