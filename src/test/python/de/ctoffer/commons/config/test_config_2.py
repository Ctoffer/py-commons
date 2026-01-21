import datetime
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any

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

@dataclass
class DatetimeTestData:
    date_from_str: datetime.date
    date_from_obj: datetime.date
    time_from_str: datetime.time
    time_from_obj: datetime.time
    datetime_from_str: datetime.datetime
    datetime_from_obj: datetime.datetime

def test_datetime():
    actual = load_config(
        "datetime.yml",
        type_=DatetimeTestData,
        strict=True
    )

    expected_date = datetime.date(2026, 1, 21)
    expected_time = datetime.time(9, 33, 14, 578_000)
    expected_datetime = datetime.datetime.combine(expected_date, expected_time)

    assert expected_date == actual.date_from_str
    assert expected_date == actual.date_from_obj
    assert expected_time == actual.time_from_str
    assert expected_time == actual.time_from_obj
    assert expected_datetime == actual.datetime_from_str
    assert expected_datetime == actual.datetime_from_obj

class Weekday (Enum):
    MONDAY = auto()
    TUESDAY = auto()
    WEDNESDAY = auto()
    THURSDAY = auto()
    FRIDAY = auto()
    SATURDAY = auto()
    SUNDAY = auto()

def test_enum():
    actual = load_config(
        "enum.yml",
        type_=list[Weekday],
        strict=True
    )
    
    assert Weekday.MONDAY == actual[0]
    assert Weekday.TUESDAY == actual[1]
    assert Weekday.WEDNESDAY == actual[2]
    assert Weekday.SATURDAY == actual[3]
    assert Weekday.FRIDAY == actual[4]

@dataclass
class NamingDummy:
    some_long_attribute: int

def test_naming_convention():
    actual = load_config(
        "naming_convention.yml",
        type_=list[NamingDummy],
        strict=True
    )

    assert 1 == actual[0].some_long_attribute
    assert 2 == actual[1].some_long_attribute
    assert 3 == actual[2].some_long_attribute

def main():
    test_nested_config_with_defaults()
    test_list_of_objects()
    test_list_of_dicts()
    test_just_an_object()
    test_dict_of_objects()
    test_datetime()
    test_enum()
    test_naming_convention()

if __name__ == "__main__":
    main()
