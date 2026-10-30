# cpp-023: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

An API is the source-level interface callers use. An ABI is the compiled calling, layout and symbol convention needed to link binaries. C++ standard library objects are risky across independently compiled boundaries. A narrow C interface uses agreed primitive representations, explicit ownership and status codes to reduce coupling. This example uses platform int; a cross-platform serialized format needs its own fixed-width encoding contract.

## Detailed reasoning

The caller and library must agree on the function symbol and how its arguments/results cross the machine boundary. extern C reduces name-mangling ambiguity but does not specify all platform ABI details. The caller owns the output integer, while the function owns only the act of validating and assigning it. The overflow case returns before assignment, so the previous output value remains a useful check that failure did not publish a partial result.

<!-- depth:start -->
## C-compatible boundaries and error translation

A C-compatible function boundary is useful when code crosses a language or binary interface. extern "C" changes language linkage conventions for the named function; it does not automatically make every C++ parameter, exception or object layout safe for a C caller. The public signature should use a deliberately constrained representation and a documented ownership/error policy.

add_checked takes two integers and an output pointer, returning a status code. Status0 means the output was written successfully; status 1 denotes a null output pointer; status 2 denotes signed-int overflow. Both failure paths return before assigning the output, so its previous value is preserved. The interface uses this platform's int representation, not a fixed-width wire format. A caller must check status before consuming the output. Returning an integer sum alone would leave no distinct channel for a failure if every integer value could also be legitimate data.

A null check can reject a missing pointer, but it cannot prove that an arbitrary nonnull pointer points to writable live storage. The caller still has a precondition to supply a valid output object. After an object is destroyed, a dangling address may remain nonnull. C-style interfaces therefore need precise lifetime and buffer-size contracts in addition to defensive null checks.

Exceptions must not escape a boundary that promises not to throw. A wrapper around potentially throwing C++ work should catch exceptions and translate them into the declared status result while preserving cleanup through RAII. noexcept is a promise enforced by termination if an exception escapes, it is not a catch block. Marking a function noexcept without controlling its implementation can make failure less recoverable.

The single-file program proves the illustrated call and error conventions within one C++ executable. It does not prove dynamic loading, ABI compatibility across compilers or successful use by another language. The later opaque-handle and host-library exercises add those boundaries separately. Keep source linkage, linker success and real foreign-consumer acceptance as distinct evidence.

## Debugging the contract

If the caller reads output after a nonzero status, it may be using an old value. If a null check passes but access crashes, inspect lifetime and buffer validity rather than assuming nonnull means safe. If an exception crosses a C boundary, add translation at the boundary and preserve a stable error contract. If a symbol cannot be found during linking, check language linkage and the actual exported name separately from runtime pointer behavior.
<!-- depth:end -->

## Worked example 1

```cpp
int out = 0;
assert(add_checked(2, 3, &out) == 0 && out == 5);
```

Expected: Status 0 publishes value 5 through the caller-owned pointer.

## Worked example 2

```cpp
assert(add_checked(2, 3, nullptr) == 1);
```

Expected: Null output pointer returns status 1 without dereferencing it.

## Exercise 1: Separate interfaces

List the add_checked source contract and binary assumptions.

**Expected:** Names/types/statuses versus compiler/platform/linkage distinguished.

**Reasoning:** An ABI includes details the header alone cannot prove.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Call a valid boundary

Pass 2, 3 and a writable output integer.

**Expected:** Status 0 and output 5.

**Reasoning:** Caller owns the destination storage.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Reject null output

Pass nullptr for out.

**Expected:** Status 1, no invalid access.

**Reasoning:** Validate pointers before dereference.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair exception leakage

Review a C wrapper that lets std::runtime_error escape.

**Expected:** Catch inside wrapper and map to a documented status.

**Reasoning:** Foreign callers cannot assume a compatible exception runtime.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Check overflow

Call INT_MAX plus 1.

**Expected:** Status 2; no overflowing addition.

**Reasoning:** Check arithmetic before evaluating it.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer a shared library

Build the wrapper separately in an owned host project and record compiler/architecture.

**Expected:** Real link/load receipt plus matching header, no inferred portability.

**Reasoning:** The browser single-file run does not exercise a shared-library ABI.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
