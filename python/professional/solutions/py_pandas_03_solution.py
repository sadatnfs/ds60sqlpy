"""Reference implementation and exact boundary checks for python-pandas-03."""

from collections.abc import Callable

import numpy as np
import pandas as pd  # type: ignore[import-untyped]


def group_shares(frame: pd.DataFrame) -> pd.Series:
    if (
        frame["customer_id"].isna().any()
        or frame["amount"].isna().any()
        or not np.isfinite(frame["amount"]).all()
        or (frame["amount"] < 0).any()
    ):
        raise ValueError("Expected known customers and finite nonnegative amounts")
    total = frame.groupby("customer_id", sort=False)["amount"].transform("sum")
    return frame["amount"].div(total.where(total.ne(0)))


def ordered_lag(events: pd.DataFrame) -> pd.DataFrame:
    if (
        events["event_id"].isna().any()
        or events["event_id"].duplicated().any()
        or events["customer_id"].isna().any()
        or not isinstance(events["at"].dtype, pd.DatetimeTZDtype)
        or str(events["at"].dt.tz) != "UTC"
        or events["at"].isna().any()
    ):
        raise ValueError("Expected unique event identities, customers and UTC times")
    f = events[["event_id", "customer_id", "at", "amount"]].copy()
    f["_position"] = np.arange(len(f))
    f = f.sort_values(["customer_id", "at", "event_id"], kind="stable")
    f["previous_amount"] = f.groupby("customer_id", sort=False)["amount"].shift(1)
    return f.sort_values("_position")[["event_id", "previous_amount"]].reset_index(drop=True)


def prior_window_sum(events: pd.DataFrame, window: pd.Timedelta) -> pd.DataFrame:
    ordered_lag(events)
    if (
        pd.isna(window)
        or window <= pd.Timedelta(0)
        or events["amount"].isna().any()
        or not np.isfinite(events["amount"]).all()
    ):
        raise ValueError("Expected a positive window and finite amounts")
    by_time = events.groupby(["customer_id", "at"], as_index=False, sort=True)["amount"].sum()
    parts = []
    for customer, group in by_time.groupby("customer_id", sort=False):
        series = group.set_index("at")["amount"]
        prior = series.rolling(window=window, closed="left", min_periods=1).sum().fillna(0)
        part = prior.rename("prior_amount").reset_index()
        part["customer_id"] = customer
        parts.append(part)
    if not parts:
        return pd.DataFrame(
            {"event_id": events["event_id"].copy(), "prior_amount": pd.Series(dtype=float)}
        )
    lookup = pd.concat(parts, ignore_index=True)
    return events[["event_id", "customer_id", "at"]].merge(
        lookup, on=["customer_id", "at"], how="left", sort=False, validate="many_to_one"
    )[["event_id", "prior_amount"]]


def session_ids(events: pd.DataFrame, gap: pd.Timedelta) -> pd.DataFrame:
    ordered_lag(events)
    if pd.isna(gap) or gap <= pd.Timedelta(0):
        raise ValueError("Expected a positive inactivity threshold")
    f = events[["event_id", "customer_id", "at"]].copy()
    f["_position"] = np.arange(len(f))
    f = f.sort_values(["customer_id", "at", "event_id"], kind="stable")
    difference = f.groupby("customer_id", sort=False)["at"].diff()
    start = difference.isna() | difference.gt(gap)
    f["session_id"] = start.groupby(f["customer_id"], sort=False).cumsum().astype(int)
    return f.sort_values("_position")[["event_id", "session_id"]].reset_index(drop=True)


def last_event_per_customer(events: pd.DataFrame) -> pd.DataFrame:
    ordered_lag(events)
    return (
        events.sort_values(["customer_id", "at", "event_id"], kind="stable")
        .drop_duplicates("customer_id", keep="last")[["customer_id", "event_id", "at", "amount"]]
        .sort_values("customer_id", kind="stable")
        .reset_index(drop=True)
    )


def category_summary(frame: pd.DataFrame, categories: list[str]) -> pd.DataFrame:
    if (
        len(categories) != len(set(categories))
        or frame["category"].isna().any()
        or not frame["category"].isin(categories).all()
    ):
        raise ValueError("Expected unique declared categories and valid labels")
    if (
        not pd.api.types.is_numeric_dtype(frame["value"].dtype)
        or not np.isfinite(frame["value"].dropna().to_numpy(dtype=float)).all()
    ):
        raise ValueError("Known category measurements must be finite numeric values")
    f = frame[["category", "value"]].copy()
    f["category"] = pd.Categorical(f["category"], categories=categories, ordered=True)
    result = f.groupby("category", observed=False, sort=True)["value"].agg(
        row_count="size", known_count="count", total=lambda values: values.sum(min_count=1)
    )
    return result.reset_index()


def expect_value_error(call: Callable[[], object]) -> None:
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main() -> None:
    # Exercise 1: Use transform without changing event grain
    f = pd.DataFrame(
        {"customer_id": ["a", "a", "b", "b"], "amount": [1.0, 3.0, 0.0, 0.0]}, index=[0, 0, 1, 1]
    )
    r = group_shares(f)
    assert (
        np.allclose(r.iloc[:2], [0.25, 0.75])
        and r.iloc[2:].isna().all()
        and r.index.equals(f.index)
    )
    bad = f.copy()
    bad.iloc[0, 1] = -1
    expect_value_error(lambda: group_shares(bad))
    missing = pd.DataFrame({"customer_id": ["a"], "amount": pd.Series([pd.NA], dtype="Float64")})
    expect_value_error(lambda: group_shares(missing))
    # Exercise 2: Lag within customer using a stable tie break
    e = pd.DataFrame(
        {
            "event_id": [2, 1, 3, 4],
            "customer_id": ["a", "a", "a", "b"],
            "at": pd.to_datetime(
                ["2026-01-01T10:00Z", "2026-01-01T10:00Z", "2026-01-01T11:00Z", "2026-01-01T10:00Z"]
            ),
            "amount": [20.0, 10.0, 30.0, 99.0],
        }
    )
    r = ordered_lag(e)
    assert (
        r.event_id.tolist() == [2, 1, 3, 4]
        and r.loc[0, "previous_amount"] == 10
        and pd.isna(r.loc[1, "previous_amount"])
        and r.loc[2, "previous_amount"] == 20
        and pd.isna(r.loc[3, "previous_amount"])
    )
    # Exercise 3: Exclude every current-time event from a prior window
    w = pd.DataFrame(
        {
            "event_id": [1, 2, 3, 4],
            "customer_id": ["a"] * 4,
            "at": pd.to_datetime(
                ["2026-01-01T10:00Z", "2026-01-01T10:30Z", "2026-01-01T10:30Z", "2026-01-01T11:00Z"]
            ),
            "amount": [1.0, 2.0, 3.0, 4.0],
        }
    )
    r = prior_window_sum(w, pd.Timedelta("30min"))
    assert r.prior_amount.tolist() == [0, 1, 1, 5] and r.event_id.tolist() == [1, 2, 3, 4]
    expect_value_error(lambda: prior_window_sum(w, pd.Timedelta(0)))
    # Exercise 4: Turn an inactivity rule into session identity
    s = pd.DataFrame(
        {
            "event_id": [1, 2, 3, 4],
            "customer_id": ["a", "a", "a", "b"],
            "at": pd.to_datetime(
                ["2026-01-01T10:00Z", "2026-01-01T10:30Z", "2026-01-01T11:01Z", "2026-01-01T12:00Z"]
            ),
            "amount": [1, 1, 1, 1],
        }
    )
    assert session_ids(s, pd.Timedelta("30min")).session_id.tolist() == [1, 1, 2, 1]
    expect_value_error(lambda: session_ids(s, pd.Timedelta(0)))
    # Exercise 5: Choose one final event deterministically
    r = last_event_per_customer(e)
    assert r.customer_id.tolist() == ["a", "b"] and r.event_id.tolist() == [3, 4]
    tied = e[e.event_id.isin([1, 2])]
    assert last_event_per_customer(tied).event_id.tolist() == [2] and len(e) == 4
    # Exercise 6: Distinguish no rows from no known measurements
    f = pd.DataFrame(
        {"category": ["a", "a", "b"], "value": pd.Series([1, pd.NA, pd.NA], dtype="Float64")}
    )
    r = category_summary(f, ["a", "b", "c"])
    assert (
        r.category.tolist() == ["a", "b", "c"]
        and r.row_count.tolist() == [2, 1, 0]
        and r.known_count.tolist() == [1, 0, 0]
    )
    assert r.loc[0, "total"] == 1 and pd.isna(r.loc[1, "total"]) and pd.isna(r.loc[2, "total"])
    expect_value_error(
        lambda: category_summary(pd.DataFrame({"category": ["z"], "value": [1]}), ["a"])
    )
    print("python-pandas-03: all six normal and boundary contracts passed")


if __name__ == "__main__":
    main()
