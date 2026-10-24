# cpp-006: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A string owns characters; string_view temporarily observes them. `from_chars` parses without locale-dependent whitespace skipping. Its error code reports invalid input or overflow, while its returned pointer identifies the first unconsumed character. Trustworthy input needs both successful conversion and full consumption.

## Detailed reasoning

For 12x, from_chars can store 12 and report no conversion error, yet its pointer stops at x. The parser therefore treats error-code success as only the first condition. The second condition compares the pointer with end. Empty input has no digits; huge input exceeds int range; whitespace is outside this deliberately strict grammar. Keep these reasons separate in a production ledger so a user can distinguish syntax, range and policy rejection.

<!-- depth:start -->
## Parsing as a trust boundary

Parsing converts a sequence of characters into a value under a grammar. The grammar here is deliberately strict: an optional minus sign followed by decimal digits represent an int, with no surrounding whitespace, plus sign or trailing suffix accepted by this wrapper. The raw string remains evidence until the entire field is accepted. A useful parser does not publish a partially parsed prefix as a trusted record.

from_chars returns two pieces of information. The error code tells whether conversion was possible and within range. The pointer identifies where conversion stopped. For42, the pointer reaches the end. For12x, conversion can succeed for12 while the pointer stops before x. The wrapper requires both success and full consumption. This is why checking only the error code admits a malformed business field.

optional<int> separates absence from a present number. A present zero is valid and must not be confused with rejection. Test the optional itself for presence, then read its value. Testing `*result != 0` as though it meant success changes the input policy and loses legitimate zero records. Dereferencing an absent optional is also outside the intended contract, so branch on presence first.

The string_view parameter borrows characters only for the duration of the call. The returned int owns its value and does not refer back to those characters. That makes a parsed result safe after the input string changes or dies. Returning a view into a temporary normalization buffer would have a very different lifetime problem, even though the parser computation looked correct.

Whitespace normalization is a separate policy. If the data contract allows trimming, perform it explicitly before strict conversion and retain enough raw context to explain rejections. Do not silently switch to a parser that skips spaces or accepts prefixes just to make a failing fixture pass. Overflow is another distinct rejection: twenty-one decimal nines must not wrap into a plausible small int. The error result is safer than performing unchecked arithmetic while building the value.

## Debugging the contract

When a malformed suffix is accepted, print or inspect the consumed-character count and compare it with the field length. When zero disappears, inspect whether value truthiness was confused with optional presence. When a long number fails, preserve the out-of-range reason rather than treating it as empty input. Empty input should be rejected before any value is published; callers should pass a valid character range, not manufacture an invalid pointer pair.
<!-- depth:end -->

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

Classify [12, 12x, empty, 0] as raw strings.

**Expected:** Two accepted values [12, 0], two rejected records.

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
