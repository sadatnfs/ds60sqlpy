"""python-pandas-03: Grouped Transforms, Temporal Windows, and Session Boundaries.

Run the worked examples, then implement the six contracts below.
Official implementations remain in solutions/.
"""

import pandas as pd  # type: ignore[import-untyped]


def group_shares(frame: pd.DataFrame) -> pd.Series:
    """
    For nonmissing customer_id and finite nonnegative amount, return each row amount divided
    by its customer total, preserving the original index. For an all-zero customer return
    missing shares rather than dividing zero by zero. Do not mutate frame.
    """
    raise NotImplementedError("Implement group_shares")


def ordered_lag(events: pd.DataFrame) -> pd.DataFrame:
    """
    Return event_id and previous_amount for each event, preserving input event order. Sort
    within customer by at then event_id, and use the previous row only within that customer.
    Require unique nonmissing event_id, known customer_id and nonmissing UTC timestamps.
    """
    raise NotImplementedError("Implement ordered_lag")


def prior_window_sum(events: pd.DataFrame, window: pd.Timedelta) -> pd.DataFrame:
    """
    Return event_id and prior_amount for each event over its customer interval[at-window,
    at). Require unique event IDs, known customers, finite amounts and UTC times; window
    must be positive. Equal-time events must receive identical prior sums. Empty prior
    windows have known sum zero.
    """
    raise NotImplementedError("Implement prior_window_sum")


def session_ids(events: pd.DataFrame, gap: pd.Timedelta) -> pd.DataFrame:
    """
    Return event_id and a one-based session_id within each customer, preserving input order.
    Sort by at, event_id and start a new session only when elapsed gap is strictly greater
    than the positive threshold. Reuse identity/time validation from ordered_lag.
    """
    raise NotImplementedError("Implement session_ids")


def last_event_per_customer(events: pd.DataFrame) -> pd.DataFrame:
    """
    Return one row per customer with customer_id, event_id, at, amount, choosing greatest at
    then greatest event_id. Sort final rows by customer_id. Validate event/time identity
    using ordered_lag and preserve the original input.
    """
    raise NotImplementedError("Implement last_event_per_customer")


def category_summary(frame: pd.DataFrame, categories: list[str]) -> pd.DataFrame:
    """
    Summarize declared unique categories in their declared order with category, row_count,
    known_count, total. Reject missing/undeclared category labels and nonnumeric or
    nonfinite known measurements. Include unobserved categories with row_count0,
    known_count0, total missing; an observed all-missing category also has missing total.
    """
    raise NotImplementedError("Implement category_summary")


def worked_examples() -> None:
    frame = pd.DataFrame({"customer_id": ["a", "a", "b"], "amount": [1.0, 3.0, 8.0]})
    total = frame.groupby("customer_id", sort=False)["amount"].transform("sum")
    share = frame.amount / total
    assert share.tolist() == [0.25, 0.75, 1.0]
    assert len(total) == len(frame)
    print("Aligned group shares:", share.tolist())

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


if __name__ == "__main__":
    worked_examples()
    print("Worked examples passed. Complete the six task functions and their boundary checks.")

# Exercise 1: Use transform without changing event grain
# Prompt: For nonmissing customer_id and finite nonnegative amount, return each row amount divided
# by its customer total, preserving the original index. For an all-zero customer return missing
# shares rather than dividing zero by zero. Do not mutate frame.
# Expected: Customers[a, a, b, b] with amounts[1,3,0,0] yield [.25,.75, NaN, NaN]. Duplicate
# incidental index labels are allowed; a negative amount raises ValueError.

# Exercise 2: Lag within customer using a stable tie break
# Prompt: Return event_id and previous_amount for each event, preserving input event order. Sort
# within customer by at then event_id, and use the previous row only within that customer. Require
# unique nonmissing event_id, known customer_id and nonmissing UTC timestamps.
# Expected: For customer a events(id 2, time 10:00, amount 20),(id 1, time 10:00, amount 10),(id
# 3, time 11:00, amount 30), previous values in original order are 10, missing,20. Another
# customer starts with missing.

# Exercise 3: Exclude every current-time event from a prior window
# Prompt: Return event_id and prior_amount for each event over its customer interval[at-window,
# at). Require unique event IDs, known customers, finite amounts and UTC times; window must be
# positive. Equal-time events must receive identical prior sums. Empty prior windows have known
# sum zero.
# Expected: Customer a amounts at 10:00=1,10:30=2,10:30=3,11:00=4 with a 30-minute window yield
# prior sums[0,1,1,5]. The lower boundary counts and the current timestamp never counts.

# Exercise 4: Turn an inactivity rule into session identity
# Prompt: Return event_id and a one-based session_id within each customer, preserving input order.
# Sort by at, event_id and start a new session only when elapsed gap is strictly greater than the
# positive threshold. Reuse identity/time validation from ordered_lag.
# Expected: Times 10:00,10:30,11:01 with 30-minute threshold give sessions 1,1,2. Every other
# customer starts at 1; zero or negative threshold is rejected.

# Exercise 5: Choose one final event deterministically
# Prompt: Return one row per customer with customer_id, event_id, at, amount, choosing greatest at
# then greatest event_id. Sort final rows by customer_id. Validate event/time identity using
# ordered_lag and preserve the original input.
# Expected: Two equal-time events for a with IDs 1 and 2 choose 2. Customer b keeps its own last
# event. Output contains each customer once and sorted customer IDs.

# Exercise 6: Distinguish no rows from no known measurements
# Prompt: Summarize declared unique categories in their declared order with category, row_count,
# known_count, total. Reject missing/undeclared category labels and nonnumeric or nonfinite known
# measurements. Include unobserved categories with row_count0, known_count0, total missing; an
# observed all-missing category also has missing total.
# Expected: Rows a:1, a:NA, b:NA and declared [a, b, c] yield counts(2,1),(1,0),(0,0) and totals
# 1, missing, missing. Unknown category z is rejected.
