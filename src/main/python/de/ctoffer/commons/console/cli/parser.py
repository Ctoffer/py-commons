import argparse
from dataclasses import dataclass
from typing import List, Any, Sequence, Dict

import numpy as np

from commons.console.cli.argument import NamedArgument, ArgumentFrequency, add_argument, Argument


@dataclass
class ParsedArguments:
    name: str
    args: Dict[str, Any]
    sub: 'ParsedArguments' = None


class ArgParser:
    def __init__(
            self,
            name: str,
            exit_on_error: bool = False,
            parent_chain: Sequence[str] = ()
    ):
        self._name = name
        self._parser = argparse.ArgumentParser(prog=name, exit_on_error=exit_on_error)
        self._exit_on_error = exit_on_error
        self._subparsers = dict()
        self._parent_chain = parent_chain

    def add_argument(
            self,
            destination: str,
            argument: Argument
    ) -> 'ArgParser':
        add_argument(
            destination,
            self._parser,
            argument
        )
        return self

    def add_subparser(
            self,
            sub_command_name: str
    ):
        result = ArgParser(
            sub_command_name,
            exit_on_error=self._exit_on_error,
            parent_chain=(*self._parent_chain, self._name)
        )
        self._subparsers[sub_command_name] = result
        # TODO (Christopher): Update help texts
        return result

    def parse(
            self,
            arguments: List[str]
    ) -> ParsedArguments:
        sub_commands = list(self._subparsers)
        subcommand_indices = [arguments.index(sub_command) for sub_command in sub_commands if sub_command in arguments]

        if len(subcommand_indices) > 0:
            index, sub_command = min(subcommand_indices), sub_commands[np.argmin(subcommand_indices)]
        else:
            index, sub_command = None, None

        main_args, sub_args = arguments[:index], arguments[index if index is not None else len(arguments):]
        main_name_space = self._parser.parse_args(main_args)
        main_name_space = ParsedArguments(
            name=self._name,
            args=dict(**main_name_space.__dict__)
        )

        if sub_args:
            main_name_space.sub = self._subparsers[sub_command].parse(sub_args[1:])

        return main_name_space

    def help(self):
        return self._parser.format_help()
