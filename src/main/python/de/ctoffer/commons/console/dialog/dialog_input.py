from typing import Callable, Dict, TypeVar, Generic, Tuple

from commons.console.dialog.input_validation import InputValidationEvent
from commons.console.util.console import Console

T = TypeVar('T')

class DialogInput(Generic[T]):
    def __init__(
            self,
            *args: str,
            cancel: str = "cancel",
            use_default_when: Callable[[str], bool] = lambda s: False,
            validation: Callable[[str], bool] = lambda s: True,
            on_validation_failed: Callable[[Dict[str, str]], InputValidationEvent] = lambda :InputValidationEvent.CANCEL_OPERATION,
            convert_valid_input: Callable[[str], T] = lambda s: s
    ):
        self._info_text = args
        self._cancel = cancel
        self._use_default_when = use_default_when
        self._validation = validation
        self._on_validation_failed = on_validation_failed
        self._convert_valid_input = convert_valid_input

    @property
    def info_text(self)->Tuple[str]:
        return self._info_text

    @property
    def cancel(self) -> str:
        return self._cancel

    @property
    def use_default_when(self) -> Callable[[str], bool]:
        return self._use_default_when

    @property
    def validation(self) -> Callable[[str], bool]:
        return self._validation

    @property
    def on_validation_failed(self) -> Callable[[], InputValidationEvent]:
        return self._on_validation_failed

    @property
    def convert_valid_input(self) -> Callable[[str], T]:
        return self._convert_valid_input

    def __call__(
            self,
            context: Dict[str, str]
    ) -> Tuple[InputValidationEvent, T]:
        console = Console()

        for line in self._info_text:
            console.print(line.format(**context))

        user_input = console.input(">: ")

        if self._use_default_when(user_input):
            return InputValidationEvent.USE_DEFAULT_INSTEAD, user_input

        try:
            correct = self._validation(user_input)
        except Exception:
            correct = False

        if correct:
            return InputValidationEvent.INPUT_ACCEPTED, self._convert_valid_input(user_input)
        else:
            with console:
                event = self._on_validation_failed(context)
            console.print("")

            if event == InputValidationEvent.INPUT_ACCEPTED:
                raise ValueError("On validation callback returned INPUT_ACCEPTED which is invalid!")

            return event, user_input
