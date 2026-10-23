# cpp-028: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A reusable record library separates stable data contracts from user-interface code. Packaging declares headers and link targets. Compatibility tests protect callers from accidental changes. The capstone combines strict parsing, named errors, ownership and exact integer output with an auditable fixture ledger.

## Worked example 1

```cpp
auto r=parse_record("7,125"); assert(r->id==7 && r->cents==125);
```

Expected: The library produces an owned record with exact fields.

## Worked example 2

```cpp
assert(!parse_record("7,125x"));
```

Expected: A trailing suffix rejects the complete record.

## Exercise 1: Write public contracts

Document parse_record input grammar and result ownership.

**Expected:** Two nonnegative integer fields, full consumption, owned success.

**Reasoning:** Consumers need semantic rules beyond signatures.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Build independent fixture

Use [7,125;0,0;7,125x;7,-1] as four records.

**Expected:** Two accepted and two rejected.

**Reasoning:** Expected results are hand-written independently.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Package a consumer

Split header, implementation and CLI into the host project.

**Expected:** Separate library and executable targets build and link.

**Reasoning:** A single-file worker cannot establish packaging.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Inject a regression

Remove the full-consumption check in a scratch implementation.

**Expected:** 7,125x must fail the golden test.

**Reasoning:** A plausible parsing shortcut is the negative control.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Check boundary ownership

Return a parsed record after input string goes out of scope.

**Expected:** Record fields remain valid copied integers.

**Reasoning:** No borrowed string_view survives in the result.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Deliver compatibility evidence

Run a consumer against current public header and library.

**Expected:** Compiler/platform identity, test output and source inventory retained.

**Reasoning:** A reviewer must reproduce the consumer boundary.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
