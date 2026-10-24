"""Reference implementation and exact boundary checks for python-pandas-01."""

from collections.abc import Callable

import numpy as np
import pandas as pd  # type: ignore[import-untyped]


def aligned_difference(left: pd.Series, right: pd.Series) -> pd.Series:
    if (
        not left.index.is_unique
        or not right.index.is_unique
        or len(left) != len(right)
        or not left.index.isin(right.index).all()
    ):
        raise ValueError("Expected the same unique labels")
    return left - right.reindex(left.index)


def assign_by_label(frame: pd.DataFrame, name: str, values: pd.Series) -> pd.DataFrame:
    if (
        not frame.index.is_unique
        or not values.index.is_unique
        or len(frame) != len(values)
        or not frame.index.isin(values.index).all()
    ):
        raise ValueError("Assignment needs the same unique row identities")
    result = frame.copy()
    result[name] = values.reindex(frame.index)
    return result


def nullable_positive(values: pd.Series) -> pd.Series:
    if str(values.dtype) != "Int64":
        raise ValueError("Expected pandas nullable Int64")
    return values.gt(0)


def select_known_true(frame: pd.DataFrame, mask: pd.Series) -> pd.DataFrame:
    if (
        not frame.index.is_unique
        or not mask.index.is_unique
        or len(frame) != len(mask)
        or not frame.index.isin(mask.index).all()
        or str(mask.dtype) not in {"bool", "boolean"}
    ):
        raise ValueError("Expected one Boolean mask value per unique frame label")
    keep = mask.reindex(frame.index).fillna(False)
    return frame.loc[keep].copy()


def reindex_with_presence(values: pd.Series, labels: list[str]) -> pd.DataFrame:
    target = pd.Index(labels)
    if not values.index.is_unique or not target.is_unique:
        raise ValueError("Expected unique source and target labels")
    return pd.DataFrame(
        {"value": values.reindex(target), "present": target.isin(values.index)}, index=target
    )


def strict_concat(frames: list[pd.DataFrame]) -> pd.DataFrame:
    if not frames:
        raise ValueError("At least one typed frame is required")
    first = frames[0]
    if any(
        not frame.columns.equals(first.columns) or not frame.dtypes.equals(first.dtypes)
        for frame in frames
    ):
        raise ValueError("Batch columns and dtypes must match exactly")
    try:
        return pd.concat(frames, axis=0, verify_integrity=True)
    except ValueError as error:
        raise ValueError("Batch row identities must be globally unique") from error


def expect_value_error(call: Callable[[], object]) -> None:
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main() -> None:
    # Exercise 1: Subtract by validated identities
    a = pd.Series([20, 10], index=["b", "a"])
    b = pd.Series([1, 2], index=["a", "b"])
    r = aligned_difference(a, b)
    assert r.index.tolist() == ["b", "a"] and r.tolist() == [18, 9]
    expect_value_error(lambda: aligned_difference(a, b.iloc[:1]))
    expect_value_error(lambda: aligned_difference(a, pd.Series([1, 2], index=["a", "a"])))
    # Exercise 2: Assign without swapping entities
    frame = pd.DataFrame({"old": [1, 2]}, index=["b", "a"])
    values = pd.Series([100, 200], index=["a", "b"])
    r = assign_by_label(frame, "new", values)
    assert r["new"].tolist() == [200, 100] and "new" not in frame
    expect_value_error(
        lambda: assign_by_label(frame, "new", pd.Series([1, 2, 3], index=["a", "b", "c"]))
    )
    # Exercise 3: Keep unknown comparison results
    s = pd.Series([2, pd.NA, 0, -1], dtype="Int64")
    r = nullable_positive(s)
    assert str(r.dtype) == "boolean" and r.iloc[0] and pd.isna(r.iloc[1]) and not r.iloc[2]
    assert str(nullable_positive(pd.Series([], dtype="Int64")).dtype) == "boolean"
    expect_value_error(lambda: nullable_positive(pd.Series([1.0, np.nan])))
    # Exercise 4: Apply an explicit unknown-filter policy
    frame = pd.DataFrame({"x": [2, 1, 3]}, index=["b", "a", "c"])
    mask = pd.Series([True, pd.NA, False], index=["a", "b", "c"], dtype="boolean")
    r = select_known_true(frame, mask)
    assert r.index.tolist() == ["a"]
    r.loc["a", "x"] = 99
    assert frame.loc["a", "x"] == 1
    expect_value_error(
        lambda: select_known_true(frame, pd.Series([1, 0, 1], index=frame.index, dtype="Int64"))
    )
    # Exercise 5: Distinguish absent labels from unknown values
    s = pd.Series([pd.NA, 5], index=["a", "b"], dtype="Int64")
    r = reindex_with_presence(s, ["b", "a", "c"])
    assert r.index.tolist() == ["b", "a", "c"] and r["present"].tolist() == [True, True, False]
    assert (
        r.loc["b", "value"] == 5 and pd.isna(r.loc["a", "value"]) and pd.isna(r.loc["c", "value"])
    )
    expect_value_error(lambda: reindex_with_presence(s, ["a", "a"]))
    # Exercise 6: Append typed batches without hiding identity conflicts
    a = pd.DataFrame({"x": pd.Series([1], index=["a"], dtype="Int64")})
    b = pd.DataFrame({"x": pd.Series([2], index=["b"], dtype="Int64")})
    r = strict_concat([a, b])
    assert r.index.tolist() == ["a", "b"] and str(r["x"].dtype) == "Int64"
    expect_value_error(lambda: strict_concat([a, a]))
    expect_value_error(lambda: strict_concat([a, b.astype(float)]))
    expect_value_error(lambda: strict_concat([]))
    print("python-pandas-01: all six normal and boundary contracts passed")


if __name__ == "__main__":
    main()
