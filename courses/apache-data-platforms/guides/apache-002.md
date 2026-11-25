# apache-002: Rows, columns, types and missing values

Tutorial mode. Stage: beginner. Direct prerequisites: `apache-001`.

## Key terms

- **Arrow schema:** The ordered list of named, typed fields, with nullability and optional metadata, that tells every consumer how to interpret an Arrow table's columns.
- **Decimal type:** A fixed-point type that stores a signed integer coefficient and a declared scale s, so the value is the coefficient divided by 10 to the power s. It represents amounts such as 12.50 exactly, unlike a binary floating-point value.
- **Precision and scale:** Precision is the maximum number of decimal digits a decimal type can hold; scale is how many of those digits follow the decimal point.
- **Nullability:** A field property stating whether a value may be absent. It records that a value can be missing, not why it is missing.
- **Schema compatibility:** Whether data written with one schema can be read under another without changing its meaning. The chapter rejects an incompatible schema instead of silently coercing values.

## Types are part of the analytical definition

A column named amount does not tell you whether it contains dollars, cents,
floating-point approximations or decimal values. A timestamp without a time-zone
contract can describe different instants to different consumers. An identifier
that happens to contain digits may still be a label whose leading zeros matter.
Good platform design makes these choices explicit before data crosses a file,
process or language boundary.

Arrow schemas describe logical fields using concrete types. A signed integer
has a range. A decimal has precision and scale. A string is not automatically a
category or a parsed date. Nullability says whether a value may be absent, but it
does not explain why it is absent. Business interpretation remains an additional
contract. Missing because a sensor failed is different from missing because a
measurement is not applicable, even when both are stored as a null.

For a decimal with scale \(s\), a value can be understood as a signed integer
coefficient divided by \(10^s\). Precision bounds the number of decimal digits
that can be represented. This lets an application preserve values such as 12.50
without relying on the binary approximation of a floating-point fraction. It
does not remove the need to specify rounding rules when multiplying, dividing or
converting between decimal scales.

## Worked case A: preserve monetary units and missingness

The first case builds a decimal column with values 12.50, missing and 7.25.
The exact observed total is 19.75. A separate integer-minor-unit calculation gives
1975 cents, which agrees after an explicit conversion. This agreement is a useful
cross-representation check. It would not hold if one input column used cents and
another used dollars without conversion.

The mean over the two observed values is 9.875. Filling the missing entry with
zero and dividing by three gives a different quantity. The example records both
the valid count and the full row count, because a numeric total alone cannot tell
a reader which denominator was used. A financial report might legitimately use
zero for a confirmed absence of revenue. It should not use zero for an unreadable
or missing source record without documenting the policy.

The program also attempts to build a decimal value outside the declared
precision. The expected rejection is part of the worked case. A pipeline that
catches this error and silently converts the field to string has changed the
schema contract. If a schema must widen, that change should be explicit and
checked by downstream consumers.

## Worked case B: identifiers and schema compatibility

The second case uses identifiers `001` and `1` as distinct labels. Converting
both to integers collapses them to the same number. That conversion would make a
later join ambiguous even though it looks harmless in a spreadsheet. The Arrow
string column preserves the exact labels, and the program demonstrates the
collision using an intentionally lossy integer conversion.

Next, two tables with the same field names but incompatible types are compared.
One amount field is decimal, while the other is string. Their schemas differ,
and strict table concatenation rejects the mismatch. Matching names alone is
therefore insufficient to prove interoperability. The failure occurs before a
consumer accidentally orders monetary values lexicographically or treats a
missing decimal as an empty string.

Nullable fields also deserve attention when schemas are merged. Relaxing a field
from required to optional allows records that earlier code may not handle.
Tightening it in the opposite direction can invalidate historical records. A
successful schema parse does not prove that the stored population satisfies the
new requirement. The operation needs an explicit validation or migration plan.

## Mistakes, diagnosis and decision

Do not infer an identifier type from one convenient sample. Do not round before
a calculation unless the metric requires it. Do not turn every parse failure into
null and then report a clean observed-only mean: that can systematically exclude
expensive or unusual cases. Keep parse-error counts separate from ordinary missing
values, and preserve enough source identity to investigate the rejected rows.

**Interview discussion: is using decimal always better than floating point?**
Use a representation that fits the quantity. Decimal is useful when exact base-ten
amounts and explicit rounding rules are required. Floating point is appropriate
for many scientific measurements and numerical algorithms, with a documented
error model. Integer minor units can simplify fixed-scale money. The correct
choice is a semantic and operational decision, not a universal ranking of types.
The next chapter separates these logical choices from files and table commits.

## Worked examples

### Sum decimal money without float drift

```python
from decimal import Decimal

import pyarrow as pa
import pyarrow.compute as pc

prices = pa.array([Decimal("12.50"), None, Decimal("7.25")], type=pa.decimal128(9, 2))
print(pc.sum(prices))
print(pc.count(prices), prices.null_count)
print(0.1 + 0.2)
```

```text
19.75
2 1
0.30000000000000004
```

The decimal sum prints 19.75 exactly, and the counts show two observed values plus one null, so a mean must divide by two. The float line beside it prints a value just above 0.3, which is the drift a binary float column would carry into a ledger. Check the result type of an aggregate too: a decimal sum can widen precision, and a downstream schema with narrower precision will reject it instead of rounding.

### Reject a decimal that exceeds declared precision

```python
from decimal import Decimal

import pyarrow as pa

try:
    pa.array([Decimal("123456.789")], type=pa.decimal128(5, 2))
except pa.ArrowInvalid as error:
    print("rejected:", type(error).__name__)
print(pa.array(["001", "1"]).unique().to_pylist())
```

```text
rejected: ArrowInvalid
['001', '1']
```

Arrow refuses to store 123456.789 in a decimal with five digits of precision instead of silently truncating it, which is the behavior a contract wants at a boundary. The second line keeps the identifiers 001 and 1 as two distinct strings, a reminder that casting identifiers to integers merges keys that a source system treats as different. Treat a precision error as a schema decision to escalate, not a value to clip.

## Complete worked source

Run it as the [worked program rules](../STUDY-GUIDE.md#worked-programs) describe.

```python
from decimal import Decimal

import pyarrow as pa
import pyarrow.compute as pc

money = pa.array([Decimal("12.50"), None, Decimal("7.25")], type=pa.decimal128(10, 2))
assert pc.sum(money).as_py() == Decimal("19.75")
minor = [1250, None, 725]
assert sum(x for x in minor if x is not None) == 1975
valid_count = len(money) - money.null_count
assert valid_count == 2 and len(money) == 3
observed_mean = pc.sum(money).as_py() / valid_count
zero_filled_mean = pc.sum(money).as_py() / len(money)
assert observed_mean == Decimal("9.875") and zero_filled_mean != observed_mean
try:
    pa.array([Decimal("1234.56")], type=pa.decimal128(5, 2))
except pa.ArrowInvalid:
    print("Precision overflow rejected")
else:
    raise AssertionError("Expected a precision failure")
identifiers = pa.array(["001", "1"], type=pa.string())
assert len(set(identifiers.to_pylist())) == 2
assert len({int(value) for value in identifiers.to_pylist()}) == 1
left = pa.table({"amount": money})
right = pa.table({"amount": pa.array(["12.50", None, "7.25"])})
assert not left.schema.equals(right.schema)
try:
    pa.concat_tables([left, right])
except pa.ArrowInvalid:
    print("Same column name with incompatible types rejected")
else:
    raise AssertionError("Expected a schema mismatch")
print("Observed total:", pc.sum(money).as_py(), "valid count:", valid_count)
print("Observed mean:", observed_mean, "zero-filled mean:", zero_filled_mean)
print("String identifiers retain their distinction:", identifiers.to_pylist())
```

## Primary references

- [Arrow type definitions](https://arrow.apache.org/docs/python/data.html)
- [Arrow decimal128 API](https://arrow.apache.org/docs/python/generated/pyarrow.decimal128.html)
