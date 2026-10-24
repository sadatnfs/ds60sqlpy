"""python-pandas-02: Join Contracts and Point-in-Time Feature Lookup.

Run the worked examples, then implement the six contracts below.
Official implementations remain in solutions/.
"""

import pandas as pd  # type: ignore[import-untyped]


def validate_dimension(frame: pd.DataFrame, key: str) -> None:
    """
    Validate that key exists, contains no missing values and is unique. Raise ValueError for
    a missing column, null key or repeated key. An empty frame with the key column is a
    valid empty dimension.
    """
    raise NotImplementedError("Implement validate_dimension")


def enrich_events(events: pd.DataFrame, dimension: pd.DataFrame) -> pd.DataFrame:
    """
    Require unique nonmissing event_id and a valid customer_id dimension. Left-join
    dimension segment onto event_id, customer_id, amount events with many-to-one validation
    and a match indicator. Preserve input event order and do not mutate either frame.
    """
    raise NotImplementedError("Implement enrich_events")


def missing_key_report(events: pd.DataFrame, dimension: pd.DataFrame) -> pd.DataFrame:
    """
    Return one diagnostic row per unmatched event with columns event_id and reason, sorted
    by event_id. Label null customer identifiers missing_key and nonnull identifiers absent
    from the dimension unknown_key. Validate event and dimension identities first.
    """
    raise NotImplementedError("Implement missing_key_report")


def latest_available(
    requests: pd.DataFrame, history: pd.DataFrame, tolerance: pd.Timedelta
) -> pd.DataFrame:
    """
    For a single history, attach the latest available_at, value no later than each request
    at time, within a nonnegative tolerance. Require unique request_id and unique history
    available_at, with nonmissing timezone-aware UTC time columns. Return original request
    order and preserve unmatched values as missing.
    """
    raise NotImplementedError("Implement latest_available")


def validate_intervals(history: pd.DataFrame) -> pd.DataFrame:
    """
    Validate a single version history with unique version_id and finite UTC start, end times
    satisfying start<end. Return it sorted by start. Reject any overlap, while permitting
    adjacent intervals where one end equals the next start.
    """
    raise NotImplementedError("Implement validate_intervals")


def validity_lookup(events: pd.DataFrame, history: pd.DataFrame) -> pd.DataFrame:
    """
    Use validated single-history half-open intervals to attach version_id, value to uniquely
    identified events at UTC instants. Return event_id, version_id, value in input event
    order. Preserve uncovered events with missing version/value and reject ambiguous
    histories.
    """
    raise NotImplementedError("Implement validity_lookup")


def worked_examples() -> None:
    events = pd.DataFrame({"event_id": [1, 2, 3], "customer_id": ["a", "b", "c"]})
    dimension = pd.DataFrame({"customer_id": ["a", "b"], "segment": ["small", "large"]})
    joined = events.merge(
        dimension, on="customer_id", how="left", validate="many_to_one", indicator=True
    )
    assert len(joined) == 3 and joined.loc[joined.event_id == 3, "_merge"].iloc[0] == "left_only"
    print("Join coverage:", joined[["event_id", "_merge"]].astype(str).values.tolist())

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


if __name__ == "__main__":
    worked_examples()
    print("Worked examples passed. Complete the six task functions and their boundary checks.")

# Exercise 1: Require one real identity per dimension row
# Prompt: Validate that key exists, contains no missing values and is unique. Raise ValueError for
# a missing column, null key or repeated key. An empty frame with the key column is a valid empty
# dimension.
# Expected: Keys[a, b] pass; [a, a], [a, None] and a frame without key fail. An empty customer_id
# column passes.

# Exercise 2: Preserve event grain during enrichment
# Prompt: Require unique nonmissing event_id and a valid customer_id dimension. Left-join
# dimension segment onto event_id, customer_id, amount events with many-to-one validation and a
# match indicator. Preserve input event order and do not mutate either frame.
# Expected: Events for customers a, c, b keep all three event_id values in input order; c has
# missing segment and left_only status. Duplicate dimension a raises ValueError.

# Exercise 3: Separate absent identifiers from unknown identifiers
# Prompt: Return one diagnostic row per unmatched event with columns event_id and reason, sorted
# by event_id. Label null customer identifiers missing_key and nonnull identifiers absent from the
# dimension unknown_key. Validate event and dimension identities first.
# Expected: Events 1:a,2:None,3:z with dimension[a] yield (2, missing_key),(3, unknown_key). A
# fully matched event yields an empty frame with both output columns.

# Exercise 4: Look backward within a freshness limit
# Prompt: For a single history, attach the latest available_at, value no later than each request
# at time, within a nonnegative tolerance. Require unique request_id and unique history
# available_at, with nonmissing timezone-aware UTC time columns. Return original request order and
# preserve unmatched values as missing.
# Expected: Requests at 10:30 and 15:00 with history at 10:00, value 10 and 12:00, value 20,
# tolerance 2 hours, yield 10 andmissing. Unsorted requests are restored to their original order;
# naive times fail.

# Exercise 5: Reject overlapping validity versions
# Prompt: Validate a single version history with unique version_id and finite UTC start, end times
# satisfying start<end. Return it sorted by start. Reject any overlap, while permitting adjacent
# intervals where one end equals the next start.
# Expected: Versions[10:00,11:00) and [11:00,12:00) pass; changing the second start to 10:59
# raises ValueError. A zero-width interval also fails.

# Exercise 6: Assign an instant to at most one version
# Prompt: Use validated single-history half-open intervals to attach version_id, value to uniquely
# identified events at UTC instants. Return event_id, version_id, value in input event order.
# Preserve uncovered events with missing version/value and reject ambiguous histories.
# Expected: Events at 10:00,11:00,12:00 against adjacent hourly versions 1,2 yield version 1,
# version 2, missing. The exact final end is excluded; gaps are not filled by nearest lookup.
