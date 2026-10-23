"""Reference implementation and exact boundary checks for python-algo-04."""

import math
from bisect import bisect_right
from collections.abc import Callable


def stair_paths(steps: int) -> int:
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 0:
        raise ValueError("Expected a nonnegative integer step count")
    previous, current = 1, 1
    for _ in range(steps):
        previous, current = current, previous + current
    return previous


def minimum_coins(coins: list[int], amount: int) -> int | None:
    if (
        isinstance(amount, bool)
        or not isinstance(amount, int)
        or amount < 0
        or any(isinstance(c, bool) or not isinstance(c, int) or c <= 0 for c in coins)
    ):
        raise ValueError("Expected positive integer coins and nonnegative amount")
    best = [0] + [math.inf] * amount
    for total in range(1, amount + 1):
        best[total] = min(
            (1 + best[total - coin] for coin in coins if coin <= total), default=math.inf
        )
    return None if math.isinf(best[amount]) else int(best[amount])


def coin_plan(coins: list[int], amount: int) -> list[int] | None:
    minimum_coins(coins, amount)
    denominations = sorted(set(coins))
    best = [0] + [math.inf] * amount
    choice: list[int | None] = [None] * (amount + 1)
    for total in range(1, amount + 1):
        for coin in denominations:
            if coin <= total and 1 + best[total - coin] < best[total]:
                best[total] = 1 + best[total - coin]
                choice[total] = coin
    if math.isinf(best[amount]):
        return None
    result = []
    remaining = amount
    while remaining:
        chosen_coin = choice[remaining]
        assert chosen_coin is not None
        result.append(chosen_coin)
        remaining -= chosen_coin
    return sorted(result)


def edit_distance(left: str, right: str) -> int:
    if len(right) > len(left):
        left, right = right, left
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(current[j - 1] + 1, previous[j] + 1, previous[j - 1] + (a != b)))
        previous = current
    return previous[-1]


def knapsack_value(weights: list[int], values: list[int], capacity: int) -> int:
    if (
        isinstance(capacity, bool)
        or not isinstance(capacity, int)
        or capacity < 0
        or len(weights) != len(values)
        or any(isinstance(w, bool) or not isinstance(w, int) or w <= 0 for w in weights)
        or any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in values)
    ):
        raise ValueError("Expected valid 0/1 items and capacity")
    best = [0] * (capacity + 1)
    for weight, value in zip(weights, values, strict=True):
        for available in range(capacity, weight - 1, -1):
            best[available] = max(best[available], value + best[available - weight])
    return best[capacity]


def weighted_schedule(jobs: list[tuple[int, int, int, str]]) -> tuple[int, list[str]]:
    seen = set()
    for start, end, value, ident in jobs:
        if (
            any(isinstance(x, bool) or not isinstance(x, int) for x in [start, end, value])
            or start >= end
            or value < 0
            or not isinstance(ident, str)
            or ident in seen
        ):
            raise ValueError(
                "Expected positive intervals, nonnegative values and unique string IDs"
            )
        seen.add(ident)
    ordered = sorted(jobs, key=lambda job: (job[1], job[0], job[3]))
    ends = [job[1] for job in ordered]
    best = [0] * (len(ordered) + 1)
    take = [False] * (len(ordered) + 1)
    previous = [0] * (len(ordered) + 1)
    for i, (start, _end, value, _ident) in enumerate(ordered, 1):
        compatible = bisect_right(ends, start, 0, i - 1)
        previous[i] = compatible
        candidate = value + best[compatible]
        if candidate > best[i - 1]:
            best[i] = candidate
            take[i] = True
        else:
            best[i] = best[i - 1]
    chosen = []
    i = len(ordered)
    while i:
        if take[i]:
            chosen.append(ordered[i - 1][3])
            i = previous[i]
        else:
            i -= 1
    return best[-1], list(reversed(chosen))


def expect_value_error(call: Callable[[], object]) -> None:
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main() -> None:
    # Exercise 1: Define the empty-state identity
    assert [stair_paths(n) for n in [0, 1, 2, 5]] == [1, 1, 2, 8]
    for n in range(2, 20):
        assert stair_paths(n) == stair_paths(n - 1) + stair_paths(n - 2)
    expect_value_error(lambda: stair_paths(-1))
    expect_value_error(lambda: stair_paths(True))
    # Exercise 2: Distinguish impossible from zero cost
    assert minimum_coins([1, 3, 4], 6) == 2 and minimum_coins([2, 4], 3) is None
    assert minimum_coins([], 0) == 0 and minimum_coins([], 2) is None
    expect_value_error(lambda: minimum_coins([0, 1], 2))
    expect_value_error(lambda: minimum_coins([True], 2))
    # Exercise 3: Reconstruct an optimal payment
    plan = coin_plan([4, 1, 3], 6)
    assert plan == [3, 3] and sum(plan) == 6 and len(plan) == minimum_coins([1, 3, 4], 6)
    assert coin_plan([], 0) == [] and coin_plan([2, 4], 3) is None
    expect_value_error(lambda: coin_plan([-1, 2], 3))
    # Exercise 4: Design a prefix recurrence
    assert edit_distance("kitten", "sitting") == 3 and edit_distance("", "abc") == 3
    assert edit_distance("same", "same") == 0 and edit_distance("ab", "ba") == 2
    assert edit_distance("abc", "ax") == edit_distance("ax", "abc")
    # Exercise 5: Preserve the at-most-once constraint
    assert knapsack_value([2, 3, 4], [4, 5, 7], 5) == 9
    assert knapsack_value([2], [3], 4) == 3 and knapsack_value([], [], 4) == 0
    assert knapsack_value([2], [3], 0) == 0
    expect_value_error(lambda: knapsack_value([0], [3], 4))
    expect_value_error(lambda: knapsack_value([2], [3, 4], 4))
    # Exercise 6: Combine binary search, recurrence and backpointers
    jobs = [(0, 2, 4, "a"), (2, 4, 4, "b"), (1, 4, 7, "c")]
    value, chosen = weighted_schedule(jobs)
    assert (value, chosen) == (8, ["a", "b"])
    selected = [next(job for job in jobs if job[3] == ident) for ident in chosen]
    assert sum(job[2] for job in selected) == value and all(
        a[1] <= b[0] for a, b in zip(selected, selected[1:], strict=False)
    )
    assert weighted_schedule([]) == (0, [])
    expect_value_error(lambda: weighted_schedule([(0, 0, 1, "a")]))
    expect_value_error(lambda: weighted_schedule([(0, 1, 1, "a"), (2, 3, 1, "a")]))
    print("python-algo-04: all six normal and boundary contracts passed")


if __name__ == "__main__":
    main()
