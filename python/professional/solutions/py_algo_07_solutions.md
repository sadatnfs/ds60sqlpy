# python-algo-07: Explained reference solutions

Compare these answers with an honest attempt at [Streaming Summaries, Order Statistics, and Sampling](../companion-guides/py_algo_07.md). The [standalone executable reference](py_algo_07_solution.py) includes all imports, type scaffolds, helpers and normal/boundary checks in `main()`. The snippets below use that shared context and match the six learner contracts.

## Exercise 1: Accumulate stable one-pass moments

**Contract: `moments`.** Consume an iterable once and return (count, mean, M2), where M2 is the sum of squared deviations from the current mean. Use Welford updates with constant many numeric state fields and do not retain observations. Empty input returns (0, 0.0, 0.0). Accept finite Python int/float values excluding bool, convert to float, and reject invalid values or nonfinite/negative computed state with ValueError.

**Expected:** [2, 4, 6] returns (3, 4.0, 8.0). A constant stream has M2 zero. Inputs around a large offset should be checked against an independent centered calculation, not raw sum-of-squares subtraction.

```python
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
```

Update the count, then use the old-mean delta for the mean adjustment and the new-mean delta for the M2 adjustment. This avoids directly subtracting two large nearly equal sums of squares. It still uses floating arithmetic, so input conversion and accumulation are approximate. Constant many fields does not mean a fixed bit budget for an arbitrarily large Python integer count.

## Exercise 2: Combine unequal chunks without averaging means blindly

**Contract: `merge_moments`.** Accept two valid (count, mean, M2) tuples and return their merged summary without observations. Counts are nonnegative Python integers excluding bool; means and M2 must be finite, M2 nonnegative, empty states exactly (0, 0, 0), and singleton M2 zero. Empty state is an identity. Use the weighted mean and between-group correction; reject invalid or nonfinite results with ValueError.

**Expected:** Merging moments([2]) with moments([4, 6]) matches moments([2, 4, 6]) within tolerance. Averaging chunk means without their counts would give 3.5 instead of 4.

```python
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
```

The correction accounts for different chunk centers. Adding M2 values alone omits the variation between those centers. Mathematical merging is associative, but floating evaluation is not bitwise associative, so compare different partitionings with justified tolerance. A state validator can check the declared structural constraints without proving that a summary truly came from the claimed original data.

## Exercise 3: Distinguish undefined from zero variance

**Contract: `sample_variance`.** Validate the moment-state contract used by merge_moments. Return M2/(count - 1) for count at least two, otherwise None. Preserve the tuple and do not reinterpret an empty or singleton sample as zero variance. Reject invalid states with ValueError. This is an arithmetic sample-variance calculation, not automatic evidence of an unbiased model estimate.

**Expected:** The summary of [2, 4, 6] gives 4.0. Empty and singleton summaries give None; [7, 7] gives 0.0. A singleton state with positive M2 is invalid.

```python
def sample_variance(state: Moments) -> float | None:
    count, _, m2 = _state(state)
    return None if count < 2 else m2 / (count - 1)
```

The denominator count minus one belongs to sample variance. Population variance of a fully observed population would use count instead. Returning None keeps an undefined estimate distinct from observed zero spread. Statistical unbiasedness requires assumptions such as independent identically distributed observations with finite variance; choosing this denominator alone does not establish them.

## Exercise 4: Retain scored records with an explicit tie policy

**Contract: `stable_top_k`.** Consume a one-pass iterable of (Python integer score, string payload) records, excluding bool scores, and retain at most k heap records. k must be a nonnegative Python integer excluding bool. Return up to k records ordered by descending score, with earlier input records first on equal scores. Preserve duplicates and payloads, never sort or retain the full input, and validate records even when k is zero. Invalid input raises ValueError.

**Expected:** [(5, "first"), (7, "best"), (5, "second"), (5, "third")] with k=3 returns [(7, "best"), (5, "first"), (5, "second")]. Equal scores do not sort by payload.

```python
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
```

The heap root must be the worst retained candidate: lowest score, and latest arrival on a tie. A tuple of score and negative position supplies that ordering, while the unique position keeps payload comparisons irrelevant. Replacing only when a new candidate is better preserves earlier ties. Auxiliary retained record count is O(k), extending the earlier value-only heap exercise to stable record identity.

## Exercise 5: Maintain exact order statistics with two heaps

**Contract: `prefix_medians`.** Return a lazy iterator yielding the exact Fraction median after each Python integer input, excluding bool. Use a negated lower min-heap as a max-heap and a normal upper min-heap, keeping lower equal in size to upper or larger by one. Preserve duplicates and use no floating conversion. Empty input yields nothing; invalid items raise ValueError when consumed. Retained heap entries grow with the prefix length.

**Expected:** For [5, 1, 9, 3], yield fractions [5, 3, 5, 4]. For [2**100, 2**100 + 1], the second median is exactly Fraction(2**101 + 1, 2).

```python
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
```

The lower heap root gives the largest lower-half value and the upper root gives the smallest upper-half value. Rebalancing sizes ensures the middle order statistics are exposed. Fractions preserve half-integer answers even far beyond float precision. A generator avoids storing every output, but these two heaps still retain every input value: exact general prefix medians are not a constant-memory summary.

## Exercise 6: Sample positions without knowing stream length

**Contract: `reservoir_sample`.** Consume an arbitrary one-pass iterable with Algorithm R, retaining at most k objects and using the supplied exact random.Random instance. Require nonnegative Python integer k excluding bool; invalid k or generator raises ValueError before consumption. For the t-th item after filling k slots, draw uniformly from range(t) and replace that slot only when it is below k. Return reservoir slot order. k=0 consumes the stream without draws; streams shorter than k return all items in encounter order.

**Expected:** For n >= k, return k sampled positions without replacement; repeated values may appear when positions differ. Saving and restoring rng.getstate() reproduces a run in the same runtime and call sequence. Input objects are retained by reference, not deep-copied.

```python
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
```

At time t, a new item enters with probability k/t. An old retained item survives with probability 1 - 1/t, because exactly one of the t possible draws replaces its slot. Multiplying its previous inclusion probability k/(t-1) by this survival probability gives k/t. A fixed seed demonstrates replay, while exhaustive small draw paths can independently verify uniform subsets without a flaky frequency threshold.

## Independent checks and limits

The reference main exercises every named contract. `tests/test_python_algorithm_modernization.py` adds independent oracles, including explicit graph reachability and exhaustive tiny spanning forests, centered rational moment calculations, sorted-prefix medians and exhaustive reservoir draw paths. Source-level contract checks are separate from semantic execution. A passing reference demonstrates tested behavior, not mastery; explain the invariant and construct a counterexample to a tempting incorrect implementation.
