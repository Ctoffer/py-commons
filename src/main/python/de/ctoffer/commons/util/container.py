from typing import Any, Callable, Mapping


def traverse_dict(dictionary: Mapping[Any, Any], key_inspector: Callable[[Mapping[Any, Any], Any, Any], None]):
    stack = [(dictionary, k, v) for k, v in dictionary.items()]

    while stack:
        parent, key, value = stack[0]
        del stack[0]

        if not isinstance(value, dict):
            key_inspector(parent, key, value)
        else:
            for k, v in reversed(value.items()):
                stack.insert(0, (value, k, v))
