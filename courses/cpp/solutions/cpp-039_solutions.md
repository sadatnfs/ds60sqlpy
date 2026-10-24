# cpp-039: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A C interface exposes stable-shaped calls to clients that may not share a C++ compiler. An opaque handle hides implementation details while preserving a documented owner. A loading boundary introduces version, symbol and cleanup responsibilities. Destroying an object in the wrong allocator or letting an exception cross the boundary can break the contract.

## Detailed reasoning

The opaque handle keeps C++ layout private, but its lifetime is still a public responsibility. A successful create must pair with the provider's destroy function, which can be wrapped by a unique_ptr custom deleter in a C++ client. A pointer that has already been destroyed is not made safe by a null check. The lesson checks null arguments and proper ownership; dynamic symbol loading, ABI version negotiation and foreign-language use require separate host receipts.

<!-- depth:start -->
## Opaque handles and ownership across an ABI

An opaque handle hides a C++ implementation behind a pointer-shaped public interface. A consumer can pass the handle back to the provider without knowing the class layout. This reduces coupling to implementation details, but the handle still has a lifecycle:creation succeeds or fails, use requires a live valid handle, and destruction ends that lifetime.

The create function catches allocation failure and returns null under its no-throw boundary. The caller checks that result before use. The read function returns a status code and writes through an output pointer only on success. The destroy function belongs to the provider, which keeps allocation and release responsibilities paired. A foreign consumer should not guess that its own delete or allocator is interchangeable.

The C++ consumer wraps the raw handle in a unique_ptr with the provider destroy function as custom deleter. That makes cleanup follow scope while preserving the ABI's release rule. The wrapper is a convenience on the C++ side; it is not part of the C-compatible signature. Other languages need their own lifetime wrapper or explicit finally/dispose discipline.

The null-handle negative checks a defined rejection path. It cannot make an arbitrary dangling nonnull pointer safe. Calling read after destroy is a use-after-lifetime error even if the old address still looks plausible. If the interface needs protection against stale external identifiers, it requires a different validated handle table or generation design, not only a null test.

extern "C" linkage and opaque layout are only part of ABI compatibility. Calling conventions, type widths, compiler settings, library loading and version negotiation can still matter. The single-file program demonstrates ownership and error semantics within one executable. A real shared-library consumer on each supported platform needs a separate build/load/run receipt.

## Debugging the contract

If a handle leaks on an exception path, wrap it immediately after successful creation. If a consumer frees it with the wrong allocator, restore the provider-owned destroy rule. If a null rejection passes but a stale pointer crashes, do not expand the test into undefined behavior; fix lifetime management. If dynamic loading fails, inspect exported symbols, architecture and ABI version separately from the function's internal logic.
<!-- depth:end -->

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
