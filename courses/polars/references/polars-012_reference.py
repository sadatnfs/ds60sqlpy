"""polars-012: complete bounded Polars investigation."""

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


def main():
    print(example_one())
    print(example_two())
    print("polars-012 reference checks passed")


if __name__ == "__main__":
    main()
