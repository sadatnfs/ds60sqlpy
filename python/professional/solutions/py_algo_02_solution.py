"""Reference implementation and exact boundary checks for python-algo-02."""

from bisect import bisect_left, bisect_right
from collections.abc import Callable


def stable_score_order(records: list[tuple[int, str]]) -> list[tuple[int, str]]:
    return sorted(records, key=lambda record: record[0])


def lower_bound(values: list[int], target: int) -> int:
    lo, hi = 0, len(values)
    while lo < hi:
        mid = (lo + hi) // 2
        if values[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def upper_bound(values: list[int], target: int) -> int:
    lo, hi = 0, len(values)
    while lo < hi:
        mid = (lo + hi) // 2
        if values[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def count_closed_range(values: list[int], lower: int, upper: int) -> int:
    if lower > upper:
        raise ValueError("Range lower bound must not exceed upper bound")
    return upper_bound(values, upper) - lower_bound(values, lower)


def merge_runs(left: list[tuple[int, str]], right: list[tuple[int, str]]) -> list[tuple[int, str]]:
    for run in [left, right]:
        if any(run[index][0] > run[index + 1][0] for index in range(len(run) - 1)):
            raise ValueError("Each input run must be sorted by score")
    i = j = 0
    result = []
    while i < len(left) and j < len(right):
        if left[i][0] <= right[j][0]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def merge_sort(records: list[tuple[int, str]]) -> list[tuple[int, str]]:
    runs = [[record] for record in records]
    if not runs:
        return []
    while len(runs) > 1:
        next_runs = []
        for index in range(0, len(runs), 2):
            next_runs.append(
                merge_runs(runs[index], runs[index + 1]) if index + 1 < len(runs) else runs[index]
            )
        runs = next_runs
    return runs[0]


def expect_value_error(call: Callable[[], object]) -> None:
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main() -> None:
    # Exercise 1: Keep identities stable on ties
    records = [(2, "z"), (1, "b"), (2, "a")]
    original = records.copy()
    assert stable_score_order(records) == [(1, "b"), (2, "z"), (2, "a")] and records == original
    empty: list[tuple[int, str]] = []
    assert stable_score_order(empty) == [] and stable_score_order(empty) is not empty
    # Exercise 2: Find the first not-less boundary
    values = [1, 2, 2, 5]
    assert (
        lower_bound(values, 2) == 1 and lower_bound(values, 0) == 0 and lower_bound(values, 9) == 4
    )
    assert lower_bound([], 2) == 0
    for target in range(7):
        assert lower_bound(values, target) == bisect_left(values, target)
    # Exercise 3: Move past all equal values
    values = [1, 2, 2, 5]
    assert (
        upper_bound(values, 2) == 3 and upper_bound([2, 2, 2], 2) == 3 and upper_bound([], 2) == 0
    )
    for target in range(7):
        assert upper_bound(values, target) == bisect_right(values, target)
    # Exercise 4: Count an inclusive interval using boundaries
    values = [1, 2, 2, 5, 7]
    assert count_closed_range(values, 2, 5) == 3 and count_closed_range(values, 3, 4) == 0
    assert count_closed_range(values, 2, 2) == 2 and count_closed_range([], 0, 9) == 0
    expect_value_error(lambda: count_closed_range(values, 5, 2))
    # Exercise 5: Merge sorted runs stably
    left = [(1, "L1"), (2, "L2")]
    right = [(1, "R1"), (3, "R3")]
    assert merge_runs(left, right) == [(1, "L1"), (1, "R1"), (2, "L2"), (3, "R3")]
    assert left == [(1, "L1"), (2, "L2")] and merge_runs([], right) == right
    expect_value_error(lambda: merge_runs([(2, "a"), (1, "b")], []))
    # Exercise 6: Build stable sorting from repeated merges
    records = [(3, "a"), (1, "b"), (2, "c"), (1, "d"), (0, "e")]
    assert merge_sort(records) == [(0, "e"), (1, "b"), (1, "d"), (2, "c"), (3, "a")]
    assert merge_sort(records) == stable_score_order(records) and records[0] == (3, "a")
    assert merge_sort([]) == [] and merge_sort([(1, "x")]) == [(1, "x")]
    for size in range(12):
        sample = [(index % 3, str(index)) for index in range(size - 1, -1, -1)]
        assert merge_sort(sample) == stable_score_order(sample)
    print("python-algo-02: all six normal and boundary contracts passed")


if __name__ == "__main__":
    main()
