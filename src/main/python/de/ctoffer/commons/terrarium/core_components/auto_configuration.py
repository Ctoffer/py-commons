from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from commons.terrarium import Terrarium


def auto_configuration(file_name: str | Path, attribute_path: str = None) -> Callable:
    pass


@auto_configuration(file_name="partial_config.yml", attribute_path="partial.attribute1")
@dataclass
class PartialAttribute1Config:
    pass


with Terrarium() as terra:
    instance = terra[PartialAttribute1Config]