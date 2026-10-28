"""Executable references for python-lang-03, including explicit ownership."""

from __future__ import annotations

from collections.abc import Callable, Generator, Iterable, Iterator
from contextlib import closing
from io import StringIO
from itertools import islice
from typing import Any


def _count(value: object, *, positive: bool = False) -> int:
    if type(value) is not int or value < (1 if positive else 0):
        raise ValueError(
            "Expected a positive integer" if positive else "Expected a nonnegative integer"
        )
    return value


# Exercise 1: Consume an exact prefix.
def take_exact(source: Iterator[int], count: int) -> tuple[int, ...]:
    _count(count)
    values = []
    for _ in range(count):
        try:
            values.append(next(source))
        except StopIteration as error:
            raise ValueError("Source ended before the requested count") from error
    return tuple(values)


# Exercise 2: Yield bounded chunks lazily.
def chunked(source: Iterable[int], size: int) -> Generator[tuple[int, ...], None, None]:
    _count(size, positive=True)

    def generate() -> Generator[tuple[int, ...], None, None]:
        iterator = iter(source)
        while batch := tuple(islice(iterator, size)):
            yield batch

    return generate()


# Exercise 3: Build overlapping neighbors.
def neighbor_pairs(source: Iterable[int]) -> Generator[tuple[int, int], None, None]:
    iterator = iter(source)
    try:
        previous = next(iterator)
    except StopIteration:
        return
    for current in iterator:
        yield previous, current
        previous = current


# Exercise 4: Give a generator explicit ownership.
def text_lines(text: str, events: list[str]) -> Generator[str, None, None]:
    stream = StringIO(text)
    events.append("open")
    try:
        for line in stream:
            yield line.removesuffix("\n")
    finally:
        stream.close()
        events.append("close")


# Exercise 5: Parse without taking resource ownership.
def parse_int_lines(source: Iterator[str]) -> Generator[int, None, None]:
    for number, line in enumerate(source, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            yield int(stripped)
        except ValueError as error:
            raise ValueError(f"invalid integer on line {number}") from error


# Exercise 6: Close an owned early-stop pipeline.
def first_numbers(text: str, count: int, events: list[str]) -> tuple[int, ...]:
    _count(count)
    if count == 0:
        return ()
    with closing(text_lines(text, events)) as lines, closing(parse_int_lines(lines)) as numbers:
        return tuple(islice(numbers, count))


def _raises(kind: type[Exception], action: Callable[[], Any]) -> Exception:
    try:
        action()
    except kind as error:
        return error
    raise AssertionError(f"Expected {kind.__name__}")


def verify_examples() -> None:
    source = iter([4, 5, 6])
    assert take_exact(source, 2) == (4, 5) and next(source) == 6
    assert take_exact(source, 0) == ()
    _raises(ValueError, lambda: take_exact(iter([1, 2]), 3))
    pulled: list[int] = []

    def measured() -> Iterator[int]:
        for value in range(5):
            pulled.append(value)
            yield value

    source = measured()
    chunks = chunked(source, 2)
    assert pulled == []
    assert next(chunks) == (0, 1) and pulled == [0, 1]
    chunks.close()
    assert next(source) == 2
    assert list(chunked([1, 2, 3, 4, 5], 2)) == [(1, 2), (3, 4), (5,)]
    assert list(chunked([], 2)) == []
    _raises(ValueError, lambda: chunked([], 0))
    _raises(ValueError, lambda: chunked([], True))
    assert list(neighbor_pairs([4, 7, 9])) == [(4, 7), (7, 9)]
    assert list(neighbor_pairs([])) == [] and list(neighbor_pairs([4])) == []
    source = iter([1, 2, 3, 4])
    pairs = neighbor_pairs(source)
    assert next(pairs) == (1, 2)
    pairs.close()
    assert next(source) == 3
    events: list[str] = []
    lines = text_lines(" a \n\nb\n", events)
    assert events == [] and list(lines) == [" a ", "", "b"]
    assert events == ["open", "close"]
    events.clear()
    lines = text_lines("a\nb", events)
    assert next(lines) == "a" and events == ["open"]
    lines.close()
    lines.close()
    assert events == ["open", "close"]
    events.clear()
    unstarted = text_lines("a", events)
    unstarted.close()
    assert events == []
    assert list(parse_int_lines(iter([" 2 ", "", "-5"]))) == [2, -5]
    error = _raises(ValueError, lambda: list(parse_int_lines(iter(["", "bad"]))))
    assert str(error) == "invalid integer on line 2"
    events.clear()
    owned_lines = text_lines("bad\n7", events)
    parser = parse_int_lines(owned_lines)
    _raises(ValueError, lambda: next(parser))
    assert events == ["open"] and next(owned_lines) == "7"
    owned_lines.close()
    assert events == ["open", "close"]
    events.clear()
    assert first_numbers("1\n\n2\nbad\n", 2, events) == (1, 2)
    assert events == ["open", "close"]
    events.clear()
    error = _raises(ValueError, lambda: first_numbers("1\n\n2\nbad\n", 3, events))
    assert str(error) == "invalid integer on line 4" and events == ["open", "close"]
    events.clear()
    assert first_numbers("bad", 0, events) == () and events == []
    _raises(ValueError, lambda: first_numbers("1", -1, events))
    assert events == []
    events.clear()
    assert first_numbers("1\n", 5, events) == (1,) and events == ["open", "close"]
    print("All six iterator, laziness, and cleanup contracts passed.")


if __name__ == "__main__":
    verify_examples()
