"""polars-003: both worked cases; complete the guide's six changes."""

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


if __name__ == "__main__":
    print(example_one())
    print(example_two())

# TODO 1: Replace bad with a whitespace-only string and define its category.
# TODO 2: Compute the malformed share of the original four records.
# TODO 3: Require that every nonmissing numeric token parses.
# TODO 4: Try the values -129, -128, 127 and 128 as Int8.
# TODO 5: Construct Decimal values using strings rather than floats.
# TODO 6: Describe how a third decimal place should be handled before storage at scale 2.
