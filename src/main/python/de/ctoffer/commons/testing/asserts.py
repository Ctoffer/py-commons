from typing import TypeVar

T = TypeVar('T')


def assert_equals(
        actual: T,
        expected: T
):
    assert expected == actual


def assert_same(
        actual: T,
        expected: T
):
    assert expected is actual


def assert_none(
        actual: T
):
    assert None is actual


def assert_not_none(
        actual: T
):
    assert None is not actual


def assert_true(
        actual: T
):
    assert actual


def assert_false(
        actual: T
):
    assert not actual
