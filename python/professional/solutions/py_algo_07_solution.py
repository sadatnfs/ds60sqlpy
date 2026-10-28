"""Standalone references for python-algo-07: exact and approximate streaming state."""

import heapq
import math
import random
from collections.abc import Callable, Iterable, Iterator
from fractions import Fraction
from typing import TypeVar

T = TypeVar("T")
Moments = tuple[int, float, float]


def _finite_number(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Expected a finite real number, excluding bool")
    try:
        result = float(value)
    except OverflowError as error:
        raise ValueError("Value exceeds floating range") from error
    if not math.isfinite(result):
        raise ValueError("Expected a finite number")
    return result


def _state(state: Moments) -> Moments:
    if not isinstance(state, tuple) or len(state) != 3:
        raise ValueError("Expected a (count, mean, M2) tuple")
    count, mean, m2 = state
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError("Count must be a nonnegative integer")
    mean, m2 = _finite_number(mean), _finite_number(m2)
    if m2 < 0 or (count == 0 and (mean != 0 or m2 != 0)) or (count == 1 and m2 != 0):
        raise ValueError("Invalid moment state")
    return count, mean, m2


def _size(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("Expected a nonnegative integer size")
    return value


def moments(values: Iterable[float]) -> Moments:
    count, mean, m2 = 0, 0.0, 0.0
    for raw in values:
        value = _finite_number(raw)
        count += 1
        delta = value - mean
        mean += delta / count
        m2 += delta * (value - mean)
        if not math.isfinite(mean) or not math.isfinite(m2) or m2 < 0:
            raise ValueError("Moment update exceeds the finite nonnegative-state contract")
    return count, mean, m2


def merge_moments(left: Moments, right: Moments) -> Moments:
    na, ma, m2a = _state(left)
    nb, mb, m2b = _state(right)
    if na == 0:
        return nb, mb, m2b
    if nb == 0:
        return na, ma, m2a
    count = na + nb
    delta = mb - ma
    mean = ma + delta * (nb / count)
    m2 = m2a + m2b + delta * delta * (na * (nb / count))
    if not math.isfinite(mean) or not math.isfinite(m2):
        raise ValueError("Merged moments exceed finite floating range")
    return count, mean, m2


def sample_variance(state: Moments) -> float | None:
    count, _, m2 = _state(state)
    return None if count < 2 else m2 / (count - 1)


def stable_top_k(records: Iterable[tuple[int, str]], k: int) -> list[tuple[int, str]]:
    k = _size(k)
    heap: list[tuple[int, int, str]] = []
    for position, record in enumerate(records):
        if not isinstance(record, (tuple, list)) or len(record) != 2:
            raise ValueError("Expected an integer score and string payload")
        score, label = record
        if isinstance(score, bool) or not isinstance(score, int) or not isinstance(label, str):
            raise ValueError("Expected an integer score and string payload")
        if k == 0:
            continue
        candidate = (score, -position, label)
        if len(heap) < k:
            heapq.heappush(heap, candidate)
        elif candidate > heap[0]:
            heapq.heapreplace(heap, candidate)
    return [(score, label) for score, _, label in sorted(heap, reverse=True)]


def prefix_medians(values: Iterable[int]) -> Iterator[Fraction]:
    lower: list[int] = []
    upper: list[int] = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("Exact medians require integer values")
        if not lower or value <= -lower[0]:
            heapq.heappush(lower, -value)
        else:
            heapq.heappush(upper, value)
        if len(lower) > len(upper) + 1:
            heapq.heappush(upper, -heapq.heappop(lower))
        elif len(upper) > len(lower):
            heapq.heappush(lower, -heapq.heappop(upper))
        if len(lower) > len(upper):
            yield Fraction(-lower[0])
        else:
            yield Fraction(-lower[0] + upper[0], 2)


def reservoir_sample(values: Iterable[T], k: int, rng: random.Random) -> list[T]:
    k = _size(k)
    if type(rng) is not random.Random:
        raise ValueError("Expected an explicit random.Random generator")
    result: list[T] = []
    for position, value in enumerate(values):
        if position < k:
            result.append(value)
        elif k:
            slot = rng.randrange(position + 1)
            if slot < k:
                result[slot] = value
    return result


def expect_value_error(call: Callable[[], object]) -> None:
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main() -> None:
    state = moments(iter([2.0, 4.0, 6.0]))
    assert state == (3, 4.0, 8.0) and moments([]) == (0, 0.0, 0.0)
    merged = merge_moments(moments([2.0]), moments([4.0, 6.0]))
    assert merged == state and merge_moments(state, moments([])) == state
    assert sample_variance(state) == 4.0 and sample_variance(moments([9])) is None
    expect_value_error(lambda: moments([math.inf]))
    expect_value_error(lambda: sample_variance((1, 2.0, 1.0)))
    records = [(5, "first"), (7, "best"), (5, "second"), (5, "third")]
    assert stable_top_k(iter(records), 3) == [(7, "best"), (5, "first"), (5, "second")]
    assert stable_top_k([], 4) == []
    expect_value_error(lambda: stable_top_k([(True, "bad")], 0))
    assert list(prefix_medians([5, 1, 9, 3])) == [
        Fraction(5),
        Fraction(3),
        Fraction(5),
        Fraction(4),
    ]
    expect_value_error(lambda: list(prefix_medians([True])))
    rng = random.Random(202)
    checkpoint = rng.getstate()
    sample = reservoir_sample(range(30), 4, rng)
    rng.setstate(checkpoint)
    assert reservoir_sample(range(30), 4, rng) == sample
    assert len(sample) == 4 and len(set(sample)) == 4
    assert reservoir_sample([1, 2], 5, random.Random(0)) == [1, 2]
    assert reservoir_sample(range(20), 0, random.Random(0)) == []
    expect_value_error(lambda: reservoir_sample([], -1, random.Random(0)))
    print("python-algo-07: six moment, selection, median and sampling contracts passed")


if __name__ == "__main__":
    main()
