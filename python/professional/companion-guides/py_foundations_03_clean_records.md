# Turn Messy Text into Trustworthy Records

**Stable ID:** `python-foundations-03`

**Estimated time:** 180 minutes, split across sessions as needed.

## Level and prerequisites

Foundation. Direct catalog prerequisites: `python-08`.

You have used functions, lists, dictionaries, exceptions, and CSV from Days 1 to 8. No pandas is needed. This module makes cleaning policies visible before a table library can hide the individual records.

## Learning objectives

- Declare accepted input representations and reject ambiguous ones.
- Preserve source rows and record specific rejection reasons.
- Handle zero, missing text, invalid integers, and duplicate identities differently.
- Reconcile input counts with accepted and rejected output.

## How to run this lesson

**Primary browser route:** run `./classroom` from the repository root and
choose **Python** on `/classroom`. Open this lesson in the shared workspace,
read its capability notice, and use its supported coding or reading workflow.
The [classroom guide](../../../docs/classroom-experience.md) explains saved work, runtimes and switching subjects.

**Optional native notebook/editor route:** the instructions below describe
separately prepared host tools. They are useful alternatives, not prerequisites
for opening this lesson in the Docker classroom.

Use the repository folder in VS Code. The rendered lesson page is a preview;
edit the actual [learner script](../lessons/py_foundations_03_clean_records.py). Copy it to an ignored
folder under `.learning/` first if you want to keep your attempt across course
updates. Use the interpreter from setup. These examples need only Python's
standard library, have no network calls, and use the same inputs on each run.

Windows PowerShell:

```powershell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython python\professional\lessons\py_foundations_03_clean_records.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_foundations_03_clean_records.py
```

The terminal shows a small worked example and the remaining TODO count.
TODOs are the starting exercise state. Write predictions before changing
code. Run after one change, save the observed value or exception, and compare
with the exercise's acceptance check. A successful example does not mean the
unfinished exercises are complete. Keep the separate
[explanatory solutions](../solutions/py_foundations_03_clean_records_solutions.md) and
[runnable solution](../solutions/py_foundations_03_clean_records_solution.py) closed until you have an
attempt and evidence, or deliberately ask for a worked comparison.

## Vocabulary and concepts

A CSV reader gives you text, even when a column is supposed to represent a
quantity. Cleaning is the translation from raw representation to a declared
meaning. It should be possible to explain what changed and what was rejected.
Imagine a receiving desk: every incoming parcel gets either an acceptance
receipt or a reason for rejection. A parcel must never disappear simply
because it looked inconvenient.

- **Raw record:** the original field values before any cleaning decision.
- **Normalization:** a permitted representation change, such as trimming
  spaces around an identifier.
- **Validation:** checking whether a value satisfies a declared rule.
- **Identity:** the field used to decide whether two records describe the
  same entity or event. Here it is a case-sensitive trimmed `id` string.
- **Rejection:** a record retained separately with a specific failed rule.
- **Reconciliation:** an independent accounting check across pipeline stages.

Our input contract is a dictionary containing string fields `id` and
`quantity`. Identifiers must remain nonempty after stripping outer whitespace.
Quantities may contain outer whitespace and an optional leading plus sign,
but must parse as integers greater than or equal to zero. Decimal text,
missing fields, non-string fields, and negative values are rejected. This is
a bounded teaching policy; other domains may legitimately allow negatives.
The first valid record for an identifier wins. Invalid earlier rows do not
reserve that identifier, because they never became accepted records.

Zero means a known count of none. Empty text means no usable representation
was supplied. Invalid text such as `many` is a third state. Mapping all three
to zero makes an aggregate look complete while losing the reason for missing
information. Preserve those distinctions in both returned data and tests.

## Worked example / walkthrough

### Example A: parse only the boundary that can fail

```python
def parse_quantity(raw):
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("quantity is missing or not text")
    try:
        quantity = int(raw.strip())
    except ValueError as exc:
        raise ValueError("quantity is not an integer") from exc
    if quantity < 0:
        raise ValueError("quantity is negative")
    return quantity


assert parse_quantity(" 0 ") == 0
assert parse_quantity("+4") == 4
```

`raw` is the function parameter. `isinstance` checks the representation
before calling a string method. The narrow try block wraps only conversion;
`raise ... from exc` keeps the original cause for diagnosis. Returning zero
is correct for the text zero, but not a fallback for a failed conversion.
Expected observation: both assertions pass; `parse_quantity("4.5")` raises
ValueError instead of quietly rounding.

### Example B: copy before changing representation

```python
raw = {"id": " A-1 ", "quantity": "2"}
cleaned = {"id": raw["id"].strip(), "quantity": int(raw["quantity"])}
assert raw["id"] == " A-1 "
assert cleaned == {"id": "A-1", "quantity": 2}
print(raw, cleaned)
```

Expected observation: the raw dictionary retains its spaces while cleaned
contains a normalized identifier and integer. Creating a new dictionary
preserves original evidence. Assigning `cleaned = raw` would make both names
refer to the same mutable dictionary; a later edit would change your evidence.
This differs from the immutable integer reassignment in the first on-ramp.

### Make rejection actionable

Use a one-based source row number and a stable reason such as `duplicate id`
or `quantity is negative`. A row number is a location in this input, not a
permanent identity across reordered files. Preserve a shallow copy of the raw
dictionary here because the input values are simple strings. If nested lists
were allowed, shallow copying would not isolate changes inside those lists.
Document the actual data shape instead of promising universal deep copying.

Only add an identifier to `seen` after all validation succeeds. That order
makes first-valid-wins precise and avoids rejecting a good replacement for an
invalid earlier row. Keep accepted rows in source order. Rejection order also
follows source order, which makes a report easier to compare with its input.
The count check `input_count == accepted_count + rejected_count` catches lost
rows, but cannot prove each accepted quantity is correct. Add value checks and
input-unchanged checks as separate evidence.

## Exercises

1. **Define the policy before coding.** Write a five-row policy table for `"0"`, `""`, `" 4 "`, `"4.5"`, and `"-1"`. For each, state accepted integer or rejection reason. Implement `parse_quantity`.

   **Verify:** Accepted results are 0 and 4. The other three inputs raise ValueError, with missing, non-integer, and negative reasons respectively.

   **Hint:** Do not use a broad exception handler as a substitute for a representation check.

2. **Keep raw records unchanged.** Implement `normalize_record` for string id and quantity fields. Given `{"id": " A ", "quantity": "2"}`, return canonical fields without mutating the input.

   **Verify:** The result equals `{"id": "A", "quantity": 2}` while the original id still contains both surrounding spaces.

   **Hint:** Construct a new dictionary rather than reusing the original object.

3. **Make missing identity visible.** Test an absent id, an empty id, and an all-space id. Decide whether `"A"` and `"a"` collide under the declared case-sensitive policy.

   **Verify:** Tests capture ValueError for each missing identity and assert that normalized ids `A` and `a` remain unequal strings.

   **Hint:** Normalization and identity comparison are separate policy choices.

4. **Account for every row.** Implement `clean_rows` returning accepted and rejected lists. Feed ids A, B, C with quantities 2, many, and 0.

   **Verify:** Three inputs produce two accepted records with total quantity 2 and one rejection at one-based row 2; count reconciliation equals 3.

   **Hint:** Catch only the validation failure and preserve its row with the reason.

5. **Enforce first valid wins.** Feed A/many, A/2, and A/3 in that order. Add duplicate detection after validation and preserve rejection evidence.

   **Verify:** Only A/2 is accepted; rows 1 and 3 are rejected for non-integer quantity and duplicate id. The first invalid row does not reserve A.

   **Hint:** Update the set of seen identifiers only at the acceptance step.

6. **Reject wrong field types.** Test `{"id": "A", "quantity": None}` and `{"id": 3, "quantity": "2"}`. Avoid converting arbitrary objects with `str`.

   **Verify:** Both records appear in rejected output with ValueError-derived reasons, and neither becomes an accepted zero or identifier `"3"`.

   **Hint:** The contract accepts text fields, not every object that can be displayed.

7. **Check empty and all-invalid batches.** Run `clean_rows` with no rows, then with two invalid quantity rows. Summarize accepted quantities with an explicit zero start.

   **Verify:** The empty batch returns two empty lists and total 0. The invalid batch has accepted count 0, rejected count 2, and total 0.

   **Hint:** An empty total does not mean that the input was complete or valid.

8. **Transfer to stock adjustments.** Describe a second contract where negative counts represent returns. Keep the original parser unchanged and write boundary cases for a separate signed parser.

   **Verify:** Your policy note records signed-parser output -1, the original parser's ValueError for the same text, and rejection tests for empty and decimal text in both contracts.

   **Hint:** A domain change should be named and tested rather than silently broadening shared validation.

## Self-check

Explain why zero differs from missing and invalid input. Reconstruct the
first-valid-wins sequence using a new identifier. Show why count reconciliation
alone cannot detect accidentally changing quantity two into twenty. Give a
second assertion that would catch that defect without opening the solution.

## Common pitfalls

If raw evidence changes after cleaning, compare object identities and inspect
assignments that reuse dictionaries. If a valid replacement is called a
duplicate, locate the point where `seen` is updated. If counts reconcile but
totals are wrong, inspect accepted integer values and compare with a manual
small-case calculation. If `None` causes AttributeError, validate the field
type before calling `.strip()`. Do not catch that programming mistake globally.

## Next step

Use these boundaries in the first independent data investigation, then carry
the same reasoning into pandas cleaning and schema validation. A library may
make conversion faster; it cannot choose your missing-value or identity policy.

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning for python-foundations-03.
Read python/professional/companion-guides/py_foundations_03_clean_records.md and python/professional/lessons/py_foundations_03_clean_records.py.
Check my direct prerequisites: python-08.
Keep solutions/ closed unless I request comparison after an attempt.
Explain the mental model, ask me to predict one result, let me attempt it,
give one hint at a time, inspect my evidence, and ask a retrieval question.
Done when I can independently reproduce the numbered acceptance checks,
explain a failure case, and transfer the policy to a changed input.
```
