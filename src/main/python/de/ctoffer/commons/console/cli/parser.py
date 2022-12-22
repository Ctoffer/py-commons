import argparse
from typing import List, Any, Sequence, Dict

import numpy as np

from commons.console.cli.argument import NamedArgument, ArgumentFrequency, add_argument, Argument

parser = argparse.ArgumentParser(
    prog="prog",
    exit_on_error=True
)
parser.add_argument("-b", "--barg", nargs="?", required=False)

argument = NamedArgument(
    type=int,
    short_name="a",
    name="arg",
    display_name="argument",
    required=True,
    number_of_arguments=ArgumentFrequency.OPTIONAL,
    validation=lambda s: len(s) > 0 and all('0' <= c <= '9' for c in s),
    mapping=int
)
list_argument = NamedArgument(
    type=List[int],
    short_name="i",
    name="integers",
    display_name="argument",
    required=True,
    number_of_arguments=ArgumentFrequency.ONE_OR_MORE
)

add_argument("larg", parser, list_argument)
add_argument("arg", parser, argument)

subparsers = parser.add_subparsers()
subparser1 = subparsers.add_parser("sub1")
subparser1.add_argument("-f", "--foo")

subparser2 = subparsers.add_parser("sub2")
subparser2.add_argument("-b", "--bar")


# print(parser.format_help())
# print(parser.parse_args(["-a", "3", "-i", "1", "2", "3", "sub1", "-f", "fooValue"]))
# exit(0)
# set1 = parser.parse_args(["sub1", "-f", "fooValue"])
# set2 = parser.parse_args(["-a", "aValue", "sub1", "-f", "fooValue"])
# set3 = parser.parse_args(["-a", "aValue"])

# print(set1, set2, set3)
# print(parser.format_help())


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
            f"{'->'.join((*self._parent_chain, self._name))}.{destination}",
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
    ) -> Dict[str, Any]:
        sub_commands = list(self._subparsers)
        subcommand_indices = [arguments.index(sub_command) for sub_command in sub_commands if sub_command in arguments]
        if len(subcommand_indices) > 0:
            index, sub_command = min(subcommand_indices), sub_commands[np.argmin(subcommand_indices)]
        else:
            index, sub_command = None, None

        main_args, sub_args = arguments[:index], arguments[index if index is not None else len(arguments):]
        main_name_space = self._parser.parse_args(main_args)
        main_name_space = dict(**main_name_space.__dict__)

        if sub_args:
            sub_name_space = self._subparsers[sub_command].parse(sub_args[1:])
            main_name_space.update(sub_name_space)

        # TODO (Ctoffer): Create class which supports relative attribute resolution
        return main_name_space


parser = ArgParser(
    "prog"
).add_argument(
    "argument",
    NamedArgument(
        type=int,
        short_name="a",
        name="arg",
        display_name="argument",
        required=True,
        number_of_arguments=ArgumentFrequency.OPTIONAL,
        validation=lambda s: len(s) > 0 and all('0' <= c <= '9' for c in s),
        mapping=int
    )
).add_argument(
    "integers",
    NamedArgument(
        type=List[int],
        short_name="i",
        name="integers",
        display_name="argument",
        required=True,
        number_of_arguments=ArgumentFrequency.ONE_OR_MORE
    )
)

parser.add_subparser("sub1").add_argument(
    "foo",
    NamedArgument(
        type=str,
        short_name="f",
        name="foo"
    )
)

parser.add_subparser("sub2").add_argument(
    "bar",
    NamedArgument(
        type=str,
        short_name="b",
        name="bar"
    )
)

print(parser.parse(["-a", "3", "-i", "1", "2", "3"]))
print(parser.parse(["-a", "3", "-i", "1", "2", "3", "sub1", "-f", "foo value"]))


class Command:
    def __init__(self, name: str, subcommands: List[Any], description: str):
        pass

    def __call__(self, *args, **kwargs):
        pass


@Command(
    name="",
    subcommands=(),
    description=""
)
class FooCommand:
    debug: ...

    def __call__(self):
        pass
