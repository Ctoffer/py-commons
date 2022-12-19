import argparse
from typing import List, Any

from commons.console.cli.argument import NamedArgument, ArgumentFrequency, add_argument

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

print(parser.format_help())
print(parser.parse_args(["-a", "3", "-i", "1", "2", "3", "sub1", "-f", "fooValue"]))
exit(0)
set1 = parser.parse_args(["sub1", "-f", "fooValue"])
set2 = parser.parse_args(["-a", "aValue", "sub1", "-f", "fooValue"])
set3 = parser.parse_args(["-a", "aValue"])

print(set1, set2, set3)
print(parser.format_help())


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
