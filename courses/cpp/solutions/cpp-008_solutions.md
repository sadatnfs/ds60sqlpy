# cpp-008: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A value copy has its own state. A reference is another name for an existing object and does not own its lifetime. `const` blocks mutation through that access path. A const reference can avoid copying a large vector, but it does not keep the vector alive after its owner is destroyed.

## Worked example 1

```cpp
auto out=doubled(std::vector<int>{2,4});
```

Expected: An owned result [4,8] survives the temporary argument.

## Worked example 2

```cpp
const std::vector<int> xs{2,4}; auto ys=xs; ys[0]=99;
```

Expected: xs stays [2,4]; ys becomes [99,4].

## Exercise 1: Draw owners

Draw input, copied output and borrowed parameter.

**Expected:** Two owners and one temporary borrow, no extra owner for the reference.

**Reasoning:** References alias; vectors own storage.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Predict mutation

Change output[0] to 99 after doubled([2,4]).

**Expected:** Input first value 2; output first value 99.

**Reasoning:** The result owns independent elements.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Write a const observer

Write size_of(const vector<int>&) without mutation.

**Expected:** [2,4] gives 2; empty gives 0.

**Reasoning:** A read-only observer does not need a value copy.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Diagnose const assignment

Attempt xs[0]=9 through const vector<int>& in a scratch file.

**Expected:** Compilation fails; remove mutation to repair.

**Reasoning:** The const access path forbids writing an element.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Identify a lifetime bug

Review a function returning const vector<int>& to its local result.

**Expected:** Reject the reference return; return vector<int> by value.

**Reasoning:** The local owner dies at return, regardless of const.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer a safe result

Call doubled with temporary [5] and retain the result.

**Expected:** Stored result remains [10] after the full expression.

**Reasoning:** Owning the returned value extends the useful lifetime safely.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
