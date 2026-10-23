# cpp-037: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

Composing generic interfaces means combining type constraints, ranges and ownership rules without hiding lifetime requirements. A range parameter can be traversable without being reusable. A returned owning vector is safer for long-lived results than a view over an unknown temporary. Concepts express admissible operations; prose still defines semantics.

## Worked example 1

```cpp
auto out=keep_positive(std::vector<int>{-1,0,2,2});
```

Expected: The owned result is [2,2], retaining multiplicity after the temporary input dies.

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

Filter [-1,0,2,2] with >0.

**Expected:** [2,2].

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
