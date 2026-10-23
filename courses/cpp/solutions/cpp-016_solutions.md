# cpp-016: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

Move semantics lets a value transfer expensive internal resources. An rvalue reference marks a candidate for transfer, while std::move is a cast that permits a move overload. The rule of zero means letting standard members manage their own copy, move and destruction behavior. A moved-from vector remains valid but its contents are unspecified.

## Worked example 1

```cpp
Batch a{{1,2},"A"}; Batch b=a; b.values[0]=9;
```

Expected: a remains [1,2]; b becomes [9,2].

## Worked example 2

```cpp
Batch b=std::move(a); a=Batch{{4},"new"};
```

Expected: b receives the old values; assigning a new valid value to a is safe.

## Exercise 1: Contrast copy and move

Copy a Batch and mutate the copy.

**Expected:** Original values unchanged.

**Reasoning:** The vector member owns its own copied storage.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Inspect the receiver

Move Batch([1,2,3]) into a new owner.

**Expected:** Receiver values exactly [1,2,3].

**Reasoning:** The target has a specified transferred value.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Reuse the source

Assign Batch([4]) to the moved-from source.

**Expected:** Source is safely usable with value [4].

**Reasoning:** Valid but unspecified permits reassignment.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair an invalid assumption

Remove a test requiring every moved-from vector to be empty.

**Expected:** Test verifies receiver and source validity only.

**Reasoning:** An implementation observation is not a portable postcondition.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Keep rule of zero

List special members needed for Batch.

**Expected:** No custom destructor/copy/move needed.

**Reasoning:** Standard fields already express ownership.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer to return values

Return Batch from a factory and store it.

**Expected:** Correct owned vector after factory scope ends.

**Reasoning:** Return by value allows elision or moves without a dangling reference.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
