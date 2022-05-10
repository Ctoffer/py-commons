import sys
from typing import List

from commons.scale.command_line import Command, Option, Parameters, execute_command, SubCommand, ParentCommand


@SubCommand()
class MySubCommand:
    parent: ParentCommand['DemoCommand']


@Command(
    name="Demo",
    version="My Version 1.0",
    mixin_standard_help_options=True,
    subcommands=(MySubCommand,)
)
class DemoCommand:
    font_size: int = Option(
        names=("-s", "--font-size"),
        description="Font size",
        default_value="19"
    )

    words: List[str] = Parameters(
        param_label="<word>",
        description="Words for this program",
        default_value="Hello, world"
    )

    def __call__(self, *args, **kwargs):
        print("font_size", self.font_size, "words", self.words)


def main():
    exit_code: int = execute_command(DemoCommand(), sys.argv)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
