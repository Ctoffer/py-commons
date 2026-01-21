from dataclasses import dataclass
from pathlib import Path
from typing import Any, get_args

from commons.typed_config import load_config


@dataclass(frozen=True)
class ConfigAttribute:
    host: str
    port: int = 8080
    path: Path | None = None
    extra_attribute: str | None = None


@dataclass
class NestedConfig:
    attribute_1: ConfigAttribute
    attribute_2: ConfigAttribute = ConfigAttribute(host="my_host")


@dataclass
class Pair:
    x: int
    y: int


@dataclass
class JustAnObject:
    day: int
    month: str
    year: int
    hour: int
    minute: int


# nested_config = load_config("sample_config.yml", type_=NestedConfig)
# print(nested_config)

def test_nested_config_with_defaults():
    actual = load_config("sample_config.yml", type_=NestedConfig)
    print(actual)


def test_list_of_objects():
    actual = load_config("list_of_objects.yml", type_=list[Pair])
    assert 5 == len(actual)
    for i in range(1, 5):
        entry = actual[i - 1]
        assert Pair == type(entry), f"expected: Pair, actual: {type(entry)}"
        assert i == entry.x, f"expected: {i}, actual: {entry.x}"
        assert i ** 2 == entry.y, f"expected: {i**2}, actual: {entry.y}"

def test_list_of_dicts():
    actual = load_config("list_of_objects.yml", type_=list[dict[str, Any]], strict=True)
    assert 5 == len(actual)
    for i in range(1, 5):
        entry = actual[i - 1]
        assert dict == type(entry), f"expected: Pair, actual: {type(entry)}"
        assert i == entry['x'], f"expected: {i}, actual: {entry['x']}"
        assert i ** 2 == entry['y'], f"expected: {i ** 2}, actual: {entry['y']}"

def test_just_an_object():
    actual = load_config("just_an_object.yml", type_=JustAnObject)

    assert JustAnObject == type(actual)
    assert 21 == actual.day
    assert "January" == actual.month
    assert 2026 == actual.year
    assert 7 == actual.hour
    assert 39 == actual.minute

    actual = load_config("just_an_object.yml", type_=dict[str, Any], strict=True)
    assert 21 == actual["day"]
    assert "January" == actual["month"]
    assert 2026 == actual["year"]
    assert 7 == actual["hour"]
    assert 39 == actual["minute"]


def test_dict_of_objects():
    actual = load_config("dict_of_objects.yml", type_=dict[str, Pair], strict=True)

    assert 2 == len(actual)
    assert Pair == type(actual["entry_1"])
    assert Pair == type(actual["entry_5"])
    assert 1, 1 == (actual["entry_1"].x, actual["entry_1"].y)
    assert 5, 25 == (actual["entry_5"].x, actual["entry_5"].y)


def main():
    # test_nested_config_with_defaults()
    test_list_of_objects()
    test_list_of_dicts()
    test_just_an_object()
    test_dict_of_objects()



if __name__ == "__main__":
    main()
