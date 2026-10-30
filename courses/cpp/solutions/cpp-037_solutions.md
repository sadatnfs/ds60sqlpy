# cpp-037: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

Composing generic interfaces means combining type constraints, ranges and ownership rules without hiding lifetime requirements. A range parameter can be traversable without being reusable. A returned owning vector is safer for long-lived results than a view over an unknown temporary. Concepts express admissible operations; prose still defines semantics.

## Detailed reasoning

A generic input_range may provide only one traversal. Counting it first can consume an iterator source, leaving no elements for the real operation. The implementation therefore filters and appends in one pass. An owning vector return makes temporary input safe and avoids a borrowed view escaping its owner. Type constraints should describe the weakest capability actually needed, while the written contract explains ordering, multiplicity and lifetime.

<!-- depth:start -->
## Generic pipelines must respect traversal and ownership

An input range may support only one pass. Reading an element can advance a stream-like source irreversibly. An implementation that first counts elements and then loops again to transform them can consume the source during its preliminary scan. A vector permits repeated traversal, but testing only vectors can hide that stronger accidental requirement.

keep_positive accepts an input_range and performs one pass. For each observed value, it appends only values greater than zero to an owning output vector. The input [-1, 0, 2, 2] produces [2, 2]. Multiplicity and order are preserved among retained elements. Zero is intentionally excluded here, unlike the earlier nonnegative examples; the predicate is part of the named contract.

The owning return value is important when the caller passes a temporary vector. The function reads the input while it is alive and returns independent storage. Returning a filtered view into that temporary would require a different lifetime argument and could dangle under an unsafe design. Generic code still needs concrete ownership reasoning.

The range concept expresses traversal capability, but this small function also assumes elements can be used in the integer comparison and appended as int without violating the intended value domain. A fully general library should either constrain those operations more precisely or document the supported element type/range. Calling something generic does not mean every possible range element type is semantically appropriate.

Materialization costs memory proportional to retained values. A production pipeline with unbounded input needs an admission or output-size budget. A lazy view can avoid storing all results, but shifts lifetime and traversal obligations to the consumer. Choose that tradeoff deliberately. The complete programs establish small finite behavior and safe owning results, not an unbounded streaming system.

## Debugging the contract

If a stream-like input produces no output after a counting pass, inspect whether it was consumed twice. If a returned result dangles, look for a view borrowing temporary storage. If zero unexpectedly survives, compare >0 with >=0 rather than changing the fixture. If generic inputs narrow large values into int, fix the element-type/range contract instead of relying on a permissive conversion.
<!-- depth:end -->

## Worked example 1

```cpp
auto out = keep_positive(std::vector<int>{-1, 0, 2, 2});
```

Expected: The owned result is [2, 2], retaining multiplicity after the temporary input dies.

## Worked example 2

```cpp
assert(keep_positive(std::vector<int>{}).empty());
```

Expected: An empty range produces an empty owned result.

## Exercise 1: State range requirements

Explain why one pass is sufficient for keep_positive.

**Expected:** Input-range traversal only, no size prepass.

**Reasoning:** A single-pass source cannot promise a second traversal.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Preserve multiplicity

Filter [-1, 0, 2, 2] with >0.

**Expected:** [2, 2].

**Reasoning:** Generic code still needs explicit bag semantics.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Retain ownership

Call with a temporary vector and use result afterward.

**Expected:** Result remains valid and owns its elements.

**Reasoning:** An owning return separates result lifetime from input lifetime.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair two-pass design

Review counting an input_range then traversing it again.

**Expected:** Use one pass or require forward_range with justification.

**Reasoning:** Constraints must match actual operations.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Check empty input

Use an empty vector and an empty span.

**Expected:** Both yield empty vectors.

**Reasoning:** Different range types share the same semantic boundary.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer a projection

Filter records by their points while retaining complete records.

**Expected:** Output retains IDs, values and duplicate qualifying rows.

**Reasoning:** A projection should not accidentally erase domain identity.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
