from dataclasses import dataclass
from typing import Any, Self


@dataclass(frozen=True)
class ComponentDescriptor:
    type_: type[Any]
    name: str

    def match_score(self, available_descriptor: Self):
        score = 0

        if self.type_ is not None:
            if self.type_ == available_descriptor.type_:
                score += 100
            elif  issubclass(available_descriptor.type_, self.type_):
                score += 50

        if self.name == available_descriptor.name:
            score += 25

        return score


