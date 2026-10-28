# MultiIndex and Lossless Reshaping Contracts

**Stable ID:** `python-pandas-05`. Allow about three hours for the explanations,
worked cases and independent implementations. The time is an estimate, not a
deadline.

## How to run this lesson

Run `./classroom` from the repository root and choose **Python** in the shared
`/classroom` directory. Open this lesson, read the Python capability notice,
and use the saved coding pad. Windows learners use the same commands in WSL 2.
Docker supplies pandas and Python; no host installation is needed. Paste the
complete learner script into the pad, save, and Run. Its two worked examples
print their expected observations. The six task functions deliberately remain
unimplemented and are not called by the opening demonstration.

The browser saves code, notes and results in its Docker learning volume. Each
Run starts a fresh process, so include the imports, fixture construction and
function calls needed for that run. Temporary in-process tables disappear when
it ends. Save the source that produces an observation, rather than relying on
objects from a previous Run. A successful demonstration does not establish that
the six tasks are complete. Open the separate explained and executable answers
only when you choose to compare your attempt.

An optional prepared contributor environment can run the same file with
`uv run --no-sync python python/professional/lessons/py_pandas_05.py`.
This route has its own checkout-local files and does not read the Docker
browser's named learning volume. See the [classroom guide](../../../docs/classroom-experience.md)
for navigation and persistence and [contributor setup](../../../CONTRIBUTING.md)
for that optional environment. Every fixture here is tiny, original and offline.

## Level and prerequisites

- **Level:** Advanced.
- **Direct prerequisite:** `python-pandas-01`, [companion guide](py_pandas_01.md).
- **Direct prerequisite:** `python-19`, [companion guide](../../ds-60day/companion-guides/day19_pandas_groupby_pivot.md).
- **Artifacts:** [learner](../lessons/py_pandas_05.py) · [explanations](../solutions/py_pandas_05_solutions.md) · [executable reference](../solutions/py_pandas_05_solution.py).

This is an advanced pandas practice lesson. Direct prerequisites are
`python-pandas-01` and `python-19`. You should already distinguish a table's row
identity from its current order, select columns, explain a missing value and
read a group operation. No database, cluster or external dataset is needed.
The examples target the classroom's prepared pandas 2.3 environment and use
`stack(future_stack=True)` explicitly.

## Learning objectives

Build a unique compound index, preserve its levels during selection, and explain
label alignment before calculating differences. Turn observed records into a
matrix while preserving the distinction between an unknown observation and an
unobserved coordinate. Restore exactly the original observed relation. Finally,
recognize export-name collisions and expose missing-side membership in a table
comparison. Verify identity, values, nullable dtype and order independently.

## Vocabulary and concepts

- **Compound key:** A tuple of fields that identifies an observation together.
  Neither site nor metric must be unique alone; `(site, metric)` must be unique
  under this lesson's one-measurement-per-coordinate contract. If the instrument
  can produce repeated readings, add a genuine reading identity or a time/version
  coordinate instead of silently averaging duplicates.

- **MultiIndex:** pandas' index representation for named coordinate levels. A
  Series remains one-dimensional, even when its labels contain two coordinates.
  The index associates each value with its site and metric; it is not a separate
  measurement matrix or a guarantee about how the physical data are partitioned.

- **Alignment:** Matching values by labels before arithmetic or combination.
  Matching two rows because they currently occupy position zero is a different
  operation. Removing labels with `to_numpy()` can be appropriate for a numerical
  algorithm, but then the caller owns the correspondence between positions.

- **Presence:** Whether a record exists at a coordinate. An existing measurement
  whose value is unknown differs from a coordinate with no record. `pd.NA` alone
  cannot represent both meanings without another field or a documented policy.

- **Reshape:** Moving coordinate levels between rows and columns. `unstack`
  turns a named row-index level into columns; `stack` performs the corresponding
  direction change. Neither command can recover information already discarded by
  aggregation, filtering or an ambiguous column-name encoding.

If sites form a set \(S\) and metrics form a set \(M\), the observed relation
\(\mathcal{R}\) may contain only some coordinates in \(S\times M\).
A rectangular display includes combinations outside \(\mathcal{R}\).
Keep an independent Boolean presence grid to distinguish those manufactured
display cells from actual observations whose measurements are unknown.

## Syntax anatomy

`set_index(["site", "metric"], verify_integrity=True)` moves the two key
columns into named index levels and refuses duplicate compound labels.
`sort_index()` establishes an explicit coordinate order for display and tests.
It does not create missing observations or resolve duplicate identities.

`xs(label, level="site", drop_level=False)` selects a cross-section while
retaining the selected level. Without `drop_level=False`, downstream code may
receive a one-level index when it expected the original two-level schema.
An absent site needs an explicit empty-result policy rather than an accidental
exception or a fabricated measurement.

`unstack("metric")` creates columns from observed metric labels. New rectangular
cells can be missing even when the original data had no unknown measurements.
In pandas 2.3, `stack(future_stack=True)` selects the newer stacking behavior;
do not also pass `dropna` or `sort`. Select observed coordinates with the
independent presence mask, then establish the desired final order yourself.

## Worked example / walkthrough

### Worked example 1: Reordered coordinates change positional subtraction

```python
import pandas as pd

keys = pd.MultiIndex.from_tuples(
    [("north", "flow"), ("south", "flow")], names=["site", "metric"]
)
left = pd.Series([10, 30], index=keys)
right = pd.Series([20, 5], index=keys[::-1])
by_label = left - right
by_position = left.to_numpy() - right.to_numpy()
assert by_label.tolist() == [5, 10]
assert by_position.tolist() == [-10, 25]
print("Label differences:", by_label.tolist())
print("Position differences:", by_position.tolist())
```

The north value ten is compared with north value five. South's thirty is
compared with south's twenty. The right-hand labels are reversed, so their
physical positions do not describe the same pairing. Both answers are valid
computations under different contracts; only the first answers this labelled
measurement question. A result with the right length and plausible magnitudes
does not prove the pairing was correct. Inspect at least one coordinate by hand.

### Worked example 2: Unknown values and absent coordinates look alike

```python
raw = pd.DataFrame(
    {"site": ["north", "north", "south"], "metric": ["flow", "temp", "flow"]}
)
raw["value"] = pd.array([0, pd.NA, 7], dtype="Float64")
observed = raw.set_index(["site", "metric"], verify_integrity=True)["value"]
wide = observed.unstack("metric")
presence = pd.Series(True, index=observed.index).unstack("metric", fill_value=False)
assert pd.isna(wide.loc["north", "temp"])
assert pd.isna(wide.loc["south", "temp"])
assert bool(presence.loc["north", "temp"])
assert not bool(presence.loc["south", "temp"])
print("Observed coordinates:", int(presence.to_numpy().sum()))
```

The display has four cells but only three observed coordinates. North's
temperature record exists and has an unknown value. South has no temperature
record. Dropping every missing value while stacking would erase the north
observation as well. Filling every missing cell with zero would invent a known
temperature for both sites. Preserve the pair of value and presence grids.

Now append another north/flow record. A pivot without an aggregation rule must
reject the duplicate coordinate. `pivot_table` can aggregate it, but choosing
an aggregation changes the question and can destroy the original observations.
Inspect the repeated keys and their provenance before deciding whether to add
another identity level, reject the feed, or deliberately summarize it.

## Exercises

1. **Establish unique compound identity.**

**Inputs:** A DataFrame with exactly site, metric, value columns. Keys are nonempty strings; value has nullable Float64 dtype, finite known measurements and optional pd.NA. Repeated compound keys are invalid.

**Expected:** Return a new Series named value, indexed by unique (site,metric) levels with those names, sorted by site then metric. Preserve every actual coordinate, zero and unknown value. Reject malformed keys, duplicate coordinates, wrong dtype or infinity with ValueError.

**Verify:** Compare the ordered tuple keys and nullable values with a manually constructed relation. Assert duplicate-key rejection and exact equality of a deep input copy afterward.

2. **Select without dropping a coordinate level.**

**Inputs:** A valid compound-key Float64 Series as above and one nonempty string site label. Input coordinate order may vary.

**Expected:** Return a new sorted Series for the chosen site while retaining both index levels and the value name/dtype. An absent site returns an empty Series with the same two-level schema.

**Verify:** Inspect both index names and all selected keys, including an observed unknown measurement. Assert an absent selection has zero rows and does not manufacture a zero value.

3. **Preserve observed membership when reshaping.**

**Inputs:** A valid unique compound-key Series whose actual records can include an unknown measurement. Only the observed labels define grid axes.

**Expected:** Return matching (value_grid,presence_grid) DataFrames with site rows and metric columns in sorted order. Values use Float64; presence uses bool. An observed unknown is missing/True; an unobserved combination is missing/False.

**Verify:** Assert the number of True cells equals the original record count. Check north/temp unknown/True and south/temp unknown/False separately, rather than comparing only numeric totals.

4. **Reconstruct actual records, including unknown values.**

**Inputs:** Matching value and presence grids with unique named site/metric axes, Float64 measurement columns and bool membership columns. A False membership cell cannot contain a known value.

**Expected:** Return exactly the observed relation as a sorted Float64 Series named value, retaining unknown observations. Reject mismatched axes, invalid labels/dtypes, infinite observations and known values at absent coordinates with ValueError.

**Verify:** Use assert_series_equal against the independent original relation, including names, dtype and unknown positions. Change an absent cell to eight and require rejection before any value can be silently discarded.

5. **Export coordinate labels without delimiter collisions.**

**Inputs:** A unique two-level MultiIndex of string coordinate pairs. Components may contain separators, quotes, empty strings or Unicode; complete index metadata is outside this encoding contract.

**Expected:** Return a pandas Index named encoded_coordinate containing compact JSON array encodings in the original pair order. Preserve both component strings exactly and reject malformed/duplicate coordinate indices with ValueError.

**Verify:** Decode every label with json.loads and compare the resulting tuple sequence with the original pairs. Assert (a__b,c) and (a,b__c) remain distinct and Unicode/quote characters survive.

6. **Compare by coordinate and expose side membership.**

**Inputs:** Two valid unique compound-key Float64 Series. Their order and key sets may differ and either side may contain unknown measurements.

**Expected:** Return the sorted outer key union with columns left_present,right_present,left_value,right_value,difference. Membership is bool; numerical columns retain nullable Float64. Difference is left minus right and remains unknown when a side/value is unavailable.

**Verify:** Compare each output row with a hand-built tuple-key dictionary. Shuffle both inputs and assert unchanged output, inspecting right-only east/flow separately from observed-unknown north/temp.


## Common pitfalls

If subtraction changes after sorting one input, inspect whether labels were
discarded before the operation. If a selected site's index loses its name or
number of levels, inspect `drop_level` and compare the complete index schema.
If a reshaped result has too few records, compare observed-key membership before
and after stacking, including records whose values are unknown. Do not only
compare sums: dropping an unknown observation can leave every numeric total
unchanged.

If an export has duplicate column names, inspect the original tuple labels.
Joining their parts with a separator is ambiguous when a part contains that
separator. For example, `(a__b, c)` and `(a, b__c)` both become `a__b__c` under
that encoding. JSON array encoding preserves the two strings, including Unicode
and quote characters; preserving complete pandas metadata is a separate task.

The functions here return new objects. Do not repair a caller's original index
or fill its missing values as a side effect. Keep a deep input copy during
testing and compare it after execution. Avoid relying on a warning disappearing
as proof of correctness: inspect the output relation and the stated contract.

## Self-check

Explain what one row means before and after each reshape. Identify which
coordinates are known, unknown and absent without running a sum. Reproduce the
two-column-name collision and explain which information the JSON encoding
preserves. Describe why a compound key needs both uniqueness and domain checks,
and why an equality of total measurements cannot establish equality of records.

## Next step

Continue to [timezone boundaries](py_pandas_06.md) after completing its timezone and data-cleaning prerequisites. Choose the sequence through the catalog rather than assuming that day labels are deadlines.

Use these checks when preparing a feature matrix or comparing model snapshots.
Carry a declared key set and a missingness policy into later joins and exports.
Continue to the timezone and typed-I/O lessons when their prerequisites are met.
The [pandas advanced indexing guide](https://pandas.pydata.org/pandas-docs/version/2.3/user_guide/advanced.html)
and [`stack` API](https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.DataFrame.stack.html)
document the selected APIs. The fixture policies, independent checks and
presence-preserving contract in this lesson are application choices.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-pandas-05: MultiIndex and Lossless Reshaping Contracts.
Read python/professional/companion-guides/py_pandas_05.md and python/professional/lessons/py_pandas_05.py. Direct prerequisites: python-pandas-01, python-19.
Explain coordinate identity and missingness, then ask me to predict one concrete result before my attempt. Give one hint at a time, review my tuple/value/exception evidence, and ask retrieval questions in my own words. Do not read solutions/ until I request a comparison or have made an honest attempt. Use only prepared local offline inputs and preserve my saved work.
Done when all six contracts and their boundary cases have inspected evidence, and I can explain how a positional comparison or a dropped unknown observation produces a plausible wrong answer.
```
