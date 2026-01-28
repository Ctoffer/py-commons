from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ComponentDescriptor:
    type_: type[Any]
    name: str

    def match_score(self, key: 'ComponentDescriptor'):
        score = 0

        if self.type_ == key.type_:
            score += 100
        elif issubclass(key.type_, self.type_):
            score += 50

        if self.name == key.name:
            score += 25

        return score


