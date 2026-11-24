# polars-003: explained reference

Implement a parsing policy that preserves rejected evidence.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Introduce a whitespace token

A blank-after-trimming policy may convert it to missing. Keep an invalid_reason field so this is not confused with an unparseable nonblank token.

```python
import polars as pl

raw = pl.DataFrame({"id": [1, 2, 3, 4], "units_text": ["2", "   ", None, "4"]})
classified = raw.with_columns(
    pl.when(pl.col("units_text").is_null())
    .then(pl.lit("missing"))
    .when(pl.col("units_text").str.strip_chars() == "")
    .then(pl.lit("blank"))
    .otherwise(pl.lit("text"))
    .alias("category")
)
assert classified["category"].to_list() == ["text", "blank", "missing", "text"]
```

**Why it holds here:** A whitespace-only string is neither null nor parseable. Classifying it before any cast gives it its own blank category, separate from missing (id 3) and from text.

**Plausible wrong approach:** Casting directly with strict=False turns the blank into null, which merges it with the genuinely missing row and loses the reason.

**How to verify:** Run the answer code and assert category is ['text', 'blank', 'missing', 'text'].

**Expected:** Your policy explicitly classifies it before numeric conversion.

## 2. Keep a rejection denominator

The two rates have different categories. Using only accepted rows as denominator would overstate a rejection fraction.

```python
import polars as pl

raw = pl.DataFrame({"id": [1, 2, 3, 4], "units_text": ["2", "bad", None, "4"]})
parsed = raw.with_columns(pl.col("units_text").cast(pl.Int64, strict=False).alias("units"))
shares = parsed.select(
    (pl.col("units_text").is_not_null() & pl.col("units").is_null()).mean().alias("malformed"),
    pl.col("units_text").is_null().mean().alias("missing"),
)
assert shares.row(0) == (0.25, 0.25)
```

**Why it holds here:** The rejection share uses all four original records as the denominator. One malformed token (bad) and one null each give 0.25.

**Plausible wrong approach:** Dividing the one rejected row by only the three non-missing rows gives 1/3, which mixes two categories into the denominator.

**How to verify:** Run the answer code and assert shares.row(0) == (0.25, 0.25).

**Expected:** Malformed share is 1/4, separately from 1/4 missing.

## 3. Make rejection fail closed

Check the quarantine height and raise a descriptive error. A successful query is not equivalent to an accepted data contract.

**Why it holds here:** Fail closed means a parsing gap stops the pipeline. Here the rejected filter returns id 2, so a check on its height must raise.

**Plausible wrong approach:** Letting strict=False finish and reporting success hides that one value was dropped.

**How to verify:** Add a guard that raises ValueError listing rejected['id'].to_list() whenever rejected.height is above 0, and confirm the original fixture stops with id 2 named in the message.

**Expected:** The original fixture raises a deliberate validation error.

## 4. Investigate a bound

The permitted interval is [-128, 127]. Keep strict mode for a mandatory bound or retain null plus a rejection reason under a permissive policy.

**Why it holds here:** Int8 holds -128 through 127. With strict=False, -129 and 128 become null, while -128 and 127 survive.

**Plausible wrong approach:** Assuming the cast wraps around, as in some C code, would predict 128 becomes -128; Polars returns null instead.

**How to verify:** Cast `pl.Series([-129, -128, 127, 128])` with `strict=False` and expect `[None, -128, 127, None]`.

**Expected:** Only -128 and 127 are representable.

## 5. Avoid early float conversion

Use Decimal("0.10") and a declared scale. This states the data representation; it does not infer a currency or a rounding policy.

**Why it holds here:** Decimal('0.10') stores exactly two hundredths, so the sum is exactly 0.30, as example_two asserts.

**Plausible wrong approach:** Adding floats 0.1 and 0.2 gives 0.30000000000000004, and Decimal(0.1) carries the long binary expansion of the float.

**How to verify:** Build the Series from strings with scale 2 and assert sum == Decimal('0.30').

**Expected:** The 0.10+0.20 result remains exactly 0.30.

## 6. Specify rounding

Use a deliberate rounding operation at the business boundary, then validate range and scale. Test positive and negative tie cases, not only convenient non-ties.

**Why it holds here:** A value like 0.125 must be rounded to two places before storage. The rule must say how ties go: half-even gives 0.12 and half-up gives 0.13.

**Plausible wrong approach:** Letting storage truncate or round silently means the result depends on the engine.

**How to verify:** Quantize Decimal('0.125') and Decimal('-0.125') to Decimal('0.01') in Python: ROUND_HALF_EVEN gives 0.12 and -0.12, ROUND_HALF_UP gives 0.13 and -0.13. Your test should pin one of those pairs.

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

Extend the fixture with one malformed token, one missing token and one out-of-range value, and reconcile every original identifier into exactly one outcome. For scientific measurements, also state approximation tolerance; for exact decimal quantities, state scale and rounding independently of display formatting.
