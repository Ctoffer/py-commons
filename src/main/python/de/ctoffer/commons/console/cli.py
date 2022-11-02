import sys
from typing import Type, Callable, List

from commons.console.cli_direct import Command, PositionalArgument


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
