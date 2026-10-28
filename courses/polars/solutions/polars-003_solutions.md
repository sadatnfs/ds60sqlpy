# polars-003: explained reference

Implement a parsing policy that preserves rejected evidence.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Introduce a whitespace token

A blank-after-trimming policy may convert it to missing. Keep an invalid_reason field so this is not confused with an unparseable nonblank token.

**Expected:** Your policy explicitly classifies it before numeric conversion.

## 2. Keep a rejection denominator

The two rates have different categories. Using only accepted rows as denominator would overstate a rejection fraction.

**Expected:** Malformed share is 1/4, separately from 1/4 missing.

## 3. Make rejection fail closed

Check the quarantine height and raise a descriptive error. A successful query is not equivalent to an accepted data contract.

**Expected:** The original fixture raises a deliberate validation error.

## 4. Investigate a bound

The permitted interval is[-128,127]. Keep strict mode for a mandatory bound or retain null plus a rejection reason under a permissive policy.

**Expected:** Only-128 and 127 are representable.

## 5. Avoid early float conversion

Use Decimal("0.10") and a declared scale. This states the data representation; it does not infer a currency or a rounding policy.

**Expected:** The 0.10+0.20 result remains exactly 0.30.

## 6. Specify rounding

Use a deliberate rounding operation at the business boundary, then validate range and scale. Test positive and negative tie cases, not only convenient non-ties.

**Expected:** The rule names rounding mode and treatment of ties.

## Complete reference

```python
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
```

## Interpretation

Implement a parsing policy that preserves rejected evidence. Extend the fixture with one malformed token, one missing token and one out-of-range value, and reconcile every original identifier into exactly one outcome. For scientific measurements, also state approximation tolerance; for exact decimal quantities, state scale and rounding independently of display formatting.
