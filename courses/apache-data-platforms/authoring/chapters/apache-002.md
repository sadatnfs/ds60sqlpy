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
