"""python-algo-07: Streaming Summaries, Order Statistics, and Sampling.

Run the worked examples, then implement the six contracts.
Complete answers belong in the reference area.
"""

import random
from collections.abc import Iterable, Iterator
from fractions import Fraction
from typing import TypeVar

T = TypeVar("T")
Moments = tuple[int, float, float]


def moments(values: Iterable[float]) -> Moments:
    """
    Consume an iterable once and return (count, mean, M2), where M2 is the sum of squared
    deviations from the current mean. Use Welford updates with constant many numeric state
    fields and do not retain observations. Empty input returns (0, 0.0, 0.0). Accept finite
    Python int/float values excluding bool, convert to float, and reject invalid values or
    nonfinite/negative computed state with ValueError.
    """
    raise NotImplementedError("Implement moments")


def merge_moments(left: Moments, right: Moments) -> Moments:
    """
    Accept two valid (count, mean, M2) tuples and return their merged summary without
    observations. Counts are nonnegative Python integers excluding bool; means and M2 must
    be finite, M2 nonnegative, empty states exactly (0, 0, 0), and singleton M2 zero. Empty
    state is an identity. Use the weighted mean and between-group correction; reject invalid
    or nonfinite results with ValueError.
    """
    raise NotImplementedError("Implement merge_moments")


def sample_variance(state: Moments) -> float | None:
    """
    Validate the moment-state contract used by merge_moments. Return M2/(count - 1) for
    count at least two, otherwise None. Preserve the tuple and do not reinterpret an empty
    or singleton sample as zero variance. Reject invalid states with ValueError. This is an
    arithmetic sample-variance calculation, not automatic evidence of an unbiased model
    estimate.
    """
    raise NotImplementedError("Implement sample_variance")


def stable_top_k(records: Iterable[tuple[int, str]], k: int) -> list[tuple[int, str]]:
    """
    Consume a one-pass iterable of (Python integer score, string payload) records, excluding
    bool scores, and retain at most k heap records. k must be a nonnegative Python integer
    excluding bool. Return up to k records ordered by descending score, with earlier input
    records first on equal scores. Preserve duplicates and payloads, never sort or retain
    the full input, and validate records even when k is zero. Invalid input raises
    ValueError.
    """
    raise NotImplementedError("Implement stable_top_k")


def prefix_medians(values: Iterable[int]) -> Iterator[Fraction]:
    """
    Return a lazy iterator yielding the exact Fraction median after each Python integer
    input, excluding bool. Use a negated lower min-heap as a max-heap and a normal upper
    min-heap, keeping lower equal in size to upper or larger by one. Preserve duplicates and
    use no floating conversion. Empty input yields nothing; invalid items raise ValueError
    when consumed. Retained heap entries grow with the prefix length.
    """
    raise NotImplementedError("Implement prefix_medians")


def reservoir_sample(values: Iterable[T], k: int, rng: random.Random) -> list[T]:
    """
    Consume an arbitrary one-pass iterable with Algorithm R, retaining at most k objects and
    using the supplied exact random.Random instance. Require nonnegative Python integer k
    excluding bool; invalid k or generator raises ValueError before consumption. For the
    t-th item after filling k slots, draw uniformly from range(t) and replace that slot only
    when it is below k. Return reservoir slot order. k=0 consumes the stream without draws;
    streams shorter than k return all items in encounter order.
    """
    raise NotImplementedError("Implement reservoir_sample")


def worked_examples() -> None:
    from fractions import Fraction

    left = [10, 10]
    right = [20, 20, 20, 20]
    na, nb = len(left), len(right)
    ma, mb = Fraction(sum(left), na), Fraction(sum(right), nb)
    combined_mean = ma + (mb - ma) * Fraction(nb, na + nb)
    between = (mb - ma) ** 2 * Fraction(na * nb, na + nb)
    assert combined_mean == Fraction(50, 3)
    assert between == Fraction(400, 3)
    assert sum((Fraction(value) - combined_mean) ** 2 for value in left + right) == between
    print("Count-weighted mean:", combined_mean, "between-group squared deviation:", between)

    from collections import Counter
    from itertools import product

    # Exhaust all Algorithm R choices for four distinct items and two slots.
    counts = Counter()
    for third_slot, fourth_slot in product(range(3), range(4)):
        reservoir = ["a", "b"]
        if third_slot < 2:
            reservoir[third_slot] = "c"
        if fourth_slot < 2:
            reservoir[fourth_slot] = "d"
        counts[tuple(sorted(reservoir))] += 1
    assert len(counts) == 6 and set(counts.values()) == {2}
    print("Each of six pairs appears on two of twelve equally probable draw paths:", dict(counts))


if __name__ == "__main__":
    worked_examples()
    print("Worked examples passed. Implement all six contracts and record boundary evidence.")

# Exercise 1: Accumulate stable one-pass moments
# Contract: moments
# Prompt: Consume an iterable once and return (count, mean, M2), where M2 is the sum of squared
# deviations from the current mean. Use Welford updates with constant many numeric state fields
# and do not retain observations. Empty input returns (0, 0.0, 0.0). Accept finite Python
# int/float values excluding bool, convert to float, and reject invalid values or
# nonfinite/negative computed state with ValueError.
# Expected: [2, 4, 6] returns (3, 4.0, 8.0). A constant stream has M2 zero. Inputs around a large
# offset should be checked against an independent centered calculation, not raw sum-of-squares
# subtraction.

# Exercise 2: Combine unequal chunks without averaging means blindly
# Contract: merge_moments
# Prompt: Accept two valid (count, mean, M2) tuples and return their merged summary without
# observations. Counts are nonnegative Python integers excluding bool; means and M2 must be
# finite, M2 nonnegative, empty states exactly (0, 0, 0), and singleton M2 zero. Empty state is an
# identity. Use the weighted mean and between-group correction; reject invalid or nonfinite
# results with ValueError.
# Expected: Merging moments([2]) with moments([4, 6]) matches moments([2, 4, 6]) within tolerance.
# Averaging chunk means without their counts would give 3.5 instead of 4.

# Exercise 3: Distinguish undefined from zero variance
# Contract: sample_variance
# Prompt: Validate the moment-state contract used by merge_moments. Return M2/(count - 1) for
# count at least two, otherwise None. Preserve the tuple and do not reinterpret an empty or
# singleton sample as zero variance. Reject invalid states with ValueError. This is an arithmetic
# sample-variance calculation, not automatic evidence of an unbiased model estimate.
# Expected: The summary of [2, 4, 6] gives 4.0. Empty and singleton summaries give None; [7, 7]
# gives 0.0. A singleton state with positive M2 is invalid.

# Exercise 4: Retain scored records with an explicit tie policy
# Contract: stable_top_k
# Prompt: Consume a one-pass iterable of (Python integer score, string payload) records, excluding
# bool scores, and retain at most k heap records. k must be a nonnegative Python integer excluding
# bool. Return up to k records ordered by descending score, with earlier input records first on
# equal scores. Preserve duplicates and payloads, never sort or retain the full input, and
# validate records even when k is zero. Invalid input raises ValueError.
# Expected: [(5, "first"), (7, "best"), (5, "second"), (5, "third")] with k=3 returns [(7,
# "best"), (5, "first"), (5, "second")]. Equal scores do not sort by payload.

# Exercise 5: Maintain exact order statistics with two heaps
# Contract: prefix_medians
# Prompt: Return a lazy iterator yielding the exact Fraction median after each Python integer
# input, excluding bool. Use a negated lower min-heap as a max-heap and a normal upper min-heap,
# keeping lower equal in size to upper or larger by one. Preserve duplicates and use no floating
# conversion. Empty input yields nothing; invalid items raise ValueError when consumed. Retained
# heap entries grow with the prefix length.
# Expected: For [5, 1, 9, 3], yield fractions [5, 3, 5, 4]. For [2**100, 2**100 + 1], the second
# median is exactly Fraction(2**101 + 1, 2).

# Exercise 6: Sample positions without knowing stream length
# Contract: reservoir_sample
# Prompt: Consume an arbitrary one-pass iterable with Algorithm R, retaining at most k objects and
# using the supplied exact random.Random instance. Require nonnegative Python integer k excluding
# bool; invalid k or generator raises ValueError before consumption. For the t-th item after
# filling k slots, draw uniformly from range(t) and replace that slot only when it is below k.
# Return reservoir slot order. k=0 consumes the stream without draws; streams shorter than k
# return all items in encounter order.
# Expected: For n >= k, return k sampled positions without replacement; repeated values may appear
# when positions differ. Saving and restoring rng.getstate() reproduces a run in the same runtime
# and call sequence. Input objects are retained by reference, not deep-copied.
