# cpp-028: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A reusable record library separates stable data contracts from user-interface code. Packaging declares headers and link targets. Compatibility tests protect callers from accidental changes. The capstone combines strict parsing, named errors, ownership and exact integer output with an auditable fixture ledger.

## Detailed reasoning

Keep the library core independent of terminal and filesystem effects so the record grammar can be tested directly. Each successful Record owns integer values, so it can outlive the string_view used during parsing. The four-row corpus distinguishes valid zero values from malformed suffixes and negative amounts. Package acceptance is a separate host boundary: compile a consumer against the public header and link the library target, then preserve the exact commands and statuses.

<!-- depth:start -->
## Designing and consuming a reusable parser library

A reusable library separates its public contract from implementation and from the application's I/O policy. The record parser accepts one string_view and returns an owning Record or rejection. The caller decides where raw text came from and whether a rejected row aborts a batch. This separation lets the parser be tested without a terminal, file or cluster and keeps its lifetime reasoning small.

The public Record owns integer id and cents values. It does not retain a view into the input, so a successful result survives after the caller's raw string is destroyed. The parser still borrows the input while reading it. A library that returned views into a temporary normalization buffer would violate that lifetime contract even if its ordinary example happened to print correct values.

The grammar is exactly two comma-separated nonnegative integer fields. The parser checks delimiter count, both conversion results, full consumption and domain ranges. The suffix fixture 7, 125x rejects a plausible permissive parser that accepts a numeric prefix. Valid0, 0 prevents the opposite bug of treating zero as absence. These cases are independent of packaging and should pass before the library is exported.

The real record-library fixture contains a public header, implementation, independent consumer and CMake target. Building the consumer against that target tests whether the header declares everything it needs and whether the implementation is actually linked. A combined single-file source cannot expose a missing exported include path or omitted library object in the same way.

Installation/export is another boundary. A local install tree should let a fresh consumer find the documented package/target without relying on the original source directory. The host exercise records configure, build, install and consumer results separately. The browser's one-main.cpp run is still useful for parser behavior, but it does not execute that packaging workflow.

A library release also needs a stability policy. Changing the accepted grammar, error representation or ownership behavior can break callers even when the function name stays the same. Document format/version changes and keep an independent consumer test. A package that compiles but silently accepts malformed suffixes is not a successful release under this contract.

## Debugging the contract

If a consumer compiles only inside the library source tree, inspect public includes and exported target properties. If it links without the intended library, check whether a header accidentally contains a duplicate implementation. If parsing passes normal rows but accepts125x, inspect full consumption. If a returned record changes when raw input is edited, look for borrowed fields where the public contract promised owning values.
<!-- depth:end -->

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

Use [7, 125; 0, 0; 7, 125x; 7, -1] as four records.

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

**Expected:** 7, 125x must fail the golden test.

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
