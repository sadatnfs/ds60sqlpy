# cpp-006: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A string owns characters; string_view temporarily observes them. `from_chars` parses without locale-dependent whitespace skipping. Its error code reports invalid input or overflow, while its returned pointer identifies the first unconsumed character. Trustworthy input needs both successful conversion and full consumption.

## Worked example 1

```cpp
assert(parse_int("42")==42);
```

Expected: All two characters are consumed, yielding 42.

## Worked example 2

```cpp
assert(!parse_int("12x"));
```

Expected: The x remains, so the field is rejected despite a valid numeric prefix.

## Exercise 1: Trace consumption

Parse 42 and 12x and inspect pointer distance.

**Expected:** 42 consumes 2; 12x consumes 2 of 3 and is rejected.

**Reasoning:** Conversion success alone is insufficient.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Retain zero

Parse 0 and -7 through optional<int>.

**Expected:** Both are present values.

**Reasoning:** A zero value is not an absent optional.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Build a ledger

Classify [12,12x,empty,0] as raw strings.

**Expected:** Two accepted values [12,0], two rejected records.

**Reasoning:** Preserve rejected raw input and reason.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair prefix acceptance

Change the condition to check only ec in a scratch copy.

**Expected:** 12x is incorrectly accepted until ptr==end is restored.

**Reasoning:** Inspect the unconsumed suffix.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Reject overflow

Parse 21 decimal nines.

**Expected:** Absent result with out-of-range conversion, never a wrapped integer.

**Reasoning:** The range error occurs before publishing a trusted value.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Define whitespace policy

Compare literal space-42-space with a deliberately trimmed copy.

**Expected:** Strict parser rejects original; explicit trim accepts 42.

**Reasoning:** Trimming is an input policy that belongs before parsing.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
