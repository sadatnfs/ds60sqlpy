# polars-003: Types, parsing failures and exact numeric values

## Level and prerequisites

Beginner. Direct prerequisites: `polars-001`, `polars-002`

**Outcome:** Implement a parsing policy that preserves rejected evidence.

## Question and mechanism

A dtype is part of the meaning of a column. Text containing digits is still text until parsing establishes a numeric interpretation. A strict cast rejects an unparseable token; a permissive cast represents failed conversions as null. Neither option automatically distinguishes a genuinely absent value from malformed source text, so preserve the raw field and the identifier while investigating rejection.

The first case starts with four records and classifies their outcomes. One record is missing at ingestion, while another contains the word bad. Treating both as zero would hide two different data-quality situations. A quarantine table keeps enough original information to diagnose the problem without contaminating the accepted calculation. In production, the action might be rejection, correction or explicit imputation, but the reason should remain available.

Precision is a separate contract. Binary floating-point is suitable for many scientific approximations but does not represent every decimal fraction exactly. Decimal stores scaled decimal values with an explicit precision and scale. Integer casts also have finite bounds. Narrowing 128 to signed 8-bit storage cannot preserve its value; an explicit failure or null is safer than assuming every smaller dtype is an interchangeable optimization.

## Syntax and data contract

cast(pl.Int64, strict=False) changes the parsed column while retaining failed conversions as null. Combine is_not_null on the raw field with is_null on the parsed field to identify invalid tokens. pl.Decimal(precision=12, scale=2) declares twelve decimal digits with two fractional positions. Choose its range from the data contract, and inspect the result of any arithmetic or cast that changes precision.

## Run the lesson

Open this subject in `/classroom`, then show its code and notes. The prepared `data-engineering` worker runs `main.py` in a fresh temporary directory. The examples use installed packages and synthetic local fixtures; no account, cloud service, network request or package download is required. Save source and notes before switching lessons. Temporary databases, project files and tracking artifacts are recreated by each complete program and removed after the job. The classroom retains the submitted source and bounded output, not an indefinitely running external service. The guide distinguishes this local execution from the deployment decisions that need an owned production environment.



## Worked case 1: Separate missing input from invalid input

The first program keeps id and units_text, derives units, and creates separate invalid and missing subsets. It also executes the strict path to prove that the invalid token is rejected. This demonstrates a policy choice with observable consequences rather than silently using a permissive conversion.

**Expected evidence:** Record 2 is malformed, record 3 is missing, and parsed units are[2,null,null,4].

```python
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


if __name__ == "__main__":
    print(example_one())
```


## Worked case 2: Decimal arithmetic and narrowing bounds

The second program constructs decimal values from strings, so binary approximation is not introduced before the Decimal object exists. It contrasts exact decimal addition with a narrowing integer conversion whose second value is outside the target range.

**Expected evidence:** Decimal total is 0.30; the Int8 conversion gives[127,null].

```python
from decimal import Decimal

import polars as pl


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
    print(example_two())
```


## Practice

Make each requested change in a saved copy. Compare both the expected result and the deliberately changed assumption. The separate reference explains the answers.


### 1. Introduce a whitespace token

Replace bad with a whitespace-only string and define its category.

**Check:** Your policy explicitly classifies it before numeric conversion.

**Hint:** Use string stripping while preserving the raw token.


### 2. Keep a rejection denominator

Compute the malformed share of the original four records.

**Check:** Malformed share is 1/4, separately from 1/4 missing.

**Hint:** Use original row count.


### 3. Make rejection fail closed

Require that every nonmissing numeric token parses.

**Check:** The original fixture raises a deliberate validation error.

**Hint:** Count invalid rows before returning clean data.


### 4. Investigate a bound

Try values-129,-128,127,128 as Int8.

**Check:** Only-128 and 127 are representable.

**Hint:** Signed 8-bit values have 256 states.


### 5. Avoid early float conversion

Construct Decimal values using strings rather than floats.

**Check:** The 0.10+0.20 result remains exactly 0.30.

**Hint:** Conversion after approximation cannot recover an unknown intended decimal.


### 6. Specify rounding

Describe how a third decimal place should be handled before storage at scale 2.

**Check:** The rule names rounding mode and treatment of ties.

**Hint:** A display format is not a data policy.


## Diagnose errors and misleading results

A permissive cast that increases null counts is not automatically data loss: it may be correct rejection of bad text. It becomes an analysis defect when the original token, count or reason disappears. Check integer bounds before narrowing and retain exact input strings for decimal parsing. Locale-specific separators, percent signs and mixed units need explicit parsing rules; stripping every nondigit can manufacture plausible but incorrect numbers.

## Transfer to independent work

Implement a parsing policy that preserves rejected evidence. Extend the fixture with one malformed token, one missing token and one out-of-range value, and reconcile every original identifier into exactly one outcome. For scientific measurements, also state approximation tolerance; for exact decimal quantities, state scale and rounding independently of display formatting.

## Primary references

- [Polars documentation: Types, parsing failures and exact numeric values](https://docs.pola.rs/user-guide/expressions/casting/)
- [Polars Python API reference](https://docs.pola.rs/api/python/stable/reference/index.html)

## Tutor guidance

Use the repository learning-companion skill for `polars-003`. Inspect the learner's own source and observations, ask for an explanation of the relevant data or state contract, and give a focused hint. Separate an assertion on this fixture from a claim about an external dataset or deployed service.
