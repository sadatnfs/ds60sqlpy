# Grouped Transforms, Temporal Windows, and Session Boundaries

**Stable ID:** `python-pandas-03`

**Estimated time:** 150 minutes; split the reading and implementation across sessions when useful.

## Level and prerequisites

Intermediate. Direct catalog prerequisites: `python-pandas-02`. This lesson deepens the named mechanism after the introductory track; it does not require a cloud account or download data.

## Learning objectives

By the end, explain the mechanism in your own words, implement each bounded contract, and use a counterexample to distinguish a correct result from a plausible mistake. The six exercises progress from inspection to transformation, edge handling and transfer.

## How to run this lesson

Open the [learner script](../lessons/py_pandas_03.py) in the prepared repository environment. The browser reader is a preview; save an attempt in an ignored `.learning/` copy if you want it preserved separately. Run from the repository root. The provided worked examples execute immediately; task functions intentionally raise `NotImplementedError` until you implement them. A successful example is not evidence that the six tasks are finished.

Windows PowerShell:

```powershell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython python/professional/lessons/py_pandas_03.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_pandas_03.py
```

Dependencies: pandas and NumPy. All fixtures are tiny and local. The terminal prints the worked results and stops without editing your files. Keep [explanatory solutions](../solutions/py_pandas_03_solutions.md) and [runnable reference](../solutions/py_pandas_03_solution.py) closed until an attempt or an explicit worked comparison.

## Vocabulary and mental model

- **Aggregation:** Combining several rows into one row per group, changing the result grain.

- **Transform:** Computing group information while returning a value aligned to every original row.

- **Window:** A defined set of neighboring rows or times over which a calculation is performed; its boundaries are part of the metric.

- **Session:** A sequence of events grouped by an explicit inactivity-gap rule rather than an intrinsic property stored in every event.

groupby can either collapse rows or attach information to them. An aggregation such as sum creates one result per group. A transform such as transform('sum') repeats the group total beside every original row, allowing row-level ratios without a manual join. Confusing these shapes is a common source of accidental index alignment and duplicated metrics.

A temporal calculation requires an ordering contract. If two events share a timestamp, a row-based lag still needs a deterministic tie break, such as event_id. A time-based prior window may instead exclude every event at the current timestamp. Those are different questions. The exercise windows use [at-window, at), so the lower boundary is included and all events at the upper boundary are excluded.

Duplicate timestamps require care when using rolling operations. Aggregate contributions at each customer/time instant before applying a time-window sum when the metric is about elapsed time rather than arrival order. Then map the computed result back to every event at that instant. Otherwise two same-time events can receive different histories merely because one appears earlier in the stored rows.

Sessionization starts with a declared gap threshold. In this lesson a new session begins only when the elapsed gap is strictly greater than the threshold; exactly 30 minutes remains in the same session for a 30-minute rule. Sort within each customer, calculate differences, flag session starts and cumulatively count them within the customer. The first event always starts session one. Restore input order only after the sequence logic has been computed.

Missing measurements and unobserved groups need separate policies. A group with two rows and no known values is not the same as a group with no rows. count counts known measurements while size counts records. A sum with min_count=1 preserves an unknown total when no values are observed, instead of returning an apparently measured zero.

The lesson uses tiny frames with explicit event_id, customer_id, UTC timestamps and amounts. Reject missing identities or ambiguous timestamp types before calculation. Preserve one result per event unless the function explicitly promises one row per customer or declared category. Verification checks both numeric values and the row grain, because a correct-looking total on the wrong number of rows is not a correct result.

## Worked examples and syntax anatomy

### Example 1

```python
frame = pd.DataFrame({"customer_id": ["a", "a", "b"], "amount": [1.0, 3.0, 8.0]})
total = frame.groupby("customer_id", sort=False)["amount"].transform("sum")
share = frame.amount / total
assert share.tolist() == [0.25, 0.75, 1.0]
assert len(total) == len(frame)
print("Aligned group shares:", share.tolist())
```

transform returns three totals aligned with the three input rows, whereas ordinary sum returns only two customer totals. The arithmetic therefore retains event grain. The shares sum to one within each positive-total customer, giving a useful invariant beyond checking one displayed number.

### Example 2

```python
events = pd.DataFrame(
    {
        "customer_id": ["a", "a", "a"],
        "at": pd.to_datetime(["2026-01-01T10:00Z", "2026-01-01T10:30Z", "2026-01-01T11:01Z"]),
    }
)
gap = events.groupby("customer_id")["at"].diff()
start = gap.isna() | gap.gt(pd.Timedelta("30min"))
session = start.groupby(events.customer_id).cumsum()
assert session.tolist() == [1, 1, 2]
print("Session sequence:", session.tolist())
```

The exact 30-minute gap remains in session one, while 31 minutes starts session two. The first missing difference means no prior event and is explicitly marked as a start. This is different from treating a missing timestamp as a valid start, which the exercise validation rejects.

## Exercises

1. **Use transform without changing event grain.** For nonmissing customer_id and finite nonnegative amount, return each row amount divided by its customer total, preserving the original index. For an all-zero customer return missing shares rather than dividing zero by zero. Do not mutate frame.

**Expected:** Customers[a, a, b, b] with amounts[1,3,0,0] yield [.25,.75, NaN, NaN]. Duplicate incidental index labels are allowed; a negative amount raises ValueError.

2. **Lag within customer using a stable tie break.** Return event_id and previous_amount for each event, preserving input event order. Sort within customer by at then event_id, and use the previous row only within that customer. Require unique nonmissing event_id, known customer_id and nonmissing UTC timestamps.

**Expected:** For customer a events(id 2, time 10:00, amount 20),(id 1, time 10:00, amount 10),(id 3, time 11:00, amount 30), previous values in original order are 10, missing,20. Another customer starts with missing.

3. **Exclude every current-time event from a prior window.** Return event_id and prior_amount for each event over its customer interval[at-window, at). Require unique event IDs, known customers, finite amounts and UTC times; window must be positive. Equal-time events must receive identical prior sums. Empty prior windows have known sum zero.

**Expected:** Customer a amounts at 10:00=1,10:30=2,10:30=3,11:00=4 with a 30-minute window yield prior sums[0,1,1,5]. The lower boundary counts and the current timestamp never counts.

4. **Turn an inactivity rule into session identity.** Return event_id and a one-based session_id within each customer, preserving input order. Sort by at, event_id and start a new session only when elapsed gap is strictly greater than the positive threshold. Reuse identity/time validation from ordered_lag.

**Expected:** Times 10:00,10:30,11:01 with 30-minute threshold give sessions 1,1,2. Every other customer starts at 1; zero or negative threshold is rejected.

5. **Choose one final event deterministically.** Return one row per customer with customer_id, event_id, at, amount, choosing greatest at then greatest event_id. Sort final rows by customer_id. Validate event/time identity using ordered_lag and preserve the original input.

**Expected:** Two equal-time events for a with IDs 1 and 2 choose 2. Customer b keeps its own last event. Output contains each customer once and sorted customer IDs.

6. **Distinguish no rows from no known measurements.** Summarize declared unique categories in their declared order with category, row_count, known_count, total. Reject missing/undeclared category labels and nonnumeric or nonfinite known measurements. Include unobserved categories with row_count0, known_count0, total missing; an observed all-missing category also has missing total.

**Expected:** Rows a:1, a:NA, b:NA and declared [a, b, c] yield counts(2,1),(1,0),(0,0) and totals 1, missing, missing. Unknown category z is rejected.

## Common mistakes and diagnosis

If a group calculation changes row count, inspect whether agg was used where transform was intended. If a lag crosses customers, verify that shift occurs after grouping and after a deterministic sort. If tied timestamps receive different prior-time features, aggregate by instant before rolling. If session counts disagree only at the threshold, inspect > versus>=. If groupby.last appears to combine values from different events, choose an entire sorted row instead. If absent categories disappear, make observed explicit and retain both row counts and known-value counts.

## Self-check and retrieval

Without copying code, explain which input property each function assumes, which observable result proves the normal case, and which counterexample would expose an incorrect implementation. Trace one boundary input by hand before running it. Keep the input and expected output beside your saved result so a reviewer can reproduce the evidence.

## Next steps

Use these mechanisms in the next deepening lesson or return to the original prerequisite examples and explain precisely which new failure cases you can now diagnose. Review the [professional track](../README.md) for related modules.

## Primary sources and official APIs

- [pandas groupby transformations](https://pandas.pydata.org/docs/user_guide/groupby.html).

- [pandas time-window rolling](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rolling.html).

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-pandas-03: Grouped Transforms, Temporal Windows, and Session Boundaries.
Read python/professional/companion-guides/py_pandas_03.md and python/professional/lessons/py_pandas_03.py. Direct prerequisites: python-pandas-02.
Explain the vocabulary and mechanism at a beginner-friendly pace, then ask me to predict a concrete result before my attempt. Give one hint at a time, review my numerical or exception evidence, and ask retrieval questions in my own words. Do not read solutions/ until I request it or have made an honest attempt. Use only the prepared local Python environment and tiny offline inputs; preserve my saved work.
Done when all six contracts and their boundary cases have inspected evidence and I can explain why a tempting incorrect implementation fails.
```
