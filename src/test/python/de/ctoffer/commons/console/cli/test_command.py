from typing import List, Type
from unittest.mock import patch, MagicMock

import pytest

from commons.console.cli.argument import NamedArgument
from commons.console.cli.command import Command, cli_data
from commons.testing.asserts import assert_equals, assert_false, assert_true, assert_same, assert_none


class CommandBase:
    def __init__(self):
        self.called = False

    def __call__(self):
        self.called = True


@Command(
    "info",
    description="Shows info to the given ticket."
)
class JiraIssueInfoCommand(CommandBase):
    pass


@Command(
    "create",
    description="Creates new ticket"
)
class JiraIssueCreateCommand(CommandBase):
    pass


@Command(
    "issue",
    subcommands=(JiraIssueInfoCommand, JiraIssueCreateCommand)
)
class JiraIssueCommand(CommandBase):
    issue_key: NamedArgument(type=str, name="key", required=False)


@Command(
    "jira",
    subcommands=(JiraIssueCommand,)
)
class JiraCommand(CommandBase):
    pass


def test_parent_parsing_with_subcommand():
    parsed_arguments = JiraCommand.__cli__.parser.parse(["issue", "-k", "ABC-1234", "info"])
    instance = JiraCommand(parsed_arguments)
    info_command, issue_command, jira_command = instance.__cli_run__()

    assert_same(expected=instance, actual=jira_command)
    assert_false(actual=jira_command.called)
    assert_equals(expected="ABC-1234", actual=issue_command.issue_key)
    assert_false(actual=issue_command.called)
    assert_true(actual=info_command.called)


def test_empty_parent_parsing_with_subcommand():
    parsed_arguments = cli_data(JiraCommand).parser.parse(["issue", "create"])
    instance = JiraCommand(parsed_arguments)
    create_command, issue_command, jira_command = instance.__cli_run__()

    assert_same(expected=instance, actual=jira_command)
    assert_false(actual=jira_command.called)
    assert_none(issue_command.issue_key)
    assert_false(actual=issue_command.called)
    assert_true(actual=create_command.called)


@patch('sys.stdout')
@pytest.mark.parametrize(
    "args, output",
    [
        (["-h"], JiraCommand),
        (["issue", "-h"], JiraIssueCommand),
        (["issue", "create", "-h"], JiraIssueCreateCommand),
        (["-h", "issue", "create", "-h"], JiraCommand),
        (["issue", "-h", "create", "-h"], JiraIssueCommand)
    ]
)
def test_help(
        mock_stdout: MagicMock,
        args: List[str],
        output: Type[CommandBase]
):
    try:
        parsed_arguments = JiraCommand.__cli__.parser.parse(args)
        JiraCommand(parsed_arguments).__cli_run__()

    except SystemExit as e:
        assert_equals(expected=0, actual=e.code)
        assert_equals(
            actual=mock_stdout.mock_calls[0].args[0],
            expected=cli_data(output).parser.help()
        )
