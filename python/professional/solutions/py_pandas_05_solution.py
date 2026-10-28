"""python-pandas-05: complete MultiIndex and reshape references.

These small trusted fixtures teach explicit identity and missingness policies.
Run the learner examples before comparing the six implementations.
"""

from __future__ import annotations

import json
import math

import pandas as pd  # type: ignore[import-untyped]


def _checked_series(values: pd.Series) -> None:
    if (
        not isinstance(values, pd.Series)
        or not isinstance(values.index, pd.MultiIndex)
        or values.index.nlevels != 2
        or list(values.index.names) != ["site", "metric"]
        or not values.index.is_unique
        or str(values.dtype) != "Float64"
        or any(not isinstance(part, str) or not part for key in values.index for part in key)
        or not values.dropna().map(math.isfinite).all()
    ):
        raise ValueError("Expected unique (site, metric) keys and finite-or-missing Float64 values")


# Exercise 1: Establish unique compound identity.
def keyed_measurements(frame: pd.DataFrame) -> pd.Series:
    """Return a sorted, named compound-key Series without aggregating observations."""
    if (
        not isinstance(frame, pd.DataFrame)
        or list(frame.columns) != ["site", "metric", "value"]
        or str(frame["value"].dtype) != "Float64"
    ):
        raise ValueError("Expected site, metric, value columns with nullable Float64 value")
    result = frame.set_index(["site", "metric"], verify_integrity=True)["value"].copy()
    _checked_series(result)
    return result.sort_index()


# Exercise 2: Select without dropping a coordinate level.
def select_site(values: pd.Series, site: str) -> pd.Series:
    """Select a site while retaining both named index levels, including empty results."""
    _checked_series(values)
    if not isinstance(site, str) or not site:
        raise ValueError("Expected a nonempty site label")
    if site not in values.index.get_level_values("site"):
        return values.iloc[:0].copy()
    return values.xs(site, level="site", drop_level=False).copy().sort_index()


# Exercise 3: Preserve observed membership when reshaping.
def observation_grid(values: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Preserve an independent presence grid so an unknown observation is not lost."""
    _checked_series(values)
    ordered = values.sort_index()
    grid = ordered.unstack("metric")
    present = pd.Series(True, index=ordered.index, dtype=bool).unstack("metric", fill_value=False)
    return grid.copy(), present.copy()


# Exercise 4: Reconstruct actual records, including unknown values.
def restore_observations(grid: pd.DataFrame, present: pd.DataFrame) -> pd.Series:
    """Restore observed coordinates, retaining actual unknown values under future_stack."""
    if (
        not isinstance(grid, pd.DataFrame)
        or not isinstance(present, pd.DataFrame)
        or not grid.index.equals(present.index)
        or not grid.columns.equals(present.columns)
        or not grid.index.is_unique
        or not grid.columns.is_unique
        or grid.index.name != "site"
        or grid.columns.name != "metric"
        or any(not isinstance(label, str) or not label for label in grid.index)
        or any(not isinstance(label, str) or not label for label in grid.columns)
        or any(str(dtype) != "bool" for dtype in present.dtypes)
        or any(str(dtype) != "Float64" for dtype in grid.dtypes)
    ):
        raise ValueError("Expected matching unique site/metric axes and Boolean presence")
    if grid.where(~present).notna().any().any():
        raise ValueError("An absent coordinate cannot contain a measured value")
    # future_stack retains unknown values. The independent mask selects actual
    # observations; dropping all NA values would also delete observed unknowns.
    stacked = grid.stack(future_stack=True)
    observed = present.stack(future_stack=True)
    result = stacked.loc[observed].astype("Float64").rename("value").sort_index()
    _checked_series(result)
    return result


# Exercise 5: Export coordinate labels without delimiter collisions.
def encode_column_labels(columns: pd.MultiIndex) -> pd.Index:
    """Encode unique two-string coordinates without delimiter collisions.

    The JSON arrays preserve each pair, not arbitrary MultiIndex metadata such
    as names or unused levels. Keep that metadata separately if it is required.
    """
    if (
        not isinstance(columns, pd.MultiIndex)
        or columns.nlevels != 2
        or not columns.is_unique
        or any(not isinstance(part, str) for key in columns for part in key)
    ):
        raise ValueError("Expected unique two-string column coordinates")
    return pd.Index(
        [json.dumps(list(key), ensure_ascii=False, separators=(",", ":")) for key in columns],
        name="encoded_coordinate",
    )


# Exercise 6: Compare by coordinate and expose side membership.
def aligned_difference(left: pd.Series, right: pd.Series) -> pd.DataFrame:
    """Compare by labels while exposing side presence independently of known values."""
    _checked_series(left)
    _checked_series(right)
    keys = left.index.union(right.index, sort=True)
    a = left.reindex(keys)
    b = right.reindex(keys)
    return pd.DataFrame(
        {
            "left_present": keys.isin(left.index),
            "right_present": keys.isin(right.index),
            "left_value": a,
            "right_value": b,
            "difference": a - b,
        },
        index=keys,
    )


def verify_examples() -> None:
    fixture = pd.DataFrame(
        {"site": ["south", "north", "north"], "metric": ["flow", "temp", "flow"]}
    )
    fixture["value"] = pd.array([4, pd.NA, 0], dtype="Float64")
    original = fixture.copy(deep=True)
    keyed = keyed_measurements(fixture)
    assert list(keyed.index) == [("north", "flow"), ("north", "temp"), ("south", "flow")]
    assert keyed.loc[("north", "flow")] == 0 and pd.isna(keyed.loc[("north", "temp")])
    pd.testing.assert_frame_equal(fixture, original)
    assert select_site(keyed, "north").index.nlevels == 2
    assert select_site(keyed, "absent").empty
    grid, present = observation_grid(keyed)
    assert bool(present.loc["north", "temp"]) and not bool(present.loc["south", "temp"])
    assert pd.isna(grid.loc["north", "temp"]) and pd.isna(grid.loc["south", "temp"])
    pd.testing.assert_series_equal(restore_observations(grid, present), keyed)
    pairs = pd.MultiIndex.from_tuples([("a__b", "c"), ("a", "b__c"), ('"', "λ")])
    encoded = encode_column_labels(pairs)
    assert encoded.is_unique
    assert [tuple(json.loads(label)) for label in encoded] == list(pairs)
    other = pd.Series(
        pd.array([10, 2, 9], dtype="Float64"),
        index=pd.MultiIndex.from_tuples(
            [("south", "flow"), ("north", "flow"), ("east", "flow")],
            names=["site", "metric"],
        ),
        name="value",
    )
    result = aligned_difference(keyed, other)
    assert list(result.index) == [
        ("east", "flow"),
        ("north", "flow"),
        ("north", "temp"),
        ("south", "flow"),
    ]
    assert result.loc[("north", "flow"), "difference"] == -2
    assert result.loc[("south", "flow"), "difference"] == -6
    assert not bool(result.loc[("east", "flow"), "left_present"])
    assert bool(result.loc[("north", "temp"), "left_present"])
    duplicate = pd.concat([fixture, fixture.iloc[[0]]], ignore_index=True)
    try:
        keyed_measurements(duplicate)
    except ValueError:
        pass
    else:
        raise AssertionError("Duplicate compound identity must be rejected")
    invalid = grid.copy()
    invalid.loc["south", "temp"] = 8
    try:
        restore_observations(invalid, present)
    except ValueError:
        pass
    else:
        raise AssertionError("An absent measured cell must not be silently discarded")
    print("python-pandas-05: all six reference contracts and boundary checks passed")


if __name__ == "__main__":
    verify_examples()
