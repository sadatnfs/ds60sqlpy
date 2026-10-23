"""Reference implementation and exact boundary checks for python-algo-01."""

from collections import Counter
from collections.abc import Callable


def pair_comparisons(size: int) -> int:
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise ValueError("Expected a nonnegative integer size")
    count = 0
    for left in range(size):
        for _right in range(left + 1, size):
            count += 1
    return count


def first_duplicate(values: list[int]) -> int | None:
    seen = set()
    for value in values:
        if value in seen:
            return value
        seen.add(value)
    return None


def frequencies(values: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts


def bag_difference(left: list[str], right: list[str]) -> dict[str, int]:
    a = Counter(left)
    b = Counter(right)
    return {key: a[key] - b[key] for key in sorted(a.keys() | b.keys()) if a[key] != b[key]}


def position_index(values: list[str]) -> dict[str, list[int]]:
    index: dict[str, list[int]] = {}
    for position, value in enumerate(values):
        index.setdefault(value, []).append(position)
    return index


def indexed_pairs(left: list[str], right: list[str]) -> list[tuple[int, int]]:
    index = position_index(right)
    result = []
    for left_position, value in enumerate(left):
        for right_position in index.get(value, []):
            result.append((left_position, right_position))
    return result


def expect_value_error(call: Callable[[], object]) -> None:
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main() -> None:
    # Exercise 1: Count work rather than guessing from timing
    assert [pair_comparisons(n) for n in [0, 1, 4, 8]] == [0, 0, 6, 28]
    for n in range(20):
        assert pair_comparisons(n) == n * (n - 1) // 2
    expect_value_error(lambda: pair_comparisons(-1))
    expect_value_error(lambda: pair_comparisons(True))
    expect_value_error(lambda: pair_comparisons(2.5))  # type: ignore[arg-type]  # Invalid-type boundary.
    # Exercise 2: Return the first repeated occurrence
    values_2 = [4, 1, 4, 1]
    assert first_duplicate(values_2) == 4 and values_2 == [4, 1, 4, 1]
    assert first_duplicate([1, 2, 2, 1]) == 2 and first_duplicate([0, 0]) == 0
    assert first_duplicate([]) is None and first_duplicate([1, 2, 3]) is None
    # Exercise 3: Build counts while preserving first appearance
    values_3 = ["b", "a", "b", "c", "a", "b"]
    result_3 = frequencies(values_3)
    assert list(result_3) == ["b", "a", "c"] and result_3 == {"b": 3, "a": 2, "c": 1}
    assert sum(result_3.values()) == len(values_3) and frequencies([]) == {}
    # Exercise 4: Reconcile occurrences in both directions
    assert bag_difference(["a", "a", "b"], ["a", "b", "b"]) == {"a": 1, "b": -1}
    assert bag_difference(["b", "a"], ["a", "b"]) == {}
    assert bag_difference([], ["x", "x"]) == {"x": -2}
    # Exercise 5: Index every occurrence instead of overwriting
    values_5 = ["a", "b", "a"]
    result_5 = position_index(values_5)
    assert result_5 == {"a": [0, 2], "b": [1]} and list(result_5) == ["a", "b"]
    assert sorted(position for positions in result_5.values() for position in positions) == list(
        range(len(values_5))
    )
    assert position_index([]) == {}
    # Exercise 6: Produce an output-sensitive equality join
    assert indexed_pairs(["a", "a", "b"], ["a", "b", "a"]) == [
        (0, 0),
        (0, 2),
        (1, 0),
        (1, 2),
        (2, 1),
    ]
    assert indexed_pairs(["a"], ["b"]) == []
    assert len(indexed_pairs(["a", "a"], ["a", "a"])) == 4
    assert indexed_pairs([], []) == []
    print("python-algo-01: all six normal and boundary contracts passed")


if __name__ == "__main__":
    main()
