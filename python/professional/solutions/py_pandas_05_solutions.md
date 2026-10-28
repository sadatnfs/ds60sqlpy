# python-pandas-05: Explained MultiIndex and reshape solutions

The [complete executable reference](py_pandas_05_solution.py) implements all
six functions, checks concrete values and exercises negative boundaries. Run it
in the prepared classroom environment. The [learner guide](../companion-guides/py_pandas_05.md)
defines the observation contract and the different meanings of unknown and
absent cells. These explanations describe the decisions behind each answer;
passing the opening example is not a substitute for checking the six functions.

## Exercise 1: Establish compound observation identity

**Inputs:** A DataFrame with exactly site, metric, value columns. Keys are nonempty strings; value has nullable Float64 dtype, finite known measurements and optional pd.NA. Repeated compound keys are invalid.

**Expected:** Return a new Series named value, indexed by unique (site,metric) levels with those names, sorted by site then metric. Preserve every actual coordinate, zero and unknown value. Reject malformed keys, duplicate coordinates, wrong dtype or infinity with ValueError.

**Verify:** Compare the ordered tuple keys and nullable values with a manually constructed relation. Assert duplicate-key rejection and exact equality of a deep input copy afterward.

The reference first checks that the incoming table has exactly `site`, `metric`
and `value` columns in that order. It requires nullable `Float64` measurements
instead of trying to infer whether strings or arbitrary objects are numerical.
This is a deliberately narrow boundary for the exercise. A broader application
can have a separate parsing function, but parsing and identity checks should
not happen accidentally as a side effect of reshaping.

```python
result = frame.set_index(["site", "metric"], verify_integrity=True)["value"].copy()
```

`verify_integrity` refuses repeated coordinate pairs. A second identical row
is still a second observation under the input relation, so the implementation
does not silently deduplicate it. The validator also rejects missing/empty key
parts and infinite known measurements. Unknown `pd.NA` measurements remain
allowed. Sorting the resulting index makes the final presentation explicit;
it does not choose which duplicate should win.

The independent fixture starts in south/north/north order but ends at
`(north,flow)`, `(north,temp)`, `(south,flow)`. Zero is preserved as a known
flow, and north temperature remains unknown. The test compares the original
DataFrame with a deep copy, proving that the function did not mutate its caller.

## Exercise 2: Retain the schema during a cross-section

**Inputs:** A valid compound-key Float64 Series as above and one nonempty string site label. Input coordinate order may vary.

**Expected:** Return a new sorted Series for the chosen site while retaining both index levels and the value name/dtype. An absent site returns an empty Series with the same two-level schema.

**Verify:** Inspect both index names and all selected keys, including an observed unknown measurement. Assert an absent selection has zero rows and does not manufacture a zero value.

```python
selected = values.xs(site, level="site", drop_level=False).copy().sort_index()
```

A cross-section chooses one value of a named coordinate level. The selection
retains both level names, so another function expecting `(site,metric)` can
consume it. The explicit `drop_level=False` is part of the output schema, not
a cosmetic choice. Looking up north must retain its two observed measurements,
including the unknown temperature, without inventing a south temperature.

An absent site returns a zero-length copy with the original two-level schema.
This policy is chosen in the contract. Returning a fabricated zero reading would
mean something different; letting an unhandled key error decide the policy
would make absence difficult to distinguish from a malformed call. The output
is sorted even if the supplied valid Series was not sorted originally.

## Exercise 3: Preserve presence separately from value

**Inputs:** A valid unique compound-key Series whose actual records can include an unknown measurement. Only the observed labels define grid axes.

**Expected:** Return matching (value_grid,presence_grid) DataFrames with site rows and metric columns in sorted order. Values use Float64; presence uses bool. An observed unknown is missing/True; an unobserved combination is missing/False.

**Verify:** Assert the number of True cells equals the original record count. Check north/temp unknown/True and south/temp unknown/False separately, rather than comparing only numeric totals.

```python
grid = ordered.unstack("metric")
present = pd.Series(True, index=ordered.index, dtype=bool).unstack(
    "metric", fill_value=False
)
```

The reference begins with a validated unique coordinate relation. Unstacking
measurement values makes a rectangle; unstacking a True value for every actual
coordinate records which cells came from observations. Only manufactured cells
receive False. Both grids have matching named axes, and measurement columns
retain nullable `Float64` dtype.

For north temperature, value is missing and presence is True. For south
temperature, value is missing and presence is False. The number of True cells
is therefore three, matching the original three records, while the matrix has
four cells. Counting only nonmissing measurements would report two and erase
the unknown observation. Filling the value grid with zeros would invent data.

## Exercise 4: Restore the observed relation without dropping unknowns

**Inputs:** Matching value and presence grids with unique named site/metric axes, Float64 measurement columns and bool membership columns. A False membership cell cannot contain a known value.

**Expected:** Return exactly the observed relation as a sorted Float64 Series named value, retaining unknown observations. Reject mismatched axes, invalid labels/dtypes, infinite observations and known values at absent coordinates with ValueError.

**Verify:** Use assert_series_equal against the independent original relation, including names, dtype and unknown positions. Change an absent cell to eight and require rejection before any value can be silently discarded.

```python
stacked = grid.stack(future_stack=True)
observed = present.stack(future_stack=True)
result = stacked.loc[observed].astype("Float64").rename("value").sort_index()
```

The two stacked objects share coordinate labels. The Boolean presence Series
selects actual observations, while the stacked values keep unknown measurements.
The result is named `value` and sorted by both levels, matching the original
canonical relation. `dropna()` would select known measurements instead, which
is the wrong membership rule. Under this selected pandas stack implementation,
do not additionally pass `dropna` or `sort` parameters.

Validation occurs before selection. Axes must match exactly, be uniquely named,
and have valid string labels. Presence must contain ordinary Boolean columns,
with no unknown membership values. Value columns must use the declared nullable
numeric dtype. An absent coordinate containing a known value is contradictory;
the reference rejects it instead of silently throwing the value away. The final
Series validator also rejects infinite observed measurements. Compare complete
Series identity, dtype, name, unknown positions and values in the roundtrip.

## Exercise 5: Encode column coordinates without collisions

**Inputs:** A unique two-level MultiIndex of string coordinate pairs. Components may contain separators, quotes, empty strings or Unicode; complete index metadata is outside this encoding contract.

**Expected:** Return a pandas Index named encoded_coordinate containing compact JSON array encodings in the original pair order. Preserve both component strings exactly and reject malformed/duplicate coordinate indices with ValueError.

**Verify:** Decode every label with json.loads and compare the resulting tuple sequence with the original pairs. Assert (a__b,c) and (a,b__c) remain distinct and Unicode/quote characters survive.

```python
label = json.dumps(list(key), ensure_ascii=False, separators=(",", ":"))
```

The input is a unique two-level column index whose coordinate parts are strings.
JSON array encoding preserves component boundaries and escapes quote characters
without depending on a separator absent from every possible input. The pairs
`(a__b,c)` and `(a,b__c)` therefore yield different labels. A Unicode component
also survives decoding unchanged.

The inverse check uses the independent JSON parser and compares the decoded
tuples with the original tuple sequence. Uniqueness alone would not prove the
values were preserved: replacing every pair with a new numeric label would
also be unique. The contract deliberately covers coordinate pairs, not every
MultiIndex property. Store names, category domains and unused levels separately
if an export requires those properties to survive too. Keep the multi-level
representation whenever the consumer supports it and a flat encoding is unnecessary.

## Exercise 6: Align comparisons and expose missing sides

**Inputs:** Two valid unique compound-key Float64 Series. Their order and key sets may differ and either side may contain unknown measurements.

**Expected:** Return the sorted outer key union with columns left_present,right_present,left_value,right_value,difference. Membership is bool; numerical columns retain nullable Float64. Difference is left minus right and remains unknown when a side/value is unavailable.

**Verify:** Compare each output row with a hand-built tuple-key dictionary. Shuffle both inputs and assert unchanged output, inspecting right-only east/flow separately from observed-unknown north/temp.

```python
keys = left.index.union(right.index, sort=True)
a = left.reindex(keys)
b = right.reindex(keys)
difference = a - b
```

The union defines one output coordinate per key present on either side. Each
input is reindexed to those coordinates before subtraction. Membership flags
come from each original index, independently of whether its measurement is known.
The final frame exposes `left_present`, `right_present`, `left_value`,
`right_value` and `difference`, with the two-level compound index retained.

In the reference fixture, east/flow appears only on the right, so its difference
is unknown and left presence is False. North/temp exists only on the left but
has an unknown measurement; left presence is True even though the displayed
value is missing. The shared north/flow difference is minus two, while shared
south/flow is minus six. Compare these values with a hand-built dictionary keyed
by tuples, then shuffle both input orders and require the same sorted output.
Filling missing sides with zero would answer a different comparison and conceal
the distinction between absence, zero and an existing unknown measurement.

All six implementations operate on copies or newly created objects. Keep
counterexamples small enough to inspect every coordinate; a large aggregate
agreement can conceal both an identity error and an erased unknown record.
