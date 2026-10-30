# cpp-016: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

Move semantics lets a value transfer expensive internal resources. An rvalue reference marks a candidate for transfer, while std::move is a cast that permits a move overload. The rule of zero means letting standard members manage their own copy, move and destruction behavior. A moved-from vector remains valid but its contents are unspecified.

## Detailed reasoning

std::move changes which overloads may be selected; it does not move bytes by itself. The type's move constructor performs the transfer. Standard library members let Batch use compiler-generated special members, so ownership behavior composes without custom cleanup code. After the transfer the receiver has the old value; the source remains an object that can be assigned a new value. Testing one implementation's empty moved-from vector would overstate the portable contract.

<!-- depth:start -->
## Copy, move and the state left behind

Copying a value preserves the source and creates another value with the type's copy semantics. Moving allows a destination to take resources from a source that will no longer be used in the same way. std::move itself is a cast that makes a move-capable overload eligible; it does not perform resource transfer on its own. The selected constructor or assignment operator determines what actually happens.

Batch contains vector and string members, so generated operations compose those members' semantics. Copying a Batch copies its vector elements and label. Mutating the copied vector does not change the original. Moving a Batch can transfer member resources efficiently, but the source remains a valid object whose exact values should not be assumed unless its type contract specifies them. In particular, do not assert that every moved-from vector or string must be empty.

The second program checks the destination values and then assigns a fresh Batch to the moved-from source. This tests a useful guaranteed operation: reusing a valid object through assignment. Reading an unspecified old label and treating it as a meaningful business value would be a different, unjustified assumption. Valid means permitted operations remain possible under their preconditions, not that all previous content survives.

The rule of zero favors types composed of well-behaved owning members so that manually written copy/move/destruction logic is unnecessary. Once a class owns a raw resource directly, those special operations must be designed together to avoid shallow copies, double release or lost ownership. A custom destructor can also affect implicit move generation, so adding one is not always a harmless logging change.

Performance claims need observation. Moving a tiny value can be no cheaper than copying, and library exception guarantees may influence whether a container copies or moves elements during reallocation. Correctness should follow the type contract first. A benchmark can then measure the actual workload and implementation rather than assuming every occurrence of std::move made the program faster.

## Debugging the contract

If changing a copy changes the original, inspect whether the member is truly owning or merely a pointer/view. If a moved-from value is used for business logic, replace the assumption with a documented post-move operation or explicit reassignment. If a class becomes unexpectedly non-movable after adding a destructor, review the generated special-member rules. Do not add std::move indiscriminately to return statements or const objects without understanding overload selection.
<!-- depth:end -->

## Worked example 1

```cpp
Batch a{{1, 2}, "A"};
Batch b = a;
b.values[0] = 9;
```

Expected: a remains [1, 2]; b becomes [9, 2].

## Worked example 2

```cpp
Batch b = std::move(a);
a = Batch{{4}, "new"};
```

Expected: b receives the old values; assigning a new valid value to a is safe.

## Exercise 1: Contrast copy and move

Copy a Batch and mutate the copy.

**Expected:** Original values unchanged.

**Reasoning:** The vector member owns its own copied storage.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Inspect the receiver

Move Batch([1, 2, 3]) into a new owner.

**Expected:** Receiver values exactly [1, 2, 3].

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
