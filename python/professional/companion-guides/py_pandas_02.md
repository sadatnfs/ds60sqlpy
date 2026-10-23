# Join Contracts and Point-in-Time Feature Lookup

**Stable ID:** `python-pandas-02`

**Estimated time:** 150 minutes; split the reading and implementation across sessions when useful.

## Level and prerequisites

Intermediate. Direct catalog prerequisites: `python-pandas-01`, `python-21`. This lesson deepens the named mechanism after the introductory track; it does not require a cloud account or download data.

## Learning objectives

By the end, explain the mechanism in your own words, implement each bounded contract, and use a counterexample to distinguish a correct result from a plausible mistake. The six exercises progress from inspection to transformation, edge handling and transfer.

## How to run this lesson

**Primary browser route:** run `./classroom` from the repository root and
choose **Python** on `/classroom`. Open this lesson in the shared workspace,
read its capability notice, and use its supported coding or reading workflow.
The [classroom guide](../../../docs/classroom-experience.md) explains saved work, runtimes and switching subjects.

**Optional native notebook/editor route:** the instructions below describe
separately prepared host tools. They are useful alternatives, not prerequisites
for opening this lesson in the Docker classroom.

Open the [learner script](../lessons/py_pandas_02.py) in the prepared repository environment. The browser reader is a preview; save an attempt in an ignored `.learning/` copy if you want it preserved separately. Run from the repository root. The provided worked examples execute immediately; task functions intentionally raise `NotImplementedError` until you implement them. A successful example is not evidence that the six tasks are finished.

Windows PowerShell:

```powershell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython python/professional/lessons/py_pandas_02.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_pandas_02.py
```

Dependencies: pandas and NumPy. All fixtures are tiny and local. The terminal prints the worked results and stops without editing your files. Keep [explanatory solutions](../solutions/py_pandas_02_solutions.md) and [runnable reference](../solutions/py_pandas_02_solution.py) closed until an attempt or an explicit worked comparison.

## Vocabulary and mental model

- **Cardinality contract:** The allowed number of matches for each key, such as many event rows matching one dimension row.

- **As-of join:** A temporal lookup choosing the closest permitted timestamp, often the latest record available no later than a decision.

- **Availability time:** The moment information could actually be used, which may be later than the event it describes.

- **Half-open validity:** An interval including its start and excluding its end, so adjacent versions cannot both own the boundary instant.

A join is both a relationship and a claim about row count. Enriching events with one customer attribute should preserve one output row per event. If the dimension has two rows for one customer, a merge can multiply events and measures. validate='many_to_one' checks that relationship, while an indicator records unmatched keys. Neither feature decides whether unmatched rows should be dropped, filled or investigated; that policy belongs to the analysis contract.

Null keys deserve attention because pandas merge behavior can match null keys to other null keys, unlike ordinary SQL equality. A missing customer identifier is not proof that two records refer to the same unknown customer. This lesson forbids null dimension identities and reports missing event keys separately from known-but-unmatched identifiers.

Temporal features add another relationship: which version was available when the decision occurred? A record can describe an event at 09:00 but arrive at 11:00. A10:00 prediction cannot use it merely because its event time is earlier. Store and join on availability time for prediction correctness, retaining event time separately when it answers another question.

merge_asof requires ordered time keys and provides direction and tolerance controls. A backward lookup chooses the latest available record no later than the request. A tolerance prevents arbitrarily stale values from being treated as current. Restore the original request order after sorting, and keep a durable request identifier so results cannot be mistaken for row-position matches.

Validity intervals model a different situation: a version is active over [start, end). A point at end belongs to the next version, if one exists. Overlapping intervals create ambiguous versions and must be rejected or explicitly resolved before lookup. A gap represents absent coverage and should remain visible rather than borrowing a nearby value without authorization.

All timestamps in these fixtures are already timezone-aware UTC. The functions reject naive or missing timestamps instead of silently assigning a zone. This strict teaching boundary keeps identity, ordering, staleness and interval ownership observable. Production multi-entity histories also require grouping by entity and the same checks within each group.

## Worked examples and syntax anatomy

### Example 1

```python
events = pd.DataFrame({"event_id": [1, 2, 3], "customer_id": ["a", "b", "c"]})
dimension = pd.DataFrame({"customer_id": ["a", "b"], "segment": ["small", "large"]})
joined = events.merge(
    dimension, on="customer_id", how="left", validate="many_to_one", indicator=True
)
assert len(joined) == 3 and joined.loc[joined.event_id == 3, "_merge"].iloc[0] == "left_only"
print("Join coverage:", joined[["event_id", "_merge"]].astype(str).values.tolist())
```

The left join retains every event. Cardinality validation protects against multiplying rows, while the indicator distinguishes a missing dimension match from a successfully attached segment. An inner join would quietly remove customer c and change the population.

### Example 2

```python
requests = pd.DataFrame(
    {"request_id": [1, 2], "at": pd.to_datetime(["2026-01-01T10:30Z", "2026-01-01T12:00Z"])}
)
history = pd.DataFrame(
    {
        "available_at": pd.to_datetime(["2026-01-01T10:00Z", "2026-01-01T11:00Z"]),
        "value": [10.0, 20.0],
    }
)
joined = pd.merge_asof(
    requests,
    history,
    left_on="at",
    right_on="available_at",
    direction="backward",
    tolerance=pd.Timedelta("45min"),
)
assert joined.loc[0, "value"] == 10 and pd.isna(joined.loc[1, "value"])
print("Bounded availability lookup:", joined["value"].tolist())
```

The second request is one hour after the last available value, exceeding the 45-minute freshness policy. Returning missing is the correct result, not an execution failure. A forward direction would introduce future information and a missing tolerance would silently change the policy.

## Exercises

1. **Require one real identity per dimension row.** Validate that key exists, contains no missing values and is unique. Raise ValueError for a missing column, null key or repeated key. An empty frame with the key column is a valid empty dimension.

**Expected:** Keys[a, b] pass; [a, a], [a, None] and a frame without key fail. An empty customer_id column passes.

2. **Preserve event grain during enrichment.** Require unique nonmissing event_id and a valid customer_id dimension. Left-join dimension segment onto event_id, customer_id, amount events with many-to-one validation and a match indicator. Preserve input event order and do not mutate either frame.

**Expected:** Events for customers a, c, b keep all three event_id values in input order; c has missing segment and left_only status. Duplicate dimension a raises ValueError.

3. **Separate absent identifiers from unknown identifiers.** Return one diagnostic row per unmatched event with columns event_id and reason, sorted by event_id. Label null customer identifiers missing_key and nonnull identifiers absent from the dimension unknown_key. Validate event and dimension identities first.

**Expected:** Events 1:a,2:None,3:z with dimension[a] yield (2, missing_key),(3, unknown_key). A fully matched event yields an empty frame with both output columns.

4. **Look backward within a freshness limit.** For a single history, attach the latest available_at, value no later than each request at time, within a nonnegative tolerance. Require unique request_id and unique history available_at, with nonmissing timezone-aware UTC time columns. Return original request order and preserve unmatched values as missing.

**Expected:** Requests at 10:30 and 15:00 with history at 10:00, value 10 and 12:00, value 20, tolerance 2 hours, yield 10 and missing. Unsorted requests are restored to their original order; naive times fail.

5. **Reject overlapping validity versions.** Validate a single version history with unique version_id and finite UTC start, end times satisfying start<end. Return it sorted by start. Reject any overlap, while permitting adjacent intervals where one end equals the next start.

**Expected:** Versions[10:00,11:00) and [11:00,12:00) pass; changing the second start to 10:59 raises ValueError. A zero-width interval also fails.

6. **Assign an instant to at most one version.** Use validated single-history half-open intervals to attach version_id, value to uniquely identified events at UTC instants. Return event_id, version_id, value in input event order. Preserve uncovered events with missing version/value and reject ambiguous histories.

**Expected:** Events at 10:00,11:00,12:00 against adjacent hourly versions 1,2 yield version 1, version 2, missing. The exact final end is excluded; gaps are not filled by nearest lookup.

## Common mistakes and diagnosis

If output rows multiply, inspect dimension uniqueness and merge validation before applying drop_duplicates. If unknown keys vanish, compare left versus inner join behavior and examine the indicator. If an as-of join complains that keys are unsorted, sort the time column while retaining an explicit source position; do not assume the DataFrame index records request order. If future information appears, inspect availability timestamps and direction. If adjacent versions both match a boundary, replace inclusive end logic with a half-open contract and validate overlaps before lookup.

## Self-check and retrieval

Without copying code, explain which input property each function assumes, which observable result proves the normal case, and which counterexample would expose an incorrect implementation. Trace one boundary input by hand before running it. Keep the input and expected output beside your saved result so a reviewer can reproduce the evidence.

## Next steps

Use these mechanisms in the next deepening lesson or return to the original prerequisite examples and explain precisely which new failure cases you can now diagnose. Review the [professional track](../README.md) for related modules.

## Primary sources and official APIs

- [pandas merge API](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html).

- [pandas merge_asof API](https://pandas.pydata.org/docs/reference/api/pandas.merge_asof.html).

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-pandas-02: Join Contracts and Point-in-Time Feature Lookup.
Read python/professional/companion-guides/py_pandas_02.md and python/professional/lessons/py_pandas_02.py. Direct prerequisites: python-pandas-01, python-21.
Explain the vocabulary and mechanism at a beginner-friendly pace, then ask me to predict a concrete result before my attempt. Give one hint at a time, review my numerical or exception evidence, and ask retrieval questions in my own words. Do not read solutions/ until I request it or have made an honest attempt. Use only the prepared local Python environment and tiny offline inputs; preserve my saved work.
Done when all six contracts and their boundary cases have inspected evidence and I can explain why a tempting incorrect implementation fails.
```
