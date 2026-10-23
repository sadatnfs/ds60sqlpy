# cpp-025: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

Undefined behavior is an operation outside the language contract, such as out-of-bounds access or signed overflow. Sanitizers instrument compiled code to detect selected violations at runtime. AddressSanitizer targets many memory errors, while UndefinedBehaviorSanitizer targets several undefined operations. A clean bounded run is evidence only for the paths exercised.

## Detailed reasoning

Checked access and sanitizer instrumentation are different mechanisms. vector::at checks its index as part of the library contract and throws out_of_range. AddressSanitizer observes selected illegal accesses in instrumented code and reports a runtime defect, often with a source stack. The ordinary safe example should never invoke undefined behavior merely to prove that it knows what a bug looks like. Compile and link the isolated fault with matching instrumentation before running it.

<!-- depth:start -->
## Checked access and instrumented memory diagnostics

Undefined behavior means the language does not provide a meaningful execution contract for that operation. An out-of-range vector subscript can appear to work, crash or produce unrelated effects. Observing one plausible value does not make it valid. A lesson should teach the invalid operation by explanation and isolated diagnostic tooling, not rely on its output as a deterministic result.

vector::at performs a checked access and throws out_of_range when the index is outside size. The first program accesses index 1 of [2, 4] and gets 4. The second requests index 2, catches the specific exception and asserts that the handler ran. This is defined behavior and a deterministic boundary test. It is different from using operator[] with index 2 and hoping for a sanitizer report.

AddressSanitizer instruments compiled code to detect selected memory errors such as certain out-of-bounds accesses and use-after-free. UndefinedBehaviorSanitizer targets other categories. These tools do not prove the absence of every bug, and their availability and supported combinations depend on the toolchain. Compile and link the isolated diagnostic program with the matching flags so the runtime support is present.

A useful sanitizer report connects an invalid access to an allocation or lifetime event and a source stack. Read the first relevant error before interpreting later symptoms. Debug symbols and a reproducible small input make the report more useful. Fix the owner, bounds or lifetime rule that caused the access rather than merely increasing allocation size until the example stops crashing.

The normal safe reference does not intentionally invoke undefined behavior. The actual fault exercise is a separate host-tooling activity with its own process and expected nonzero diagnostic outcome. That boundary prevents the browser's successful safe example from being mislabeled as a sanitizer qualification. Compiler warnings, checked APIs and dynamic instrumentation are complementary evidence.

## Debugging the contract

If at throws unexpectedly, compare the index with size, not capacity. If a sanitizer finds a use-after-free, trace the owner destruction and every retained borrow. If an instrumented link fails, check that sanitizer flags reached the link step too. If an uninstrumented invalid access seems fine, do not convert that observation into an expected output. Keep the reproducer isolated and repair the contract.
<!-- depth:end -->

## Worked example 1

```cpp
assert(checked_at({2,4},1)==4);
```

Expected: Index 1 selects 4.

## Worked example 2

```cpp
try { checked_at({2,4},2); } catch(const std::out_of_range&) { /* expected */ }
```

Expected: Checked access rejects index 2 instead of invoking unchecked access.

## Exercise 1: Classify the defect

Explain index 2 into vector size 2.

**Expected:** Out of bounds; valid indices 0 and 1.

**Reasoning:** A half-open index interval ends before size.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Use checked access

Compare at(2) with the contract of operator[2].

**Expected:** at throws; unchecked invalid access is undefined behavior.

**Reasoning:** A deterministic exception is not a sanitizer report.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Prepare instrumented build

Compile the safe reference with sanitizer flags on a supported host.

**Expected:** Compile/link/run statuses and compiler version recorded.

**Reasoning:** Instrumentation requires the matching runtime library.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Diagnose a controlled failure

In a separate instrumented scratch program introduce one heap out-of-bounds access.

**Expected:** Nonzero sanitizer report naming access and source location; never claim ordinary profile detection.

**Reasoning:** Keep the fault isolated from normal lesson execution.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Repair and rerun

Replace invalid access with a valid index or explicit check.

**Expected:** Sanitizer report disappears on that test path; result is correct.

**Reasoning:** Absence of a report is bounded evidence.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer signed arithmetic

Review INT_MAX+1 and use pre-add range validation.

**Expected:** Input rejected before overflow.

**Reasoning:** Sanitizers diagnose executed undefined operations, not all possible inputs.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
