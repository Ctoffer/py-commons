from enum import Enum
from typing import Dict

from commons.console.util.console import Console


class InputValidationEvent(Enum):
    REPEAT_OPERATION = 0
    CANCEL_OPERATION = 1
    USE_DEFAULT_INSTEAD = 2
    INPUT_ACCEPTED = 3


class InputValidationFailedHandler:
    def __init__(
            self,
            *args: str,
            event: InputValidationEvent = InputValidationEvent.REPEAT_OPERATION
    ):
        self._info_text = tuple(args)
        self._event = event

    def __call__(
            self,
            context: Dict[str, str]
    ) -> InputValidationEvent:
        console = Console()

        for line in self._info_text:
            console.print(line.format(**context))

        return self._event
