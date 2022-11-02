from commons.console.cli_direct import Command, Argument, run_command, PositionalArgument


@Command(
    name="A",
    description="Subcommand A"
)
class A:
    option: Argument(
        short="o",
        long="option",
        type=str,
        required=True
    )

    def __init__(self):
        print(type(self), "__init__", self.option)

    def __call__(self, *args, **kwargs):
        print("__call__", self.__cli_name__)


@Command(
    name="B",
    description="Subcommand B"
)
class B:
    option: Argument(
        short="o",
        long="option",
        type=str
    )

    def __init__(self):
        print(type(self), "__init__", self.option)

    def __call__(self, *args, **kwargs):
        print("__call__", self.__cli_name__)


@Command(
    name="C",
    description="Subcommand C"
)
class C:
    option: Argument(
        short="o",
        long="option",
        type=str
    )

    def __init__(self):
        print(type(self), "__init__", self.option)

    def __call__(self, *args, **kwargs):
        print("__call__", self.__cli_name__)


@Command(
    name="D",
    description="Subcommand D"
)
class D:
    option: Argument(
        short="o",
        long="option",
        type=str
    )

    def __init__(self):
        print(type(self), "__init__", self.option)

    def __call__(self, *args, **kwargs):
        print("__call__", self.__cli_name__)


@Command(
    name="E",
    description="Subcommand E"
)
class E:
    option: Argument(
        short="o",
        long="option",
        type=str
    )

    def __init__(self):
        print(type(self), "__init__", self.option)

    def __call__(self, *args, **kwargs):
        print("__call__", self.__cli_name__)


@Command(
    name="F",
    description="Subcommand F"
)
class F:
    option: Argument(
        short="o",
        long="option",
        type=str
    )

    def __init__(self):
        print(type(self), "__init__", self.option)

    def __call__(self, *args, **kwargs):
        print("__call__", self.__cli_name__)


@Command(
    name="demo1",
    subcommands=(A, B, C),
    description="Demo1 command with subcommands"
)
class Demo1:
    def __init__(self):
        print(type(self), "__init__")

    def __call__(self, *args, **kwargs):
        print("__call__", self.__cli_name__)


@Command(
    name="demo2",
    subcommands=(D, E, F),
    description="Demo2 command with subcommands"
)
class Demo2:
    def __init__(self):
        print(type(self), "__init__")

    def __call__(self, *args, **kwargs):
        print("__call__", self.__cli_name__)


@Command(
    name="core",
    subcommands=(Demo1, Demo2),
    description="Core command with demo commands"
)
class Core:
    message: Argument(
        short="m",
        long="message",
        type=str,
        description="A message which can be used in core.",
        required=True
    )
    message2: Argument(
        short="m2",
        long="message2",
        type=str,
        description="A message 2 which can be used in core."
    )

    message3: PositionalArgument(
        type=str,
        description="Positional argument which must be given"
    )

    def __init__(self):
        print(type(self), "__init__", self.message)

    def __call__(self, *args, **kwargs):
        print("__call__", self.__cli_name__)


run_command(
    Core,
    ["program_dummy", "core", "-m", "core message", "m3", "demo1", "A", "-o", "An option"],
    interactive=True
)
