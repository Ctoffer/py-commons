from typing import List, Dict, Any

import pytest

from commons.console.cli.argument import NamedArgument, ArgumentFrequency, Flag, PositionalArgument
from commons.console.cli.parser import ArgParser, ParsedArguments
from commons.testing.asserts import assert_equals, assert_not_none, assert_none


@pytest.fixture
def standard_parser() -> ArgParser:
    return ArgParser(
        "prog"
    ).add_argument(
        "aarg", NamedArgument(type=int, name="aargument")
    ).add_argument(
        "parg", PositionalArgument(type=List[int], name="pargument")
    ).add_argument(
        "barg", NamedArgument(type=int, name="bargument", required=True)
    ).add_argument(
        "flag", Flag(type=bool, name="flag")
    ).add_argument(
        "qarg", PositionalArgument(type=List[int], name="qargument", required=True)
    )


@pytest.fixture
def nested_parser() -> ArgParser:
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

    return parser


class TestHelpText:
    def test_help_different_arguments(
            self,
            standard_parser: ArgParser
    ):
        print(standard_parser.help())

    def test_help_text_nested(
            self,
            nested_parser: ArgParser
    ):
        """
        prog [-h] -a [argument] -i argument [argument ...]

        optional arguments:
          -h, --help            show this help message and exit
          -a [argument], --arg [argument]
          -i argument [argument ...], --integers argument [argument ...]

        :param nested_parser:
        :return:
        """

        help_text = nested_parser.help().split("\n")
        print(nested_parser.help())

        assert_equals(actual=help_text, expected=[""])


class TestSubCommand:
    def test_parser_without_subcommand(
            self,
            nested_parser: ArgParser
    ):
        actual = nested_parser.parse(["-a", "3", "-i", "1", "2", "3"])

        self._check_name_and_args(actual)

        sub = actual.sub
        assert_none(actual=sub)

    @staticmethod
    def _check_name_and_args(
            actual: ParsedArguments
    ):
        name = actual.name
        args = actual.args
        assert_equals(actual=name, expected="prog")
        assert_equals(actual=args["argument"], expected=3)
        assert_equals(actual=args["integers"], expected=[1, 2, 3])

    def test_parser_with_subcommand(
            self,
            nested_parser: ArgParser
    ):
        actual = nested_parser.parse(["-a", "3", "-i", "1", "2", "3", "sub1", "-f", "foo value"])

        self._check_name_and_args(actual)

        sub = actual.sub
        assert_not_none(actual=sub)
        assert_equals(actual=sub.name, expected="sub1")
        assert_equals(actual=sub.args["foo"], expected="foo value")
        assert_none(actual=sub.sub)
