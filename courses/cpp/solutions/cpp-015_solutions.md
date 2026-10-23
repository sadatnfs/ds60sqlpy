# cpp-015: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

RAII means acquiring a resource in an object and releasing it when that object leaves scope. unique_ptr owns one dynamically allocated object and cannot be copied. Its destructor releases the owned object even when an exception unwinds the scope. The owner must not be confused with a borrowed raw pointer.

## Detailed reasoning

At scope entry the unique_ptr becomes responsible for one allocation. Moving it hands that responsibility to another owner; the moved-from pointer no longer releases the object. During exception unwinding the current owner still runs its destructor, which reduces the live count. Count resources at scope boundaries rather than depending on an informal promise to call delete later. Resource lifetime and the lifetime of a borrowed pointer must be drawn separately.

## Worked example 1

```cpp
auto p=std::make_unique<int>(7); auto q=std::move(p);
```

Expected: p is empty, q owns the integer 7.

## Worked example 2

```cpp
{ auto p=std::make_unique<Tracked>(live); }
```

Expected: live rises to 1 in scope and returns to 0 at destruction.

## Exercise 1: Trace ownership

Draw p and q before and after moving unique_ptr<int>(7).

**Expected:** One live allocation; exactly one owner at each point.

**Reasoning:** Moving transfers the pointer ownership.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Check normal cleanup

Run the Tracked scoped case.

**Expected:** live=1 inside and 0 afterward.

**Reasoning:** Destructor cleanup is tied to scope.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Check exceptional cleanup

Throw after constructing Tracked and catch outside.

**Expected:** live=0 after catch.

**Reasoning:** Stack unwinding destroys the owner.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Reject accidental copy

Try auto q=p with unique_ptr.

**Expected:** Compile failure; move only when ownership should change.

**Reasoning:** unique_ptr disables copying by design.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Handle empty owner

Default-construct unique_ptr<int> and inspect Boolean state.

**Expected:** false, with no dereference.

**Reasoning:** An empty owner has nothing to destroy.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer to a collection

Own three unique_ptr<int> values in a vector then leave scope.

**Expected:** All three allocations released; no manual delete loop.

**Reasoning:** Composed RAII owners clean up recursively.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
