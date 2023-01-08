from dataclasses import dataclass
from typing import Dict, Callable

from commons.console.cli.parser import ArgParser


@dataclass(init=False, frozen=False)
class CliInternalData:
    name: str
    description: str
    subcommands: Dict[str, Callable]
    create_subparser: Callable
    parser: ArgParser
