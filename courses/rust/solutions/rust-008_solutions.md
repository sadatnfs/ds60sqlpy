# rust-008: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-008_solution.rs](rust-008_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Move ownership to a new binding:** The reference intentionally does not compile an invalid old-binding access; the practice task asks the learner to inspect that diagnostic separately. The new binding owns the text.

**Clone only when two owners are needed:** The explicit clone makes the allocation and independent ownership decision visible. The cloned String can change independently.

## Reason through the six tasks

1. **Predict and explain.** Draw ownership before and after the move.

2. **Guided modification.** Temporarily read first after its move and preserve the compiler diagnostic.

3. **Independent construction.** Write a function taking and returning an owned String.

4. **Diagnose a defect.** Diagnose adding clones everywhere instead of choosing a borrowed interface.

5. **Boundary evidence.** Compare String movement with copying an i32.

6. **Transfer and justify.** Explain whether a function should borrow, clone or take ownership when retaining data for later use.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Every owned value has a responsibility for releasing its resources. Moving a non-Copy value transfers that responsibility to another binding or operation. The old binding can no longer be used as though it still owns the value. This prevents accidental double release and many use-after-free errors before execution.

Clone explicitly asks for a value-level duplication defined by the type. Cloning a String duplicates its text storage; cloning an Arc later duplicates shared ownership rather than deep-copying its contents. Copy is a stricter implicit duplication capability used by suitable simple types. Learn the semantic distinction instead of assuming every assignment copies everything.

Assignment of String moves ownership. `.clone()` requests the type's duplication behavior. A function taking String owns its argument and may retain or release it. Returning the String transfers ownership back.

Clone does not universally mean deep copy. A move can be optimized without changing its ownership semantics. Compiler rejection of a use-after-move is useful evidence, not an obstacle to suppress.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
