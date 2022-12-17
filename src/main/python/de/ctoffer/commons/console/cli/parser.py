import argparse
from typing import List, Any

parser = argparse.ArgumentParser(
    prog="prog",
    exit_on_error=True
)
parser.add_argument("-a", "--arg", nargs="?", required=True)
parser.add_argument("-b", "--barg", nargs="?", required=False)

subparsers = parser.add_subparsers()
subparser1 = subparsers.add_parser("sub1")
subparser1.add_argument("-f", "--foo")

subparser2 = subparsers.add_parser("sub2")
subparser2.add_argument("-b", "--bar")

print(parser.format_help())
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
