"""python-pandas-04: Chunked Data, Global Reductions, and Cross-Batch State.

Run the worked examples, then implement the six contracts below.
Official implementations remain in solutions/.
"""

from io import StringIO

import numpy as np
import pandas as pd  # type: ignore[import-untyped]


def mean_state(values: pd.Series) -> tuple[float, int]:
    """
    For a numeric Series containing finite values or missing entries, return accurate
    known-value sum and known-value count. Reject nonnumeric dtype or infinity with
    ValueError. An empty or all-missing numeric Series returns (0.0,0).
    """
    raise NotImplementedError("Implement mean_state")


def merge_means(states: list[tuple[float, int]]) -> float | None:
    """
    Combine sum/count states into one mean, returning None if total count is zero. Require
    finite sums and nonnegative integer counts; a zero-count state must have zero sum.
    Reject invalid states with ValueError.
    """
    raise NotImplementedError("Implement merge_means")


def customer_totals(chunks) -> pd.DataFrame:
    """
    Consume chunks with nonmissing string customer_id and nullable/integer amount_cents.
    Reject missing or nonstring customers, noninteger amount dtype, and totals outside
    signed int64 range. Return customer_id, row_count, known_count, total_cents sorted
    by customer, preserving missing totals when a customer has no known amounts.
    """
    raise NotImplementedError("Implement customer_totals")


def unique_records(chunks) -> pd.DataFrame:
    """
    Consume chunks with nonmissing integer event_id and amount_cents that is integer or
    missing. Keep the first occurrence of identical event records in encounter order. Reject
    any repeated ID with a different amount, including missing versus zero, with ValueError.
    """
    raise NotImplementedError("Implement unique_records")


def rolling_means(chunks, window: int):
    """
    Yield full-window row-count rolling means across an iterable of finite numeric
    one-dimensional chunks. Require a positive non-Boolean integer window. Do not reset
    history at a chunk boundary, and yield nothing before a full window exists.
    """
    raise NotImplementedError("Implement rolling_means")


def csv_chunks(text: str, chunksize: int):
    """
    Yield chunks from in-memory CSV text with exactly event_id, customer_id, amount_cents
    columns in that order. Parse IDs/amounts as Int64 and customers as string. Require
    positive integer chunksize, nonmissing IDs/customers and valid numeric text. Preserve
    missing amounts.
    """
    raise NotImplementedError("Implement csv_chunks")


def worked_examples() -> None:
    chunks = [pd.Series([1.0, 3.0]), pd.Series([100.0])]
    means = [chunk.mean() for chunk in chunks]
    correct = sum(chunk.sum() for chunk in chunks) / sum(chunk.count() for chunk in chunks)
    assert np.mean(means) == 51 and np.isclose(correct, 104 / 3)
    print("Wrong mean of means:", np.mean(means), "global mean:", correct)

    text = "event_id,customer_id,amount_cents\n1,a,10\n2,b,\n3,a,20\n"
    chunks = list(
        pd.read_csv(
            StringIO(text),
            chunksize=2,
            dtype={"event_id": "Int64", "customer_id": "string", "amount_cents": "Int64"},
        )
    )
    assert [len(chunk) for chunk in chunks] == [2, 1]
    assert chunks[0].amount_cents.isna().sum() == 1
    print("Typed chunk lengths:", [len(chunk) for chunk in chunks])


if __name__ == "__main__":
    worked_examples()
    print("Worked examples passed. Complete the six task functions and their boundary checks.")

# Exercise 1: Retain the correct mean denominator
# Prompt: For a numeric Series containing finite values or missing entries, return accurate
# known-value sum and known-value count. Reject nonnumeric dtype or infinity with ValueError. An
# empty or all-missing numeric Series returns (0.0,0).
# Expected: [1, NA,3] returns (4.0,2), not count 3. Empty Float64 and [NA] Float64 return (0.0,0);
# infinity fails.

# Exercise 2: Combine uneven chunks correctly
# Prompt: Combine sum/count states into one mean, returning None if total count is zero. Require
# finite sums and nonnegative integer counts; a zero-count state must have zero sum. Reject
# invalid states with ValueError.
# Expected: States(4,2),(100,1) yield 104/3. Adding(0,0) has no effect. Empty states return None;
# (5,0), negative count or Boolean count is rejected.

# Exercise 3: Reduce typed amounts across batches
# Prompt: Consume an iterable of chunks with nonmissing string customer_id and nullable/integer
# amount_cents. Reject
# missing customers, noninteger amount dtype or totals outside signed int64 range. Return
# customer_id, row_count, known_count, total_cents sorted by customer, preserving missing totals
# when a customer has no known amounts.
# Expected: Across chunks a:10, b:NA then a:20, b:NA, return a counts 2,2, total 30 and b counts
# 2,0, totalNA. Input chunk boundaries do not change the result.

# Exercise 4: Detect conflicts across chunk boundaries
# Prompt: Consume chunks with nonmissing integer event_id and amount_cents that is integer or
# missing. Keep the first occurrence of identical event records in encounter order. Reject any
# repeated ID with a different amount, including missing versus zero, with ValueError.
# Expected: Chunks[(1,10),(2, NA)] then[(1,10),(3,20)] return IDs 1,2,3. Repeating ID 2 with
# amount 0 raises ValueError; missing is not normalized to zero.

# Exercise 5: Carry rolling history across batches
# Prompt: Yield full-window row-count rolling means across an iterable of finite numeric
# one-dimensional chunks. Require a positive non-Boolean integer window. Do not reset history at a
# chunk boundary, and yield nothing before a full window exists.
# Expected: Chunks[1,2] then[3,4] with window 3 yield [2,3], the same as one chunk[1,2,3,4]. Empty
# input yields no values; window 0 and NaN input fail on iteration.

# Exercise 6: Make parsing a typed batch boundary
# Prompt: Yield chunks from in-memory CSV text with exactly event_id, customer_id, amount_cents
# columns in that order. Parse IDs/amounts as Int64 and customers as string. Require positive
# integer chunksize, nonmissing IDs/customers and valid numeric text. Preserve missing amounts.
# Expected: Three CSV rows with chunksize 2 yield lengths 2,1 and nullable Int64 amounts. An empty
# amount stays missing; amount bad or missing event_id raises ValueError during iteration.
