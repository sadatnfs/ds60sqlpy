"""Reference implementation and exact boundary checks for python-pandas-02."""

from collections.abc import Callable

import numpy as np
import pandas as pd  # type: ignore[import-untyped]


def validate_dimension(frame: pd.DataFrame, key: str) -> None:
    if key not in frame or frame[key].isna().any() or frame[key].duplicated().any():
        raise ValueError("Dimension keys must exist, be nonmissing and be unique")


def enrich_events(events: pd.DataFrame, dimension: pd.DataFrame) -> pd.DataFrame:
    validate_dimension(events, "event_id")
    validate_dimension(dimension, "customer_id")
    if not {"customer_id", "amount"}.issubset(events.columns) or "segment" not in dimension:
        raise ValueError("Expected event amount and dimension segment")
    return events[["event_id", "customer_id", "amount"]].merge(
        dimension[["customer_id", "segment"]],
        on="customer_id",
        how="left",
        sort=False,
        validate="many_to_one",
        indicator="dimension_status",
    )


def missing_key_report(events: pd.DataFrame, dimension: pd.DataFrame) -> pd.DataFrame:
    validate_dimension(events, "event_id")
    validate_dimension(dimension, "customer_id")
    events = events.reset_index(drop=True)
    missing = events["customer_id"].isna()
    unknown = ~events["customer_id"].isin(dimension["customer_id"]) & ~missing
    result = events.loc[missing | unknown, ["event_id"]].copy()
    result["reason"] = np.where(missing.loc[result.index], "missing_key", "unknown_key")
    return result.sort_values("event_id", kind="stable").reset_index(drop=True)


def latest_available(
    requests: pd.DataFrame, history: pd.DataFrame, tolerance: pd.Timedelta
) -> pd.DataFrame:
    validate_dimension(requests, "request_id")
    validate_dimension(history, "available_at")
    for series in [requests["at"], history["available_at"]]:
        if (
            not isinstance(series.dtype, pd.DatetimeTZDtype)
            or str(series.dt.tz) != "UTC"
            or series.isna().any()
        ):
            raise ValueError("Expected nonmissing timezone-aware UTC times")
    if pd.isna(tolerance) or tolerance < pd.Timedelta(0):
        raise ValueError("Expected a nonnegative freshness tolerance")
    left = requests[["request_id", "at"]].copy()
    left["_position"] = np.arange(len(left))
    right = history[["available_at", "value"]].sort_values("available_at")
    joined = pd.merge_asof(
        left.sort_values("at"),
        right,
        left_on="at",
        right_on="available_at",
        direction="backward",
        tolerance=tolerance,
    )
    return joined.sort_values("_position").drop(columns="_position").reset_index(drop=True)


def validate_intervals(history: pd.DataFrame) -> pd.DataFrame:
    validate_dimension(history, "version_id")
    for series in [history["start"], history["end"]]:
        if (
            not isinstance(series.dtype, pd.DatetimeTZDtype)
            or str(series.dt.tz) != "UTC"
            or series.isna().any()
        ):
            raise ValueError("Expected finite UTC interval endpoints")
    ordered = history.sort_values("start", kind="stable").copy()
    if (ordered["start"] >= ordered["end"]).any() or (
        ordered["start"].iloc[1:].to_numpy() < ordered["end"].iloc[:-1].to_numpy()
    ).any():
        raise ValueError("Intervals must be positive and nonoverlapping")
    return ordered


def validity_lookup(events: pd.DataFrame, history: pd.DataFrame) -> pd.DataFrame:
    validate_dimension(events, "event_id")
    ordered = validate_intervals(history)
    if (
        not isinstance(events["at"].dtype, pd.DatetimeTZDtype)
        or str(events["at"].dt.tz) != "UTC"
        or events["at"].isna().any()
    ):
        raise ValueError("Expected UTC event instants")
    rows = []
    for event in events[["event_id", "at"]].itertuples(index=False):
        match = ordered.loc[(ordered["start"] <= event.at) & (event.at < ordered["end"])]
        if match.empty:
            rows.append((event.event_id, pd.NA, np.nan))
        else:
            rows.append((event.event_id, match.iloc[0]["version_id"], match.iloc[0]["value"]))
    return pd.DataFrame(rows, columns=["event_id", "version_id", "value"])


def expect_value_error(call: Callable[[], object]) -> None:
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main() -> None:
    # Exercise 1: Require one real identity per dimension row
    validate_dimension(pd.DataFrame({"customer_id": ["a", "b"]}), "customer_id")
    validate_dimension(pd.DataFrame({"customer_id": []}), "customer_id")
    expect_value_error(
        lambda: validate_dimension(pd.DataFrame({"customer_id": ["a", "a"]}), "customer_id")
    )
    expect_value_error(
        lambda: validate_dimension(pd.DataFrame({"customer_id": [None]}), "customer_id")
    )
    expect_value_error(lambda: validate_dimension(pd.DataFrame({"x": [1]}), "customer_id"))
    # Exercise 2: Preserve event grain during enrichment
    e = pd.DataFrame(
        {"event_id": [3, 1, 2], "customer_id": ["a", "c", "b"], "amount": [10, 20, 30]}
    )
    d = pd.DataFrame({"customer_id": ["a", "b"], "segment": ["x", "y"]})
    r = enrich_events(e, d)
    assert r.event_id.tolist() == [3, 1, 2] and r.dimension_status.astype(str).tolist() == [
        "both",
        "left_only",
        "both",
    ]
    assert len(r) == len(e) and "segment" not in e
    expect_value_error(lambda: enrich_events(e, pd.concat([d, d.iloc[:1]])))
    # Exercise 3: Separate absent identifiers from unknown identifiers
    e = pd.DataFrame({"event_id": [3, 1, 2], "customer_id": ["z", "a", None]})
    d = pd.DataFrame({"customer_id": ["a"]})
    r = missing_key_report(e, d)
    assert list(r.itertuples(index=False, name=None)) == [(2, "missing_key"), (3, "unknown_key")]
    e.index = [0, 0, 0]
    assert list(missing_key_report(e, d).itertuples(index=False, name=None)) == [
        (2, "missing_key"),
        (3, "unknown_key"),
    ]
    assert missing_key_report(e[e.event_id == 1], d).columns.tolist() == ["event_id", "reason"]
    # Exercise 4: Look backward within a freshness limit
    r = pd.DataFrame(
        {"request_id": [2, 1], "at": pd.to_datetime(["2026-01-01T15:00Z", "2026-01-01T10:30Z"])}
    )
    h = pd.DataFrame(
        {
            "available_at": pd.to_datetime(["2026-01-01T12:00Z", "2026-01-01T10:00Z"]),
            "value": [20.0, 10.0],
        }
    )
    x = latest_available(r, h, pd.Timedelta("2h"))
    assert (
        x.request_id.tolist() == [2, 1] and pd.isna(x.loc[0, "value"]) and x.loc[1, "value"] == 10
    )
    naive = r.copy()
    naive["at"] = naive["at"].dt.tz_localize(None)
    expect_value_error(lambda: latest_available(naive, h, pd.Timedelta("2h")))
    # Exercise 5: Reject overlapping validity versions
    h = pd.DataFrame(
        {
            "version_id": [1, 2],
            "start": pd.to_datetime(["2026-01-01T10:00Z", "2026-01-01T11:00Z"]),
            "end": pd.to_datetime(["2026-01-01T11:00Z", "2026-01-01T12:00Z"]),
            "value": [10, 20],
        }
    )
    assert len(validate_intervals(h)) == 2
    bad = h.copy()
    bad.loc[1, "start"] = pd.Timestamp("2026-01-01T10:59Z")
    expect_value_error(lambda: validate_intervals(bad))
    bad = h.copy()
    bad.loc[0, "end"] = bad.loc[0, "start"]
    expect_value_error(lambda: validate_intervals(bad))
    # Exercise 6: Assign an instant to at most one version
    e = pd.DataFrame(
        {
            "event_id": [1, 2, 3],
            "at": pd.to_datetime(["2026-01-01T10:00Z", "2026-01-01T11:00Z", "2026-01-01T12:00Z"]),
        }
    )
    r = validity_lookup(e, h)
    assert (
        r.event_id.tolist() == [1, 2, 3]
        and r.loc[0, "version_id"] == 1
        and r.loc[1, "version_id"] == 2
        and pd.isna(r.loc[2, "version_id"])
    )
    assert pd.isna(r.loc[2, "value"])
    print("python-pandas-02: all six normal and boundary contracts passed")


if __name__ == "__main__":
    main()
