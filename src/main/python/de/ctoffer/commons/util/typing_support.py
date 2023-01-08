from typing import Iterable, List, Tuple, Set, Union, Type, Any, get_args, get_origin


class FlatMap:
    def __getitem__(self, item):
        return item


_REVERSE_ORIGIN = {list: List, tuple: Tuple, set: Set, Union: FlatMap()}


def expand_type_combinations(
        types_to_expand: Iterable[Type[Any]]
) -> Iterable[Type[Any]]:
    # FIXME (Ctoffer): This implementation is not robust
    #                 expand_type_combinations((List[Tuple[Union[int, float], Union[bool, str]]],))
    #                 will not result in
    #                 List[Tuple[int, bool]], List[Tuple[int, str]], List[Tuple[float, bool]], List[Tuple[float, str]]
    result = list()

    for type_to_expand in types_to_expand:
        generic_args = get_args(type_to_expand)

        if len(generic_args) > 0:
            container = _REVERSE_ORIGIN[get_origin(type_to_expand)]
            expanded_types = expand_type_combinations(generic_args)
            result.extend(container[expanded_type] for expanded_type in expanded_types)
        else:
            result.append(type_to_expand)

    return result
