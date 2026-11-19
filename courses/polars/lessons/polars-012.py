"""polars-012: both worked cases; complete the guide's six changes."""

import polars as pl
import pyarrow as pa


def example_one():
    frame = pl.DataFrame({"id": [1, 2, 3], "value": [2.0, None, 4.0]})
    arrow = frame.to_arrow()
    assert arrow.column("id").to_pylist() == [1, 2, 3]
    assert arrow.column("value").null_count == 1
    restored = pl.from_arrow(arrow)
    assert restored.equals(frame)
    assert isinstance(arrow, pa.Table)
    return {"arrow_schema": str(arrow.schema), "round_trip": True, "nulls": 1}


def example_two():
    status = pl.Enum(["new", "paid", "shipped"])
    frame = pl.DataFrame({"status": ["shipped", "new", "paid"]}).with_columns(
        pl.col("status").cast(status)
    )
    assert frame.sort("status")["status"].cast(pl.String).to_list() == ["new", "paid", "shipped"]
    try:
        pl.Series(["unknown"]).cast(status)
    except pl.exceptions.InvalidOperationError:
        rejected = True
    else:
        rejected = False
    assert rejected
    return {"business_order": ["new", "paid", "shipped"], "unknown_rejected": rejected}


if __name__ == "__main__":
    print(example_one())
    print(example_two())

# TODO 1: Explain why a null is separate from a numeric payload value.
# TODO 2: State what the round-trip test actually proves.
# TODO 3: Extend the allowed states with returned.
# TODO 4: Add cancelled without changing the Enum.
# TODO 5: Compare business-order and alphabetical sorting.
# TODO 6: List what a receiver needs beyond an Arrow object.
