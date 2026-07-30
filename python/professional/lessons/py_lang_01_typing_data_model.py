"""python-lang-01 learner lab: typing and the Python data model."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from typing import Generic, Literal, TypeVar, overload

T = TypeVar("T")


@overload
def parse_scalar(text: str, kind: Literal["int"]) -> int: ...


@overload
def parse_scalar(text: str, kind: Literal["bool"]) -> bool: ...


@overload
def parse_scalar(text: str, kind: Literal["text"]) -> str: ...


def parse_scalar(
    text: str,
    kind: Literal["int", "bool", "text"],
) -> int | bool | str:
    """TODO: implement the runtime behavior promised by the overloads."""

    raise NotImplementedError("complete parse_scalar")


class Batches(Generic[T], Iterator[tuple[T, ...]]):
    """Iterator exercise that makes ``iter`` and ``next`` explicit."""

    def __init__(self, items: Sequence[T], size: int) -> None:
        if size < 1:
            raise ValueError("size must be positive")
        self._items = items
        self._size = size
        self._offset = 0

    def __iter__(self) -> Batches[T]:
        return self

    def __next__(self) -> tuple[T, ...]:
        """TODO: return the next tuple and raise StopIteration when exhausted."""

        raise NotImplementedError("complete Batches.__next__")


def self_check() -> None:
    for label, call in (
        ("overloaded parser", lambda: parse_scalar("12", "int")),
        ("iterator protocol", lambda: list(Batches([1, 2, 3], 2))),
    ):
        try:
            print(label, "->", call())
        except NotImplementedError:
            print("TODO:", label)


if __name__ == "__main__":
    self_check()
