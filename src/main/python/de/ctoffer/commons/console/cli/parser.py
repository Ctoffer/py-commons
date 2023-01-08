import argparse
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Any, Sequence, Dict, Union

from commons.console.cli.argument import NamedArgument, ArgumentFrequency, add_argument, Argument, Flag, \
    PositionalArgument

_INDEX_OF_USAGE = 1


@dataclass
class ParsedArguments:
    name: str
    args: Dict[str, Any]
    sub_name: str = None
    sub: 'ParsedArguments' = None


class ArgParser:
    def __init__(
            self,
            name: str,
            exit_on_error: bool = False,
            short_info: str = "",
            parent_chain: Sequence[str] = ()
    ):
        self._name = name
        self._exit_on_error = exit_on_error
        self._short_info = short_info
        self._arguments = list()
        self._subparsers = dict()
        self._parent_chain = parent_chain

        self._parser = argparse.ArgumentParser(prog=name, exit_on_error=exit_on_error)
        self._parser.format_help = self.help

    @property
    def name(
            self
    ) -> str:
        return self._name

    @property
    def short_info(
            self
    ) -> str:
        return self._short_info

    def add_argument(
            self,
            destination: str,
            argument: Argument
    ) -> 'ArgParser':
        """
        Adds an argument to this parser.

        If the argument is a PositionalArgument it will automatically be set to required, since there is no support
        for optional positional arguments.

        :param destination: Name of the bound argument
        :param argument: Contains the data describing the argument
        :return: The current parser instance
        """
        if isinstance(argument, PositionalArgument):
            argument.required = True

        self._arguments.append(argument)
        add_argument(
            destination,
            self._parser,
            argument
        )
        return self

    def add_subparser(
            self,
            sub_command_name: str,
            short_info: str = ""
    ):
        result = ArgParser(
            sub_command_name,
            short_info=short_info,
            exit_on_error=self._exit_on_error,
            parent_chain=(*self._parent_chain, self._name)
        )
        self._subparsers[sub_command_name] = result
        return result

    def parse(
            self,
            arguments: List[str]
    ) -> ParsedArguments:
        sub_commands = list(self._subparsers)
        subcommand_indices = [arguments.index(sub_command) for sub_command in sub_commands if sub_command in arguments]

        if len(subcommand_indices) > 0:
            index = min(subcommand_indices)
            sub_command = arguments[index]
        else:
            index, sub_command = None, None

        main_args, sub_args = arguments[:index], arguments[index if index is not None else len(arguments):]
        main_name_space = self._parser.parse_args(main_args)
        main_name_space = ParsedArguments(
            name=self._name,
            args=dict(**main_name_space.__dict__)
        )

        if sub_args:
            main_name_space.sub_name = sub_command
            main_name_space.sub = self._subparsers[sub_command].parse(sub_args[1:])

        return main_name_space

    def help(self):
        help_segments = defaultdict(list)
        help_segments["sub"].extend(sorted(self._subparsers.values(), key=lambda k: k.name))

        for argument in self._arguments:
            if type(argument) == Flag:
                key = "flag"
            elif type(argument) == NamedArgument:
                key = "named-req" if argument.required else "named-opt"
            elif type(argument) == PositionalArgument:
                key = "positional"
            else:
                raise ValueError(f"Unknown category for argument '{argument}'.")

            help_segments[key].append(argument)

        help_segments["flag"].insert(0, Flag(
            short_name="h", name="help", help_text="show this help message and exit", required=False
        ))

        lines = list()
        lines.append("Usage:")
        lines.append([f"   {self.name}"])
        lines.append("")

        ArgParser._add_subcommand_segment_to_help(lines, help_segments["sub"])
        ArgParser._add_segment_to_help(lines, help_segments["flag"], "flags")
        ArgParser._add_segment_to_help(lines, help_segments["named-req"], "required named arguments")
        ArgParser._add_segment_to_help(lines, help_segments["named-opt"], "optional named arguments")
        ArgParser._add_segment_to_help(lines, help_segments["positional"], "positional arguments")

        lines[_INDEX_OF_USAGE] = " ".join(lines[_INDEX_OF_USAGE])
        return '\n'.join(lines)

    @staticmethod
    def _add_subcommand_segment_to_help(
            lines: List[Union[List[str], str]],
            segment_data: List['ArgParser']
    ):
        if segment_data:
            lines.append("subcommands:")
            names = list(map(lambda sub: sub.name, segment_data))
            max_len_name = max(map(len, names))
            lines[_INDEX_OF_USAGE].append(f"{{{','.join(names)}}}")

            for subcommand in segment_data:
                format_string = f"   {{name:<{max_len_name + 2}s}}{{help}}"
                lines.append(format_string.format(name=subcommand.name, help=subcommand.short_info))
            lines.append("")
        else:
            lines[_INDEX_OF_USAGE].append("")

    @staticmethod
    def _add_segment_to_help(
            lines: List[Union[List[str], str]],
            segment_data: List[Argument],
            title: str
    ):
        if not segment_data:
            return

        lines.append(f"{title}:")
        # TODO (Ctoffer): Complexitiy is growing, maybe use pandas Dataframe or custom class?
        table = {
            "short_name": list(),
            "name": list(),
            "display_name": list(),
            "help_text": list(),
            "required": list(),
            "number_of_arguments": list()
        }
        number_of_table_rows = 0

        for argument in segment_data:
            if isinstance(argument, NamedArgument) and argument.short_name is not None:
                short_name = f"-{argument.short_name}, "
            else:
                short_name = ""

            name = argument.name if type(argument) == PositionalArgument else f"--{argument.name}"
            display_name = argument.display_name if argument.display_name is not None else ""

            table["short_name"].append(short_name)
            table["name"].append(name)
            table["display_name"].append(display_name)
            table["help_text"].append(argument.help_text)
            table["required"].append(argument.required)
            table["number_of_arguments"].append(argument.number_of_arguments)
            number_of_table_rows += 1

        table_sizes = {k: max(map(len, column)) for k, column in table.items() if
                       k in ("short_name", "name", "display_name")}

        format_line = f"   {{short_name:<{table_sizes['short_name']}s}}" \
                      f"{{name:<{table_sizes['name']}s}} " \
                      f"{{display_name:<{table_sizes['display_name']}s}}" \
                      f"{{help_text}}"

        for i in range(number_of_table_rows):
            short_name = table["short_name"][i]
            name = table["name"][i]
            display_name = table["display_name"][i]
            help_text = table["help_text"][i]
            required = table["required"][i]
            number_of_arguments = table["number_of_arguments"][i]

            lines[_INDEX_OF_USAGE].insert(-1, build_usage_help_segment(
                short_name[:-2], name, display_name, required, number_of_arguments
            ))
            display_name = map_display_name(display_name, number_of_arguments)
            if display_name:
                display_name = display_name + " "
            lines.append(
                format_line.format(
                    short_name=short_name,
                    name=name,
                    display_name=display_name,
                    help_text=help_text
                ).rstrip()
            )
        lines.append("")


def map_argument_frequency(
        number_of_arguments: ArgumentFrequency,
        display_name: str
) -> str:
    if number_of_arguments == ArgumentFrequency.OPTIONAL:
        result = f"[{display_name}]"
    elif number_of_arguments == ArgumentFrequency.ZERO_OR_MORE:
        result = f"[{display_name} ...]"
    elif number_of_arguments == ArgumentFrequency.ONE_OR_MORE:
        result = f"{display_name} [{display_name} ...]"
    else:
        raise ValueError(f"Unexpected value for parameter 'number of arguments': {number_of_arguments}")

    return result


def map_display_name(
        display_name: str,
        number_of_arguments: Union[None, int, ArgumentFrequency]
) -> str:
    if number_of_arguments is None:
        result = display_name.rstrip()
    elif type(number_of_arguments) == int:
        result = (' '.join([display_name] * number_of_arguments)).rstrip()
    elif type(number_of_arguments) == ArgumentFrequency:
        result = map_argument_frequency(number_of_arguments, display_name)
    else:
        raise ValueError(f"Unexpected type for parameter 'number_of_arguments': {type(number_of_arguments)}")

    return result


# TODO (Ctoffer): Make stackable iterative constraints compatible with error_handler, logging, time_measurement
# @constraint(Scope.Parameter, applies_to="name", enforce=NotEmpty)
# @constraint(Scope.Parameter, applies_to="number_of_arguments", enforce=StrictTypeCheck)
# @constraint(Scope.Return, enforce=(StrictTypeCheck, NotEmpty))
def build_usage_help_segment(
        short_name: str,
        name: str,
        display_name: str,
        required: bool,
        number_of_arguments: Union[None, int, ArgumentFrequency]
) -> str:
    """
    Creates the argument segment for the usage line in the help text.

    The basic name shown is either the short_name if present or the name.
    The name is then paired with the result of map_display_name.
    In case the argument is optional [] are put around the segment.

    :param short_name: Possible empty string representing a short name for this argument
    :param name: Proper name of the argument. Can't be not empty.
    :param display_name:
    :param required:
    :param number_of_arguments:
    :return:
    """
    result = short_name if short_name else name

    result = f"{result} {map_display_name(display_name, number_of_arguments)}".rstrip()

    if not required:
        result = f"[{result}]"

    return result
