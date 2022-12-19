import argparse
import pathlib
from typing import TypeVar, Generic, Callable, Iterable, Tuple, Set, List, Generator

T = TypeVar('T')
C = TypeVar('C', List, Set, Tuple)


class MapperAction(argparse.Action, Generic[T]):
    def __init__(
            self,
            mapper: Callable[[str], T],
            **kwargs
    ):
        super().__init__(**kwargs)
        self._mapper = mapper

    def __call__(
            self,
            current_parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            values,
            option_string=None
    ):
        setattr(namespace, self.dest, self._mapper(values))


class CollectionMapperAction(argparse.Action, Generic[C]):
    def __init__(
            self,
            collection_mapper: Callable[[Iterable[T]], C],
            mapper: Callable[[str], T],
            **kwargs
    ):
        super().__init__(**kwargs)
        self._collection_mapper = collection_mapper
        self._mapper = mapper

    def __call__(
            self,
            current_parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            values,
            option_string=None
    ):
        setattr(namespace, self.dest, self._collection_mapper(self._mapper(value) for value in values))


def create_simple_action(
        mapper: Callable[[str], T]
) -> MapperAction[T]:
    class MapperActionImpl(MapperAction[T]):
        def __init__(self, **kwargs):
            super().__init__(mapper=mapper, **kwargs)

    return MapperActionImpl[T]


def create_collection_action(
        collection_mapper: Callable[[Iterable[T]], C],
        mapper: Callable[[str], T]
) -> CollectionMapperAction[C]:
    class MapperActionImpl(CollectionMapperAction[C]):
        def __init__(self, **kwargs):
            super().__init__(collection_mapper=collection_mapper, mapper=mapper, **kwargs)

    return MapperActionImpl[C]


_BOOL_MAPPING = {
    "true": True,
    "yes": True,
    "false": False,
    "no": False,
}

_SIMPLE_MAPPER = {
    int: int,
    float: float,
    bool: lambda s: _BOOL_MAPPING[s.lower()],
    str: lambda s: s,
    pathlib.Path: pathlib.Path
}

IntMapperAction = create_simple_action(int)
FloatMapperAction = create_simple_action(float)
BoolMapperAction = create_simple_action(lambda s: _BOOL_MAPPING[s.lower()])
StrMapperAction = create_simple_action(lambda s: s)
PathMapperAction = create_simple_action(pathlib.Path)

# TODO (Ctoffer): Code duplications because of wrong Typing ... need to solve Generic of Generic
IntSetMapperAction = create_collection_action(set, _SIMPLE_MAPPER[int])
FloatSetMapperAction = create_collection_action(set, _SIMPLE_MAPPER[float])
BoolSetMapperAction = create_collection_action(set, _SIMPLE_MAPPER[bool])
StrSetMapperAction = create_collection_action(set, _SIMPLE_MAPPER[str])
PathSetMapperAction = create_collection_action(set, _SIMPLE_MAPPER[pathlib.Path])

IntTupleMapperAction = create_collection_action(tuple, _SIMPLE_MAPPER[int])
FloatTupleMapperAction = create_collection_action(tuple, _SIMPLE_MAPPER[float])
BoolTupleMapperAction = create_collection_action(tuple, _SIMPLE_MAPPER[bool])
StrTupleMapperAction = create_collection_action(tuple, _SIMPLE_MAPPER[str])
PathTupleMapperAction = create_collection_action(tuple, _SIMPLE_MAPPER[pathlib.Path])

IntListMapperAction = create_collection_action(list, _SIMPLE_MAPPER[int])
FloatListMapperAction = create_collection_action(list, _SIMPLE_MAPPER[float])
BoolListMapperAction = create_collection_action(list, _SIMPLE_MAPPER[bool])
StrListMapperAction = create_collection_action(list, _SIMPLE_MAPPER[str])
PathListMapperAction = create_collection_action(list, _SIMPLE_MAPPER[pathlib.Path])
