from typing import TypeVar

T = TypeVar('T')


def assert_equals(
        actual: T,
        expected: T
):
    assert expected == actual


def assert_none(
        actual: T
):
    assert None is actual


def assert_not_none(
        actual: T
):
    assert None is not actual
