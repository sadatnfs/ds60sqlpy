# cpp-039: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A C interface exposes stable-shaped calls to clients that may not share a C++ compiler. An opaque handle hides implementation details while preserving a documented owner. A loading boundary introduces version, symbol and cleanup responsibilities. Destroying an object in the wrong allocator or letting an exception cross the boundary can break the contract.

## Worked example 1

```cpp
Analyzer* p=analyzer_create(); int value=0; analyzer_read(p,&value); analyzer_destroy(p);
```

Expected: One successful create has exactly one matching destroy; initial value is 0.

## Worked example 2

```cpp
assert(analyzer_read(nullptr,&out)==1);
```

Expected: Null handle is rejected without dereferencing it.

## Exercise 1: Document ownership

Name who destroys a successfully created handle.

**Expected:** Caller invokes analyzer_destroy exactly once.

**Reasoning:** The provider controls allocation and deallocation pairing.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Wrap safely

Use unique_ptr with analyzer_destroy as deleter.

**Expected:** Scope exit calls the provider destructor once.

**Reasoning:** RAII can manage a C boundary through a custom deleter.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Reject null arguments

Test null handle and null output independently.

**Expected:** Status 1 for either, no pointer dereference.

**Reasoning:** Both borrowed pointers require validation.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair cross-boundary throw

Review a create function that throws bad_alloc across C.

**Expected:** Catch inside and return null or a documented status.

**Reasoning:** The foreign caller may not support C++ unwinding.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Version the interface

Add a provider ABI-version query returning 1.

**Expected:** Caller rejects unsupported version before using handles.

**Reasoning:** A version check supplements, rather than proves, actual binary compatibility.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer real loading

Build and load a shared provider in a separate owned host project.

**Expected:** Record exported symbols, architecture, compiler and create/destroy test.

**Reasoning:** The browser source is not a dynamic-loader acceptance receipt.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
