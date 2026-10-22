# Exact Values, Unicode Identity, and Calendar Boundaries: solution reasoning

Stable ID: `python-data-02`.

Read the [guide](../companion-guides/py_data_02_exact_values_time_text.md) and attempt the [learner artifact](../lessons/py_data_02_exact_values_time_text.py) first. The [executable solution](py_data_02_exact_values_time_text_solution.py) is a comparison implementation. It does not certify your changed program merely because its own demonstration succeeds. Copy the acceptance cases into your attempt, then change one input without changing the intended policy.

The reference makes representation decisions before arithmetic or
selection. A lexical money rule accepts one documented format; a separate
Unicode pipeline preserves raw collisions; timestamp parsing requires an
offset and normalizes the representation to UTC. The functions reject invalid
inputs instead of consulting machine locale or silently rounding.

```python
from decimal import Decimal

assert Decimal("0.10") + Decimal("0.20") == Decimal("0.30")
```

Whole-batch totals use integer cents, so an unrelated caller changing the
Decimal arithmetic context cannot silently round a large sum. The format is
intentionally bounded; this is not a general financial ledger, language-aware
identity service, or named-timezone resolver. Those broader systems require
additional contracts and evidence.

## Exercise 1. Parse exact cents

The money parser checks type before stripping and matches a small ASCII decimal grammar. It then constructs Decimal from text and quantizes to a cent exponent. Because the grammar already rules out a third fractional digit, quantization only standardizes representation; it never decides a rounding policy. A local Decimal context protects the small conversion from a caller's unexpectedly low precision setting. Check both numeric equality and exponent, since Decimal("12.3") equals Decimal("12.30") numerically while representing different displayed precision. The chosen contract requires the cent exponent explicitly.

## Exercise 2. Reject ambiguous numeric forms

NaN and Infinity are valid Decimal spellings but not accepted monetary amounts here. Exponent notation, signs, extra precision, and overlong integer parts also fail the lexical contract. Rejecting those forms early makes the accepted representation inspectable and bounds work on unreasonable input. A float is rejected even if it appears to contain a clean decimal value, because it has already crossed an approximate representation boundary. These decisions are domain policy rather than claims that those representations are invalid for all Python calculations.

## Exercise 3. Expose Unicode collisions

NFC makes canonically equivalent accents comparable. Casefold then supports the explicitly chosen caseless match and can turn the German sharp s into ss. A final NFC normalizes any resulting character sequence again. Collision reporting groups distinct raw spellings under their canonical key and retains insertion order for review. Repeating exactly the same raw spelling twice does not count as a distinct-spelling collision. The report does not prove that the spellings denote the same person, account, or product. A consumer must choose a merge or rejection rule separately.

## Exercise 4. Parse and convert an instant

Parse the source text with datetime.fromisoformat and reject any result whose utcoffset is None. Convert the aware result with astimezone(timezone.utc). The local timestamp at 00:30 with offset plus two hours becomes 22:30 UTC on the previous date, and compares equal to that UTC representation. Replacing tzinfo would incorrectly change the identified instant. The reference accepts explicit offsets; it does not use the machine timezone or a downloaded zone database. Missing-offset input raises a visible ValueError so no implicit assumption enters the result.

## Exercise 5. Own an exact boundary once

Validate the start, end, and candidate datetime as aware values, normalize them to UTC, and require end strictly greater than start. Include a candidate when start is less than or equal to it and it is strictly less than end. The exact endpoint belongs only to the next adjacent interval. Rejecting empty windows instead of returning an empty result makes an accidental swapped or equal bound visible. Comparing aware instants also prevents misleading comparisons between equal wall-clock strings from different offsets. Keep endpoint tests alongside normal mid-window examples.

## Exercise 6. Reconcile a window total

Validate each amount and timestamp, then select by the half-open UTC interval. The two selected amounts contribute ten and twenty integer cents, giving thirty cents and count two. The record at the exact end contributes neither count nor money. Conversion back to a two-decimal Decimal occurs once after integer summation. A separate manually written integer calculation provides an oracle for this tiny case. Count alone would not catch an amount defect, and total alone could miss swapping equal-value records, so preserve both observations.

## Exercise 7. Prevent filter-hidden invalid data

Whole-source validation is a deliberate ordering guarantee. The malformed out-of-window amount fails before the selection can conceal it. This prevents a pipeline from claiming its source boundary passed while merely ignoring inconvenient records. A different system might quarantine invalid records and continue, but it must report rejected rows and limits on completeness. Do not silently change between these policies to make a test pass. The reference raises ValueError for the bad amount and performs no partial publication or report write, so callers see a clear failed boundary.

## Exercise 8. Transfer to local-day reporting

A local business day is defined by a named zone's calendar rules and may not last exactly twenty-four hours during seasonal changes. Require the zone identity, applicable timezone rules or version, and a policy for ambiguous or nonexistent wall-clock times. Test both seasonal transition directions and an event at the local boundary. Fixed-offset examples cannot establish those behaviors. The current lab deliberately uses aware offset timestamps for a portable offline core. A future zoned extension should make its database dependency explicit and preserve the same instant and interval reasoning.

## Compare and transfer

Try the same instant with two offsets and verify that membership is unchanged while printed local dates differ. Then use NFC-only matching in a copy and observe which casefold collisions disappear. Explain why this is a policy change rather than an optimization. Your evidence should name accepted formats, rejected representations, raw collisions, and the exact selected UTC interval.
