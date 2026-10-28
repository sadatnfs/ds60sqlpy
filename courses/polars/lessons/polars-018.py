"""polars-018: worked starting point; complete the guide's six changes."""

import polars as pl


def example_one():
    raw = pl.DataFrame(
        {
            "event_id": [1, 2, 2, 3, 4],
            "customer": [10, 10, 10, 20, 20],
            "amount_text": ["5", "7", "7", "bad", "9"],
            "time": [1, 2, 2, 3, 4],
        }
    )
    parsed = raw.with_columns(pl.col("amount_text").cast(pl.Int64, strict=False).alias("amount"))
    quarantine = parsed.filter(pl.col("amount").is_null())
    clean = parsed.filter(pl.col("amount").is_not_null()).unique(subset="event_id").sort("event_id")
    result = (
        clean.group_by("customer")
        .agg(pl.col("amount").sum().alias("total"), pl.len().alias("events"))
        .sort("customer")
    )
    assert quarantine["event_id"].to_list() == [3]
    assert clean.height == 3 and result.to_dicts() == [
        {"customer": 10, "total": 12, "events": 2},
        {"customer": 20, "total": 9, "events": 1},
    ]
    assert raw.height == clean.height + quarantine.height + 1
    return {"result": result.to_dicts(), "rejected": 1, "duplicate_rows": 1}


if __name__ == "__main__":
    print(example_one())

# TODO 1: Change one repeated event amount while keeping its id.
# TODO 2: Write the complete row-accounting equation.
# TODO 3: Assert one output row per customer.
# TODO 4: Change the output bytes after writing its receipt.
# TODO 5: Explain byte identity versus logical table equality.
# TODO 6: Specify what a model-training consumer must verify.
