# cpp-040: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

Hardening means enforcing explicit bounds before processing untrusted-shaped input. Path validation distinguishes a user-supplied identifier from a filesystem path. Resource limits cap input length, row count and execution work. A parser may be memory-safe yet still accept dangerous locations or consume unreasonable resources.

## Detailed reasoning

The allowed identifier grammar avoids interpreting input as a path at all. batch_7 is a name; ../secret and a/b contain characters that cannot enter this narrow namespace. This does not solve the general problem of safe filesystem containment with symlinks and races. Keep that limitation explicit. Row and byte limits bound work before parsing, and publication should occur only after the accepted/rejected accounting meets the declared policy.

## Worked example 1

```cpp
assert(safe_id("batch_7"));
```

Expected: The seven-character identifier uses only the allowed alphabet.

## Worked example 2

```cpp
assert(!safe_id("../secret"));
```

Expected: Dot and slash violate the narrow identifier grammar.

## Exercise 1: Write the grammar

Specify accepted identifier characters and length.

**Expected:** 1 to 16 lowercase ASCII letters, digits or underscore.

**Reasoning:** A narrow contract is easier to inspect than arbitrary path sanitization.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Test normal input

Validate batch_7 and 0.

**Expected:** Both accepted.

**Reasoning:** An identifier may be numeric without becoming a path.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Reject traversal shapes

Test ../secret, a/b and a backslash-separated path.

**Expected:** All rejected before filesystem access.

**Reasoning:** Separators are outside the grammar.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair overclaim

Explain why this is not a general symlink-safe path sandbox.

**Expected:** No claim of arbitrary path containment; scope remains identifiers.

**Reasoning:** Filesystem races and links require stronger host operations.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Enforce size

Test empty, 16-character and 17-character strings.

**Expected:** Reject, accept, reject.

**Reasoning:** Length is checked before per-character work.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer row budgets

Set max 100 rows and 256 bytes per row before parsing a file.

**Expected:** Oversized input rejected with counts and no partial publication.

**Reasoning:** Input limits and output publication must form one contract.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
