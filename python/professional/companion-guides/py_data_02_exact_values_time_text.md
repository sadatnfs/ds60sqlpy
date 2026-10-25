# Exact Values, Unicode Identity, and Calendar Boundaries

**Stable ID:** `python-data-02`

**Estimated time:** 240 minutes, split across sessions as needed.

## Level and prerequisites

Advanced. Direct catalog prerequisites: `python-21`, `python-29`.

You have worked with time-series data and explicit schemas. This module steps beneath a DataFrame to examine three boundary failures: approximate money, text that looks identical but has different code points, and timestamps that refer to different local calendars. No external data or timezone download is needed.

## Learning objectives

- Parse a bounded exact monetary representation without silent rounding.
- Distinguish Unicode normalization from identity and collision policy.
- Require offset-aware timestamps and compare them as UTC instants.
- Use half-open windows and independent integer-cent reconciliation.

## How to run this lesson

**Primary browser route:** run `./classroom` from the repository root and
choose **Python** on `/classroom`. Open this lesson in the shared workspace,
read its capability notice, and use its supported coding or reading workflow.
The [classroom guide](../../../docs/classroom-experience.md) explains saved work, runtimes and switching subjects.

**Optional contributor route:** use the prepared environment in
[CONTRIBUTING](../../../CONTRIBUTING.md) on Linux, macOS or Windows through
WSL 2. The commands below assume its packages are already installed. They are
not prerequisites for opening this lesson in the Docker classroom. Local
`.learning/` files and CLI progress belong to this checkout; they do not read or
update the Docker classroom's named learning volume.

Use the repository folder in VS Code. The rendered lesson page is a preview;
edit the actual [learner script](../lessons/py_data_02_exact_values_time_text.py). Copy it to an ignored
folder under `.learning/` first if you want to keep your attempt across course
updates. Use the interpreter from setup. These examples need only Python's
standard library, have no network calls, and use the same inputs on each run.

Prepared POSIX/WSL contributor terminal:

```sh
uv run --no-sync python python/professional/lessons/py_data_02_exact_values_time_text.py
```

The terminal shows a small worked example and the remaining TODO count.
TODOs are the starting exercise state. Write predictions before changing
code. Run after one change, save the observed value or exception, and compare
with the exercise's acceptance check. A successful example does not mean the
unfinished exercises are complete. Keep the separate
[explanatory solutions](../solutions/py_data_02_exact_values_time_text_solutions.md) and
[runnable solution](../solutions/py_data_02_exact_values_time_text_solution.py) closed until you have an
attempt and evidence, or deliberately ask for a worked comparison.

## Vocabulary and concepts

A schema can say decimal, string, and timestamp while still leaving critical
meaning undecided. What rounding is allowed? Do two visually identical labels
denote one identity? Which side owns an event exactly at midnight? These are
boundary policies, not formatting preferences. Think of the boundary as a
translator that must declare which representations it accepts and how it
preserves meaning. Reject ambiguity before calculating a polished result.

- **Binary floating point:** an approximate representation of many decimal
  fractions, useful for scientific calculations but not exact currency units.
- **Decimal:** a base-ten number representation; constructing it from text
  preserves the supplied decimal digits instead of a prior float approximation.
- **Quantization:** mapping a number to a fixed decimal exponent, potentially
  requiring rounding if the input has finer precision.
- **Unicode normalization:** conversion of equivalent character sequences to
  a chosen canonical representation, such as NFC.
- **Case folding:** a language-independent Unicode operation for caseless
  matching; it can merge labels that a domain considers distinct.
- **Aware datetime:** a datetime with a usable offset from UTC; it identifies
  an instant rather than only a wall-clock reading.
- **Half-open interval:** a window that includes its start and excludes its
  end, written `[start, end)`.

The money parser accepts stripped ASCII decimal text with one to twelve
integer digits and zero, one, or two fractional digits. Amounts are
nonnegative, have no exponent notation, and represent one declared currency.
It rejects excess precision instead of rounding it. A real multicurrency
system must also carry currency identity; adding two amounts with different
currencies is outside this lab's contract. Use integer cents to reconcile a
batch, avoiding dependence on a caller's Decimal precision context.

For labels, NFC addresses canonical character equivalence. Casefold is a
separate, explicit caseless-matching choice. Neither is a complete identity
solution: normalization can reveal collisions that need review. Keep every
raw spelling in the collision report. Do not claim that this eliminates
homoglyphs, resolves languages, or makes untrusted paths safe.

## Worked example / walkthrough

### Example A: preserve source decimal meaning

```python
from decimal import Decimal

assert Decimal("0.10") + Decimal("0.20") == Decimal("0.30")
assert Decimal(0.1) != Decimal("0.1")
assert int(Decimal("12.34") * 100) == 1234
```

`Decimal("0.10")` reads text directly. `Decimal(0.1)` instead captures the
existing binary float value, including its approximation. The integer-cent
conversion is safe here because the contract already limits precision to
cents. Truncating arbitrary Decimal input first would hide an invalid third
fractional digit. Expected observation: all three assertions pass, and the
last amount has exactly 1234 cents.

### Example B: compare instants, then decide window ownership

```python
from datetime import datetime, timezone

local = datetime.fromisoformat("2026-01-02T00:30:00+02:00")
utc = local.astimezone(timezone.utc)
start = datetime.fromisoformat("2026-01-01T22:00:00+00:00")
end = datetime.fromisoformat("2026-01-01T23:00:00+00:00")
assert utc.isoformat() == "2026-01-01T22:30:00+00:00"
assert start <= utc < end
assert not (start <= end < end)
```

`fromisoformat` parses a supplied offset; `astimezone` changes representation
while preserving the instant. It does not relabel the wall clock. Expected
observation: a local January 2 event belongs to the UTC January 1 window. The
final assertion excludes the exact end, so adjacent windows cannot both own
that instant. Replacing timezone information with `replace(tzinfo=...)` would
assign a meaning rather than convert an already-known instant.

### Wall-clock ambiguity needs more information

A timestamp without an offset cannot tell this lab which instant occurred.
Reject it instead of assuming the executing machine's timezone. A named zone
also has historical and seasonal rules; a fixed offset does not teach those
rules or resolve repeated daylight-saving clock times. This offline lab uses
explicit offsets so Windows, macOS, and Linux agree without an external zone
database. In real zoned data, preserve the zone, disambiguation policy, and
timezone-data version when they matter to reproduction.

Validate every source record before filtering its window. An invalid record
outside the desired window still violates the input contract and must be
reported instead of hidden by filtering. The reference raises ValueError for
such a record. A quarantine pipeline could retain it separately, but would
need count and rejected-value accounting of its own.

## Exercises

1. **Parse exact cents.** Implement `parse_money`. Accept `" 12.3 "` as Decimal 12.30 and zero as Decimal 0.00. Preserve the two-decimal exponent.

   **Verify:** The accepted values have exponent -2 and integer-cent values 1230 and 0; `"0.10"` plus `"0.20"` totals exactly 0.30.

   **Hint:** Validate the text shape before quantizing so quantization cannot silently repair precision.

2. **Reject ambiguous numeric forms.** Probe `"1.005"`, `"NaN"`, `"Infinity"`, `"1e2"`, `"-1"`, an empty string, a float, and a thirteen-digit integer string.

   **Verify:** Every probe raises ValueError. A two-digit fractional amount `"1.00"` still succeeds, showing the check is not blanket rejection.

   **Hint:** A bounded lexical rule can rule out both unexpected notation and unreasonable digit counts.

3. **Expose Unicode collisions.** Implement `canonical_label` using trim, NFC, casefold, then NFC. Implement collision_groups that retains distinct raw spellings for shared canonical values.

   **Verify:** Assert equal canonical values for `"Café"` and `"Cafe\u0301"`; collision output maps `strasse` to two raw spellings. Identical repeated raw text produces an empty collision mapping.

   **Hint:** Keep raw spellings even when their normalized comparison keys agree.

4. **Parse and convert an instant.** Implement `parse_instant` to require an aware parsed timestamp and return UTC. Compare `2026-01-02T00:30:00+02:00` with its UTC equivalent.

   **Verify:** Both representations produce equal datetimes at 2026-01-01 22:30 UTC; a timestamp without any offset raises ValueError.

   **Hint:** Check utcoffset before converting; do not assume the local machine timezone.

5. **Own an exact boundary once.** Implement a window membership function that requires aware ordered bounds. Test start, one middle instant, end, and an empty or reversed window.

   **Verify:** Membership assertions return True for start/middle and False for end; tests capture ValueError for nonpositive windows. Adjacent-window boundary membership sums to exactly 1.

   **Hint:** Use a single declared [start, end) policy across every comparison.

6. **Reconcile a window total.** Implement `window_total` over records with amount and occurred_at text. Include two in-window values 0.10 and 0.20 and an exact-end value 9.00.

   **Verify:** The result is count 2 and Decimal total 0.30; an independent integer sum gives 30 cents. The 9.00 record is excluded.

   **Hint:** Perform exact cents accounting after validation, then convert the integer sum back to Decimal.

7. **Prevent filter-hidden invalid data.** Add an out-of-window record with amount `"bad"`. Explain whether filtering is permitted to conceal the malformed source value.

   **Verify:** A test captures ValueError for the bad amount and confirms that no total is returned, even with the malformed record outside the selected window.

   **Hint:** Boundary ordering is observable behavior; test it explicitly.

8. **Transfer to local-day reporting.** Write a policy note for a source that asks for a city-local business day instead of a UTC day. State what additional metadata and tests are needed without inventing a zone conversion.

   **Verify:** The note requires a named zone and rules/version, tests a seasonal offset change and ambiguous local time, and distinguishes a local day from a fixed 24-hour UTC window.

   **Hint:** The present fixed-offset examples do not establish daylight-saving behavior.

## Self-check

Explain why constructing Decimal from an existing float does not recover
the original decimal intent. Give a normalization collision that should be
reviewed rather than merged silently. Describe the exact instant owned by the
second of two adjacent windows. Explain what evidence a UTC-only lab cannot
provide about a city-local daylight-saving boundary.

## Common pitfalls

If a cent total drifts, inspect where floats entered the pipeline. If a label
unexpectedly merges, compare raw code points, NFC output, and casefold output
as separate stages. If a timestamp shifts by hours, compare conversion with
timezone replacement. If a record appears twice across windows, inspect the
two endpoint comparisons. If an invalid amount disappears, check whether
filtering happened before the validation boundary.

## Next step

Use these explicit instants in leakage-resistant evaluation. Bring the same
currency, identity, and time policies to dataframe and SQL boundaries rather
than assuming a library default matches your intended meaning.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for python-data-02.
Read python/professional/companion-guides/py_data_02_exact_values_time_text.md and python/professional/lessons/py_data_02_exact_values_time_text.py.
Check my direct prerequisites: python-21, python-29.
Keep solutions/ closed unless I request comparison after an attempt.
Explain the mental model, ask me to predict one result, let me attempt it,
give one hint at a time, inspect my evidence, and ask a retrieval question.
Done when I can independently reproduce the numbered acceptance checks,
explain a failure case, and transfer the policy to a changed input.
```
