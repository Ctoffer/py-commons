import sys
from typing import Type, Callable, List

from commons.console.cli_direct import Command, PositionalArgument
from commons.console.cli_interactive import run_interactive


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

    result = WrapperCommand.__cli__.parser.parse_args(args[1:])

    if not result.__parent_chain__.startswith(command.__cli__.name):
        raise ValueError("Parsed arguments did not contain root-parent command.")
    elif interactive:
        run_interactive(command(result))
    else:
        return command(result).__cli_run__()


