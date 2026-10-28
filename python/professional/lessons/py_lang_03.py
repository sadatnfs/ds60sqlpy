"""python-lang-03: Iterators, Generator Pipelines, and Resource Lifetime.

Run two offline worked examples, then implement the six separate task functions.
Each classroom Run starts a fresh process; saved source and notes persist.
The opening examples do not call the unimplemented exercises.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator


# Exercise 1: Consume an exact prefix.
# Inputs: A caller-owned iterator and an exact nonnegative integer count.
# Expected: Consume exactly count items and return a tuple, without probing for an additional
# | item or closing the caller iterator. Zero consumes nothing. Reject a malformed count
# | with ValueError before pulling. If the source ends too early, raise ValueError after
# | consuming the available items; consumption cannot be rolled back.
# Verify: From iter([4, 5, 6]), requesting two returns (4, 5) and next(source) is 6.
# | Requesting three from two items raises ValueError. A counted source confirms zero
# | pulls for count 0 or an invalid count.
def take_exact(source: Iterator[int], count: int) -> tuple[int, ...]:
    """Consume an exact prefix.

    See the explicit input, expected, and verification contract above.
    """
    raise NotImplementedError("Implement take_exact")


# Exercise 2: Yield bounded chunks lazily.
# Inputs: An iterable and an exact positive integer chunk size.
# Expected: Validate size when chunked is called, before accessing the source. Return an
# | iterator producing tuples of at most size items, including a final partial chunk. Do
# | not preconsume source elements before the first next call, omit empty chunks, and do
# | not close a caller-owned iterator.
# Verify: The input [1, 2, 3, 4, 5] with size 2 yields (1, 2), (3, 4), (5,). Check the source
# | pull count is 0 at construction and 2 after only the first chunk; size 0 raises
# | immediately.
def chunked(source: Iterable[int], size: int) -> Iterator[tuple[int, ...]]:
    """Yield bounded chunks lazily.

    See the explicit input, expected, and verification contract above.
    """
    raise NotImplementedError("Implement chunked")


# Exercise 3: Build overlapping neighbors.
# Inputs: A finite or unbounded iterable of integers; empty and singleton inputs are allowed.
# Expected: Return a lazy iterator of adjacent overlapping pairs in source order, retaining only
# | one previous value. Empty and singleton inputs yield nothing. The first result
# | consumes two values; each later result consumes exactly one additional value. Leave
# | a caller-owned source open on early close.
# Verify: [4, 7, 9] yields (4, 7), (7, 9). A spy iterator confirms three pulls for two
# | results; after closing the pair generator, the underlying source still yields its
# | next value.
def neighbor_pairs(source: Iterable[int]) -> Iterator[tuple[int, int]]:
    """Build overlapping neighbors.

    See the explicit input, expected, and verification contract above.
    """
    raise NotImplementedError("Implement neighbor_pairs")


# Exercise 4: Give a generator explicit ownership.
# Inputs: A text string and an observation list. The implementation owns a new io.StringIO
# | created inside its generator body.
# Expected: Acquire the StringIO only when iteration first starts and append open. Yield
# | physical lines with exactly one final newline character removed, preserving other
# | spaces and blank lines. Close the stream and append close in finally on exhaustion
# | or explicit generator close. Closing an unstarted generator acquires nothing.
# Verify: For " a \n\nb\n", list output is [" a ", "", "b"] with events ["open", "close"].
# | After one next call the events are ["open"]; generator.close() appends close once.
def text_lines(text: str, events: list[str]) -> Iterator[str]:
    """Give a generator explicit ownership.

    See the explicit input, expected, and verification contract above.
    """
    raise NotImplementedError("Implement text_lines")


# Exercise 5: Parse without taking resource ownership.
# Inputs: A caller-owned iterator of physical text lines, including blank lines and signed
# | decimal integers accepted by int.
# Expected: Lazily skip whitespace-only lines and convert the rest with int. On malformed
# | nonblank input raise ValueError with the message invalid integer on line N, where N
# | counts all physical lines starting at one. Do not close the source, even when
# | parsing fails or the parser is closed.
# Verify: [" 2 ", "", "-5"] yields 2 and -5. ["", "bad"] raises ValueError("invalid integer on
# | line 2"). A tracked source stays open until its owner explicitly closes it.
def parse_int_lines(source: Iterator[str]) -> Iterator[int]:
    """Parse without taking resource ownership.

    See the explicit input, expected, and verification contract above.
    """
    raise NotImplementedError("Implement parse_int_lines")


# Exercise 6: Close an owned early-stop pipeline.
# Inputs: Text and an exact nonnegative requested count. This function owns the text_lines and
# | parse_int_lines generators it creates.
# Expected: Return at most count parsed integers, preserving order and skipping blank lines.
# | Always close owned generators on early stop, exhaustion, or parse failure. Count
# | zero returns () without opening a stream. Invalid counts raise ValueError before
# | acquisition. Malformed content after the requested prefix remains unconsumed.
# Verify: For "1\n\n2\nbad\n", count 2 returns (1, 2) with ["open", "close"]. Count 3 raises
# | the line-4 ValueError with the same balanced events. Count 0 leaves an empty event
# | list.
def first_numbers(text: str, count: int, events: list[str]) -> tuple[int, ...]:
    """Close an owned early-stop pipeline.

    See the explicit input, expected, and verification contract above.
    """
    raise NotImplementedError("Implement first_numbers")


def worked_examples() -> None:
    pulled = []

    def measured():
        for value in (3, 5, 8):
            pulled.append(value)
            yield value

    stream = measured()
    assert pulled == []
    assert next(stream) == 3
    assert pulled == [3]
    assert list(stream) == [5, 8]
    assert list(stream) == []
    print("Pulled once:", pulled)

    from contextlib import closing

    events = []

    def owned_letters():
        events.append("open")
        try:
            yield "a"
            yield "b"
        finally:
            events.append("close")

    with closing(owned_letters()) as letters:
        assert next(letters) == "a"
        assert events == ["open"]
    assert events == ["open", "close"]
    print("Early-stop cleanup:", events)


if __name__ == "__main__":
    worked_examples()
    print("Examples passed. Implement and verify the six separate task functions.")
