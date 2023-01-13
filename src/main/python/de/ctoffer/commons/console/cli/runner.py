import sys
from typing import List, Any, Type

from commons.console.cli.command import Command, cli_data


def command_run(
        command: Type[Any],
        args: List[str] = None
):
    if args is None:
        args = sys.argv

    @Command(
        name=cli_data(command).name,
        subcommands=(command,)
    )
    class WrapperCommand:
        def __call__(self):
            pass

    parsed_arguments = cli_data(WrapperCommand).parser.parse(args)
    instance = WrapperCommand(parsed_arguments)
    instance.__cli_run__()
