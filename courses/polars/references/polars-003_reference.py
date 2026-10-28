"""polars-003: complete bounded Polars investigation."""

from decimal import Decimal

import polars as pl


def example_one():
    raw = pl.DataFrame({"id": [1, 2, 3, 4], "units_text": ["2", "bad", None, "4"]})
    parsed = raw.with_columns(pl.col("units_text").cast(pl.Int64, strict=False).alias("units"))
    rejected = parsed.filter(pl.col("units_text").is_not_null() & pl.col("units").is_null())
    missing = parsed.filter(pl.col("units_text").is_null())
    assert rejected["id"].to_list() == [2] and missing["id"].to_list() == [3]
    assert parsed["units"].to_list() == [2, None, None, 4]
    try:
        raw.select(pl.col("units_text").cast(pl.Int64, strict=True))
    except pl.exceptions.InvalidOperationError:
        strict_failed = True
    else:
        strict_failed = False
    assert strict_failed
    return {"rejected_ids": [2], "missing_ids": [3], "strict_rejected_bad_token": strict_failed}


def example_two():
    amounts = pl.Series(
        "amount", [Decimal("0.10"), Decimal("0.20")], dtype=pl.Decimal(precision=12, scale=2)
    )
    assert amounts.sum() == Decimal("0.30")
    limits = pl.Series("n", [127, 128])
    converted = limits.cast(pl.Int8, strict=False)
    assert converted.to_list() == [127, None]
    assert limits.dtype == pl.Int64
    return {"decimal_total": str(amounts.sum()), "narrow_cast": converted.to_list()}


def main():
    print(example_one())
    print(example_two())
    print("polars-003 reference checks passed")


if __name__ == "__main__":
    main()
