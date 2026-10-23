# Chunked Data, Global Reductions, and Cross-Batch State

**Stable ID:** `python-pandas-04`

**Estimated time:** 150 minutes; split the reading and implementation across sessions when useful.

## Level and prerequisites

Intermediate. Direct catalog prerequisites: `python-pandas-03`, `python-23`. This lesson deepens the named mechanism after the introductory track; it does not require a cloud account or download data.

## Learning objectives

By the end, explain the mechanism in your own words, implement each bounded contract, and use a counterexample to distinguish a correct result from a plausible mistake. The six exercises progress from inspection to transformation, edge handling and transfer.

## How to run this lesson

Open the [learner script](../lessons/py_pandas_04.py) in the prepared repository environment. The browser reader is a preview; save an attempt in an ignored `.learning/` copy if you want it preserved separately. Run from the repository root. The provided worked examples execute immediately; task functions intentionally raise `NotImplementedError` until you implement them. A successful example is not evidence that the six tasks are finished.

Windows PowerShell:

```powershell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython python/professional/lessons/py_pandas_04.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_pandas_04.py
```

Dependencies: pandas and NumPy. All fixtures are tiny and local. The terminal prints the worked results and stops without editing your files. Keep [explanatory solutions](../solutions/py_pandas_04_solutions.md) and [runnable reference](../solutions/py_pandas_04_solution.py) closed until an attempt or an explicit worked comparison.

## Vocabulary and mental model

- **Chunk:** A bounded batch of rows read or processed at one time; it is an implementation boundary rather than a statistical group.

- **Reduction state:** The information retained from a batch that can be combined with other batches to compute a global result.

- **Sufficient aggregation state:** A state such as sum and count that retains what a specified aggregate needs, without claiming statistical sufficiency for every model.

- **Carry state:** Information preserved across chunk boundaries, such as the previous window values or identities already observed.

Reading in chunks reduces peak input memory only if the computation avoids collecting every chunk again. A result may still require state proportional to the number of groups, distinct identities or output rows. State the memory behavior honestly: bounded batch size does not automatically make the whole algorithm constant-memory.

A global mean requires the sum and count of known observations. Averaging chunk means gives equal weight to chunks, which is wrong when they have different lengths or different missing counts. For chunks[1,3] and [100], the chunk means are 2 and 100, whose average is 51. The correct global mean is 104/3. Chunk boundaries must not change the result.

Missing values affect the denominator. A chunk with three rows but one known amount contributes one to a known-value mean count, while its record count is three. Preserve both counts when reporting data quality. For integer-cent totals, use Python integer accumulation and explicitly enforce the output representation's range instead of permitting silent fixed-width overflow.

Deduplication is a global operation when an event can appear in different chunks. A set or dictionary of observed identities grows with the number of unique events. That may be acceptable for a small pipeline, but it is not bounded by chunk size. A repeated identical event can be ignored under a declared policy; a repeated ID with conflicting content should stop the calculation rather than choose whichever arrived first silently.

Temporal windows also cross boundaries. Resetting a rolling mean for each chunk discards the previous batch's last values and changes the feature at every read boundary. A deque of the last window-size observations preserves the necessary history. In production, separate deques may be needed for each entity and time-based eviction needs actual timestamps, not only row counts.

Typed CSV chunks provide a concrete input boundary. Parse IDs and integer amounts with nullable integer dtypes and customer labels as strings. Validate exact columns, key presence and parse failures per chunk. The examples use in-memory text, so no file or network download is needed. The same reduction principles apply to a prepared local file reader, provided its schema and error policy are preserved.

## Worked examples and syntax anatomy

### Example 1

```python
chunks = [pd.Series([1.0, 3.0]), pd.Series([100.0])]
means = [chunk.mean() for chunk in chunks]
correct = sum(chunk.sum() for chunk in chunks) / sum(chunk.count() for chunk in chunks)
assert np.mean(means) == 51 and np.isclose(correct, 104 / 3)
print("Wrong mean of means:", np.mean(means), "global mean:", correct)
```

The second chunk contains only one observation, so giving it the same influence as the two-row chunk changes the population weighting. Sum/count states retain enough information for the global mean regardless of how the input is partitioned.

### Example 2

```python
text = "event_id,customer_id,amount_cents\n1,a,10\n2,b,\n3,a,20\n"
chunks = list(
    pd.read_csv(
        StringIO(text),
        chunksize=2,
        dtype={"event_id": "Int64", "customer_id": "string", "amount_cents": "Int64"},
    )
)
assert [len(chunk) for chunk in chunks] == [2, 1]
assert chunks[0].amount_cents.isna().sum() == 1
print("Typed chunk lengths:", [len(chunk) for chunk in chunks])
```

The empty amount is preserved as a missing nullable integer rather than coerced to zero. The final chunk is shorter, which is normal and is exactly why averaging per-chunk means is unsafe. Materializing chunks here is only for inspecting the tiny demonstration, not a scalable reading pattern.

## Exercises

1. **Retain the correct mean denominator.** For a numeric Series containing finite values or missing entries, return accurate known-value sum and known-value count. Reject nonnumeric dtype or infinity with ValueError. An empty or all-missing numeric Series returns (0.0,0).

**Expected:** [1, NA,3] returns (4.0,2), not count 3. Empty Float64 and [NA] Float64 return (0.0,0); infinity fails.

2. **Combine uneven chunks correctly.** Combine sum/count states into one mean, returning None if total count is zero. Require finite sums and nonnegative integer counts; a zero-count state must have zero sum. Reject invalid states with ValueError.

**Expected:** States(4,2),(100,1) yield 104/3. Adding(0,0) has no effect. Empty states return None; (5,0), negative count or Boolean count is rejected.

3. **Reduce typed amounts across batches.** Consume an iterable of chunks with nonmissing string customer_id and nullable/integer amount_cents. Reject missing or nonstring customers, noninteger amount dtype or totals outside signed int64 range. Return customer_id, row_count, known_count, total_cents sorted by customer, preserving missing totals when a customer has no known amounts.

**Expected:** Across chunks a:10, b:NA then a:20, b:NA, return a counts 2,2, total 30 and b counts 2,0, totalNA. Input chunk boundaries do not change the result.

4. **Detect conflicts across chunk boundaries.** Consume chunks with nonmissing integer event_id and amount_cents that is integer or missing. Keep the first occurrence of identical event records in encounter order. Reject any repeated ID with a different amount, including missing versus zero, with ValueError.

**Expected:** Chunks[(1,10),(2, NA)] then[(1,10),(3,20)] return IDs 1,2,3. Repeating ID 2 with amount 0 raises ValueError; missing is not normalized to zero.

5. **Carry rolling history across batches.** Yield full-window row-count rolling means across an iterable of finite numeric one-dimensional chunks. Require a positive non-Boolean integer window. Do not reset history at a chunk boundary, and yield nothing before a full window exists.

**Expected:** Chunks[1,2] then[3,4] with window 3 yield [2,3], the same as one chunk[1,2,3,4]. Empty input yields no values; window 0 and NaN input fail on iteration.

6. **Make parsing a typed batch boundary.** Yield chunks from in-memory CSV text with exactly event_id, customer_id, amount_cents columns in that order. Parse IDs/amounts as Int64 and customers as string. Require positive integer chunksize, nonmissing IDs/customers and valid numeric text. Preserve missing amounts.

**Expected:** Three CSV rows with chunksize 2 yield lengths 2,1 and nullable Int64 amounts. An empty amount stays missing; amount bad or missing event_id raises ValueError during iteration.

## Common mistakes and diagnosis

If changing chunksize changes a mean, inspect whether chunk means were averaged instead of sum/count states. If duplicates survive only across batches, move identity state outside the per-chunk loop. If rolling results restart at every boundary, preserve the final window context. If memory still grows, count distinct groups, identity keys and collected output rows; bounded input batches do not bound those structures. If a later CSV chunk fails parsing, do not label previously emitted partial aggregates complete. Stage or checkpoint results with an explicit completion boundary in a real pipeline.

## Self-check and retrieval

Without copying code, explain which input property each function assumes, which observable result proves the normal case, and which counterexample would expose an incorrect implementation. Trace one boundary input by hand before running it. Keep the input and expected output beside your saved result so a reviewer can reproduce the evidence.

## Next steps

Use these mechanisms in the next deepening lesson or return to the original prerequisite examples and explain precisely which new failure cases you can now diagnose. Review the [professional track](../README.md) for related modules.

## Primary sources and official APIs

- [pandas chunked CSV reading](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html).

- [Python deque](https://docs.python.org/3/library/collections.html#collections.deque).

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-pandas-04: Chunked Data, Global Reductions, and Cross-Batch State.
Read python/professional/companion-guides/py_pandas_04.md and python/professional/lessons/py_pandas_04.py. Direct prerequisites: python-pandas-03, python-23.
Explain the vocabulary and mechanism at a beginner-friendly pace, then ask me to predict a concrete result before my attempt. Give one hint at a time, review my numerical or exception evidence, and ask retrieval questions in my own words. Do not read solutions/ until I request it or have made an honest attempt. Use only the prepared local Python environment and tiny offline inputs; preserve my saved work.
Done when all six contracts and their boundary cases have inspected evidence and I can explain why a tempting incorrect implementation fails.
```
