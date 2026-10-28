# Streaming Summaries, Order Statistics, and Sampling

**Stable ID:** `python-algo-07`. Allow about 150 minutes for reading,
tracing and independent implementation. This estimate is not a deadline.

## How to run this lesson

Run `./classroom` from the repository root and choose **Python** in the shared
`/classroom` directory. Select this unit, read its Python capability notice,
and open the saved coding pad. Windows learners use the same launcher in
WSL 2. Docker supplies the prepared Python Core environment and the required
standard-library modules; no extra package, dataset or service is needed.
Paste the complete [learner script](../lessons/py_algo_07.py), save and Run.
The two worked examples print their observations. The six task functions
remain unimplemented and are not called by the opening demonstrations.

Every browser Run starts a fresh process. Include imports, fixtures and your
checks together, and save the source that reproduces an observation. The
learning volume retains code, notes and results; it does not retain live tree
objects, heap contents or generator state between processes. A successful
opening demonstration is evidence for those examples, not completion of the
six independent implementations.

An optional separately prepared contributor environment can run
`uv run --no-sync python python/professional/lessons/py_algo_07.py`
from the repository root. See [contributor setup](../../../CONTRIBUTING.md)
for that route and the [classroom guide](../../../docs/classroom-experience.md)
for browser persistence. The host checkout and interpreter do not read the
browser's Docker learning volume. All inputs in this lesson are original,
tiny offline fixtures.

## Level and prerequisites

- **Level:** Advanced Python algorithm practice, using Python 3.11-compatible syntax.
- **Direct prerequisite:** `python-31`, [probability and sampling](../../ds-60day/companion-guides/day31_probability_basics.md).
- **Direct prerequisite:** `python-algo-02`, [stable sorting, heaps and greedy invariants](py_algo_02.md).
- **Direct prerequisite:** `python-algo-03`, [graphs, shortest paths and dynamic programming](py_algo_03.md).
- **Artifacts:** [learner](../lessons/py_algo_07.py), [explained answers](../solutions/py_algo_07_solutions.md), [executable reference](../solutions/py_algo_07_solution.py).

## Learning objectives

Accumulate and merge moment summaries without replaying observations, while
separating undefined sample variance from zero. Preserve arrival identity at a
top-k tie, and compute exact prefix medians while accounting for growing heap
state. Sample input positions with Algorithm R, distinguish replay from
independent evidence, and justify the inclusion rule on a bounded fixture.

## Starting point and observable outcome

This unit is `python-algo-07`. Complete `python-31`, `python-algo-02` and `python-algo-03` first. You should understand basic variance and sampling, stable tie ordering, and min-heap operations. Use the Docker classroom's prepared Python Core environment. The programs use only the standard library and bounded offline iterables; no live event system is implied by the word streaming.

You will compute summaries without replaying an input, merge chunk statistics correctly, preserve record identity at a top-k cutoff, produce exact prefix medians, and sample unknown-length input positions. Your evidence must state the retained memory and numerical meaning of each output. A one-pass algorithm is not automatically constant-memory, and a deterministic seed is not a proof of uniform sampling.

## Vocabulary and concepts

- **Mergeable summary:** State that can combine disjoint input chunks for
  one declared calculation without retaining or replaying their observations.
  A moment merge needs each chunk's count, center and squared-deviation sum.
- **Stable cutoff:** A selection rule that preserves the declared order among
  equally ranked records. Here earlier arrivals win equal-score top-k ties,
  regardless of the payload's alphabetical order.
- **Order statistic:** A value defined by sorted position rather than input
  position, such as the median. Producing answers in one pass does not imply
  that an exact order statistic uses bounded retained memory.
- **Reservoir sample:** A bounded set of input positions selected while the
  full stream length is unknown. Equal values at different positions remain
  different eligible observations, and the retained objects are references.

### Stream, summary, merge and order statistic

A **stream** here is an iterable that may be consumable only once. An iterator can yield a value and then forget it. Calling `list(values)` materializes the entire stream and changes the memory contract even if the next calculation is fast. Tests should therefore use one-pass sources rather than only reusable lists.

A **summary state** retains information sufficient for a particular calculation. A count and mean cannot reconstruct every observation. A **mergeable summary** can combine states from disjoint chunks without replaying their original data. An **order statistic** depends on sorted position, such as the median. Exact general medians require much more retained information than a mean and variance summary.

A **reservoir** holds a bounded sample while the total input length remains unknown. Sampling is by input position: equal values at different positions are separate possible observations. Returning duplicate values does not mean a position was selected twice. These distinctions affect both correctness tests and the interpretation of output.

## Welford state and stable updates

The state is a tuple \((n,\mu,M_2)\), where \(n\) is the count, \(\mu\) the mean, and \(M_2\) the sum of squared deviations from that mean. For a new value \(x\), let \(\delta=x-\mu\). Update using

\[
n'=n+1,\qquad \mu'=\mu+\delta/n',\qquad
M_2'=M_2+\delta(x-\mu').
\]

The old and new means have different roles. Reusing the old mean in the final factor produces the wrong recurrence. This approach avoids computing variance as a difference between two large raw sums, which can lose small variation when all values have a large common offset.

The calculation still uses finite floating-point arithmetic. It can round, and sufficiently large intermediate differences can overflow even when each input is finite. The contract rejects a nonfinite or negative computed state rather than quietly claiming a usable variance. Constant many numeric fields also does not mean a fixed bit count: a Python integer count can grow in representation size.

Empty input has the identity state `(0, 0.0, 0.0)`. Sample variance uses \(M_2/(n-1)\) only for \(n\ge2\). Returning `None` for fewer observations distinguishes undefined sample variance from an observed zero variance. The denominator alone does not establish independent observations or an unbiased statistical model.

## Worked example: chunk size affects both mean and spread

Predict whether the combined mean is 15 or closer to 20. This complete rational calculation avoids using the exercise implementation as its own oracle.

```python
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
```

The right chunk has twice as many observations, so the combined mean is \(50/3\), not the simple average of chunk means. Both chunks individually have zero within-chunk spread, yet the combined sample varies because their centers differ. A merge that only adds their two zero M2 values loses all of that between-group variation.

For states \((n_a,\mu_a,M_{2a})\) and \((n_b,\mu_b,M_{2b})\), write \(\Delta=\mu_b-\mu_a\) and \(n=n_a+n_b\). Then

\[
\mu=\mu_a+\Delta n_b/n,\qquad
M_2=M_{2a}+M_{2b}+\Delta^2 n_an_b/n.
\]

Handle an empty chunk before dividing. In exact arithmetic, merging is associative. Floating evaluation can differ across reduction trees, so compare chunkings with tolerance and record the partitioning when exact replay matters. State validation checks declared constraints; it cannot prove that a caller's claimed count and mean correspond to real original records.

## Stable top-k is a record policy

The earlier heap lesson retained numeric values. This unit retains `(integer_score, string_payload)` records and specifies which equal-score records survive the cutoff: earlier arrivals win. The payload is not a secondary alphabetical key, and duplicates remain separate occurrences.

A bounded min-heap should expose the worst retained record at its root. Lower scores are worse; for equal scores, later arrivals are worse. A key `(score, -position, payload)` expresses this because positions are unique. The payload never breaks a tie between distinct records with the same position. Replace the root only when the incoming record is better.

At most \(k\) records are retained during scanning, and sorting only those survivors costs \(O(k\log k)\). The scan costs \(O(n\log k)\) for positive bounded k, with the usual constant-size interpretation when k is one. The output itself also holds up to k records. A zero limit still consumes and validates the source so malformed records do not disappear behind a special case.

## Exact prefix medians need growing state

Maintain the lower half in a max-heap represented by negated integers and the upper half in an ordinary min-heap. Python 3.12 has the required min-heap functions, so no newer max-heap API is needed. Keep the lower heap the same size as the upper heap or larger by one, with every lower value no greater than every upper value.

For an odd prefix, the median is the largest lower value. For an even prefix, it is the average of the largest lower and smallest upper values. Returning `Fraction` preserves an exact half-integer even far beyond float64 precision. Using floating conversion would silently alter the exactness contract.

The function is a generator, so it yields answers as input arrives and does not retain every output. Its heaps nevertheless retain every input value: after t observations, they contain t entries. This is a one-pass exact algorithm with linear retained state, not a bounded quantile sketch. Approximate quantile algorithms trade accuracy for memory under separate contracts; they are outside these six exercises.

## Worked example: prove a small reservoir distribution exactly

A seeded histogram can look plausible by chance. Instead, this complete program enumerates every random choice path for a four-item stream and a two-slot reservoir.

```python
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
```

There are three equally likely choices at the third item and four at the fourth, giving twelve equally likely paths. Each of the six unordered pairs appears twice. This checks uniform subsets in the tiny fixture without a tolerance or a flaky statistical threshold.

Now change the replacement rule to always replace slot zero whenever a new item is admitted. Some pairs become impossible or overrepresented. The admission probability alone is insufficient: the replacement slot must also be selected correctly. The exhaustive example isolates that failure much more clearly than printing one sample.

## Reservoir inclusion reasoning and state ownership

Algorithm R fills the first k slots, then draws uniformly from `range(t)` for the t-th observed item. If the drawn index is below k, it replaces that reservoir slot. For \(t>k\), the new item's inclusion probability is \(k/t\). An old item already included with probability \(k/(t-1)\) survives with probability \(1-1/t\), giving

\[
\frac{k}{t-1}\left(1-\frac1t\right)=\frac{k}{t}.
\]

This proves equal inclusion probabilities by induction. Uniform subsets follow from the full Algorithm R argument and are independently exercised by the small exhaustive check. A particular seeded output is not itself that proof.

Pass an explicit `random.Random` instance. Its `getstate` and `setstate` methods support replay in a compatible runtime with the same call sequence. The function advances that instance when replacement draws are needed. It makes no cross-version bitwise promise. For k zero, it consumes the stream without draws; for a stream shorter than k, all values are returned in encounter order.

Reservoir values are retained by reference. Sampling a mutable dictionary does not deep-copy it, so later mutation of that dictionary can change the sampled object's contents. The algorithm promises a sample of positions, not an immutable data snapshot. Keep that ownership boundary visible when sampling evolving records.

## Exercises

### Six exercises

Implement these contracts in `python/professional/lessons/py_algo_07.py`. Use one-pass iterators in tests, distinguish exact integer or Fraction answers from approximate floating summaries, and record the generator state when demonstrating replay.

1. **Accumulate stable one-pass moments: `moments`.** Consume an iterable once and return (count, mean, M2), where M2 is the sum of squared deviations from the current mean. Use Welford updates with constant many numeric state fields and do not retain observations. Empty input returns (0, 0.0, 0.0). Accept finite Python int/float values excluding bool, convert to float, and reject invalid values or nonfinite/negative computed state with ValueError.

   **Expected:** [2, 4, 6] returns (3, 4.0, 8.0). A constant stream has M2 zero. Inputs around a large offset should be checked against an independent centered calculation, not raw sum-of-squares subtraction.

2. **Combine unequal chunks without averaging means blindly: `merge_moments`.** Accept two valid (count, mean, M2) tuples and return their merged summary without observations. Counts are nonnegative Python integers excluding bool; means and M2 must be finite, M2 nonnegative, empty states exactly (0, 0, 0), and singleton M2 zero. Empty state is an identity. Use the weighted mean and between-group correction; reject invalid or nonfinite results with ValueError.

   **Expected:** Merging moments([2]) with moments([4, 6]) matches moments([2, 4, 6]) within tolerance. Averaging chunk means without their counts would give 3.5 instead of 4.

3. **Distinguish undefined from zero variance: `sample_variance`.** Validate the moment-state contract used by merge_moments. Return M2/(count - 1) for count at least two, otherwise None. Preserve the tuple and do not reinterpret an empty or singleton sample as zero variance. Reject invalid states with ValueError. This is an arithmetic sample-variance calculation, not automatic evidence of an unbiased model estimate.

   **Expected:** The summary of [2, 4, 6] gives 4.0. Empty and singleton summaries give None; [7, 7] gives 0.0. A singleton state with positive M2 is invalid.

4. **Retain scored records with an explicit tie policy: `stable_top_k`.** Consume a one-pass iterable of (Python integer score, string payload) records, excluding bool scores, and retain at most k heap records. k must be a nonnegative Python integer excluding bool. Return up to k records ordered by descending score, with earlier input records first on equal scores. Preserve duplicates and payloads, never sort or retain the full input, and validate records even when k is zero. Invalid input raises ValueError.

   **Expected:** [(5, "first"), (7, "best"), (5, "second"), (5, "third")] with k=3 returns [(7, "best"), (5, "first"), (5, "second")]. Equal scores do not sort by payload.

5. **Maintain exact order statistics with two heaps: `prefix_medians`.** Return a lazy iterator yielding the exact Fraction median after each Python integer input, excluding bool. Use a negated lower min-heap as a max-heap and a normal upper min-heap, keeping lower equal in size to upper or larger by one. Preserve duplicates and use no floating conversion. Empty input yields nothing; invalid items raise ValueError when consumed. Retained heap entries grow with the prefix length.

   **Expected:** For [5, 1, 9, 3], yield fractions [5, 3, 5, 4]. For [2**100, 2**100 + 1], the second median is exactly Fraction(2**101 + 1, 2).

6. **Sample positions without knowing stream length: `reservoir_sample`.** Consume an arbitrary one-pass iterable with Algorithm R, retaining at most k objects and using the supplied exact random.Random instance. Require nonnegative Python integer k excluding bool; invalid k or generator raises ValueError before consumption. For the t-th item after filling k slots, draw uniformly from range(t) and replace that slot only when it is below k. Return reservoir slot order. k=0 consumes the stream without draws; streams shorter than k return all items in encounter order.

   **Expected:** For n >= k, return k sampled positions without replacement; repeated values may appear when positions differ. Saving and restoring rng.getstate() reproduces a run in the same runtime and call sequence. Input objects are retained by reference, not deep-copied.

## Common pitfalls

### Diagnosis, applications and retrieval

If merged variance is too small, check the between-group correction. If tied top-k records appear alphabetically, inspect the heap key. If exact medians differ for huge integers, remove float conversion. If memory grows unexpectedly, determine whether the implementation retained the input, every output, or the exact median heaps required by its contract.

These methods support telemetry summaries, ranking, incremental monitoring and bounded inspection samples. They answer different questions with different memory and accuracy costs. Explain which methods are mergeable, which retain all observed values, and why replayed reservoir output is not independent additional sampling evidence. Then choose one altered condition, such as unequal chunk sizes or duplicate scores, and defend its expected result without the reference implementation.

## Self-check

Without the solution, explain why two constant chunks with different means
can merge into a nonzero M2. State which count makes sample variance undefined
and how that differs from an observed zero. Trace an equal-score cutoff using
arrival positions, then explain which of the six operations retains every
observed value despite producing answers incrementally.

Reconstruct the twelve equally probable choice paths for the four-item,
two-slot reservoir fixture. Explain why repeating a saved generator state
replays one result rather than supplying independent evidence of uniformity.
Change one chunk size or one tie position and defend the resulting observation
before executing your implementation.

## Next step

Choose one small application and write its memory and exactness requirements
before choosing a summary: moment state, exact median heaps and a reservoir
solve different questions. Revisit [iterator and generator lifetime](py_lang_03.md)
after its listed prerequisites if source consumption or borrowed-object
ownership remains unclear. Keep the original bounded fixtures as regression
cases before adapting the algorithms to a larger offline input.

## Official API references

Use Python 3.12's [heapq documentation](https://docs.python.org/3.12/library/heapq.html), [Fraction API](https://docs.python.org/3.12/library/fractions.html), and [random state interface](https://docs.python.org/3.12/library/random.html#random.getstate) for the exact standard-library operations used here.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-algo-07: Streaming Summaries, Order Statistics, and Sampling.
Read python/professional/companion-guides/py_algo_07.md and python/professional/lessons/py_algo_07.py. Direct prerequisites: python-31, python-algo-02, python-algo-03. Keep explanations within that boundary and introduce new vocabulary at a beginner-friendly pace.
Focus on Welford moments, mergeable summary state, sample variance, stable bounded top-k, exact two-heap medians, reservoir inclusion probabilities. Explain one mechanism, ask me to predict a concrete result, let me attempt it, give one hint at a time, then review my output, invariant, memory or exception evidence. Ask me to retrieve the explanation in my own words. Do not read solutions/ until I ask or have made an honest attempt.
For retrieval, ask me to derive the count-weighted moment merge, distinguish undefined variance from zero, trace an arrival-stable top-k tie, and account for the two median heaps. Ask me to reconstruct the small reservoir choice distribution and explain why seeded replay alone is not a uniformity proof.
Use only the Docker classroom's prepared Python Core environment, standard-library code and tiny offline fixtures. Preserve my saved work. This lesson requires no live SQL, database writes, downloads or external services; do not execute live SQL as part of it.
Done when all six named contracts have inspected normal and boundary evidence and I can explain a counterexample to an incorrect algorithm and the actual retained-state cost.
```
