"""python-pandas-05: MultiIndex and Lossless Reshaping Contracts.

Run the two offline worked examples, then implement the six task contracts.
The classroom saves your submitted source and notes. Each Run is a new process.
Complete answers are in solutions/ and are not called by this learner artifact.
"""

from __future__ import annotations

import pandas as pd


# Exercise 1: Establish unique compound identity.
# Inputs: A DataFrame with exactly site, metric, value columns. Keys are nonempty strings; value has
# | nullable Float64 dtype, finite known measurements and optional pd.NA. Repeated compound keys are
# | invalid.
# Expected: Return a new Series named value, indexed by unique (site,metric) levels with those
# | names, sorted by site then metric. Preserve every actual coordinate, zero and unknown value.
# | Reject malformed keys, duplicate coordinates, wrong dtype or infinity with ValueError.
# Verify: Compare the ordered tuple keys and nullable values with a manually constructed relation.
# | Assert duplicate-key rejection and exact equality of a deep input copy afterward.
def keyed_measurements(frame: pd.DataFrame) -> pd.Series:
    """
    A DataFrame with exactly site, metric, value columns. Keys are nonempty strings; value has
    nullable Float64 dtype, finite known measurements and optional pd.NA. Repeated compound keys are
    invalid.

    Return a new Series named value, indexed by unique (site,metric) levels with those names, sorted
    by site then metric. Preserve every actual coordinate, zero and unknown value. Reject malformed
    keys, duplicate coordinates, wrong dtype or infinity with ValueError.
    """
    raise NotImplementedError("Implement keyed_measurements")


# Exercise 2: Select without dropping a coordinate level.
# Inputs: A valid compound-key Float64 Series as above and one nonempty string site label. Input
# | coordinate order may vary.
# Expected: Return a new sorted Series for the chosen site while retaining both index levels and the
# | value name/dtype. An absent site returns an empty Series with the same two-level schema.
# Verify: Inspect both index names and all selected keys, including an observed unknown measurement.
# | Assert an absent selection has zero rows and does not manufacture a zero value.
def select_site(values: pd.Series, site: str) -> pd.Series:
    """
    A valid compound-key Float64 Series as above and one nonempty string site label. Input
    coordinate order may vary.

    Return a new sorted Series for the chosen site while retaining both index levels and the value
    name/dtype. An absent site returns an empty Series with the same two-level schema.
    """
    raise NotImplementedError("Implement select_site")


# Exercise 3: Preserve observed membership when reshaping.
# Inputs: A valid unique compound-key Series whose actual records can include an unknown
# | measurement. Only the observed labels define grid axes.
# Expected: Return matching (value_grid,presence_grid) DataFrames with site rows and metric columns
# | in sorted order. Values use Float64; presence uses bool. An observed unknown is missing/True; an
# | unobserved combination is missing/False.
# Verify: Assert the number of True cells equals the original record count. Check north/temp
# | unknown/True and south/temp unknown/False separately, rather than comparing only numeric totals.
def observation_grid(values: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    A valid unique compound-key Series whose actual records can include an unknown measurement. Only
    the observed labels define grid axes.

    Return matching (value_grid,presence_grid) DataFrames with site rows and metric columns in
    sorted order. Values use Float64; presence uses bool. An observed unknown is missing/True; an
    unobserved combination is missing/False.
    """
    raise NotImplementedError("Implement observation_grid")


# Exercise 4: Reconstruct actual records, including unknown values.
# Inputs: Matching value and presence grids with unique named site/metric axes, Float64 measurement
# | columns and bool membership columns. A False membership cell cannot contain a known value.
# Expected: Return exactly the observed relation as a sorted Float64 Series named value, retaining
# | unknown observations. Reject mismatched axes, invalid labels/dtypes, infinite observations and
# | known values at absent coordinates with ValueError.
# Verify: Use assert_series_equal against the independent original relation, including names, dtype
# | and unknown positions. Change an absent cell to eight and require rejection before any value can
# | be silently discarded.
def restore_observations(grid: pd.DataFrame, present: pd.DataFrame) -> pd.Series:
    """
    Matching value and presence grids with unique named site/metric axes, Float64 measurement
    columns and bool membership columns. A False membership cell cannot contain a known value.

    Return exactly the observed relation as a sorted Float64 Series named value, retaining unknown
    observations. Reject mismatched axes, invalid labels/dtypes, infinite observations and known
    values at absent coordinates with ValueError.
    """
    raise NotImplementedError("Implement restore_observations")


# Exercise 5: Export coordinate labels without delimiter collisions.
# Inputs: A unique two-level MultiIndex of string coordinate pairs. Components may contain
# | separators, quotes, empty strings or Unicode; complete index metadata is outside this encoding
# | contract.
# Expected: Return a pandas Index named encoded_coordinate containing compact JSON array encodings
# | in the original pair order. Preserve both component strings exactly and reject
# | malformed/duplicate coordinate indices with ValueError.
# Verify: Decode every label with json.loads and compare the resulting tuple sequence with the
# | original pairs. Assert (a__b,c) and (a,b__c) remain distinct and Unicode/quote characters
# | survive.
def encode_column_labels(columns: pd.MultiIndex) -> pd.Index:
    """
    A unique two-level MultiIndex of string coordinate pairs. Components may contain separators,
    quotes, empty strings or Unicode; complete index metadata is outside this encoding contract.

    Return a pandas Index named encoded_coordinate containing compact JSON array encodings in the
    original pair order. Preserve both component strings exactly and reject malformed/duplicate
    coordinate indices with ValueError.
    """
    raise NotImplementedError("Implement encode_column_labels")


# Exercise 6: Compare by coordinate and expose side membership.
# Inputs: Two valid unique compound-key Float64 Series. Their order and key sets may differ and
# | either side may contain unknown measurements.
# Expected: Return the sorted outer key union with columns
# | left_present,right_present,left_value,right_value,difference. Membership is bool; numerical
# | columns retain nullable Float64. Difference is left minus right and remains unknown when a
# | side/value is unavailable.
# Verify: Compare each output row with a hand-built tuple-key dictionary. Shuffle both inputs and
# | assert unchanged output, inspecting right-only east/flow separately from observed-unknown
# | north/temp.
def aligned_difference(left: pd.Series, right: pd.Series) -> pd.DataFrame:
    """
    Two valid unique compound-key Float64 Series. Their order and key sets may differ and either
    side may contain unknown measurements.

    Return the sorted outer key union with columns
    left_present,right_present,left_value,right_value,difference. Membership is bool; numerical
    columns retain nullable Float64. Difference is left minus right and remains unknown when a
    side/value is unavailable.
    """
    raise NotImplementedError("Implement aligned_difference")


def worked_examples() -> None:
    keys = pd.MultiIndex.from_tuples(
        [("north", "flow"), ("south", "flow")], names=["site", "metric"]
    )
    left = pd.Series([10, 30], index=keys)
    right = pd.Series([20, 5], index=keys[::-1])
    assert (left - right).tolist() == [5, 10]
    assert (left.to_numpy() - right.to_numpy()).tolist() == [-10, 25]
    print("Label differences:", (left - right).tolist())
    print("Position differences:", (left.to_numpy() - right.to_numpy()).tolist())

    raw = pd.DataFrame({"site": ["north", "north", "south"], "metric": ["flow", "temp", "flow"]})
    raw["value"] = pd.array([0, pd.NA, 7], dtype="Float64")
    observed = raw.set_index(["site", "metric"], verify_integrity=True)["value"]
    wide = observed.unstack("metric")
    presence = pd.Series(True, index=observed.index).unstack("metric", fill_value=False)
    assert pd.isna(wide.loc["north", "temp"]) and pd.isna(wide.loc["south", "temp"])
    assert bool(presence.loc["north", "temp"]) and not bool(presence.loc["south", "temp"])
    print("Observed coordinates:", int(presence.to_numpy().sum()))


if __name__ == "__main__":
    worked_examples()
    print("Examples passed. Implement and verify the six separate task functions.")
