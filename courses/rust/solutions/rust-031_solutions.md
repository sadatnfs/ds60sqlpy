# rust-031: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-031_solution.rs](rust-031_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Represent recursion through indirection:** Each node owns the next node and releases that chain through ordinary ownership. Box makes the recursive type have a finite outer size.

**Observe a weak target disappearing:** Upgrade makes absence explicit after the final strong owner is released. The weak reference does not keep the String alive.

## Reason through the six tasks

1. **Predict and explain.** Draw the owning edges of the recursive list.

2. **Guided modification.** Add another node and predict its total.

3. **Independent construction.** Model a parent-child relationship with a weak back-reference.

4. **Diagnose a defect.** Diagnose an Rc cycle that keeps both objects alive.

5. **Boundary evidence.** Test an empty list and upgrading a dead weak reference.

6. **Transfer and justify.** Choose Box, Rc or Arc for unique, local-shared and cross-thread ownership scenarios.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Box provides owned indirection, useful when a recursive structure needs a finite-sized outer representation. Rc provides shared ownership within one thread, while Weak provides a non-owning link that may no longer upgrade to a live owner. These pointers express different lifetime contracts and should not be chosen interchangeably.

Cycles of strong reference counts can leak resources even in memory-safe Rust. A parent-child structure often needs owning edges in one direction and weak back-references in the other. RefCell permits checked interior mutation in a single thread; violating its dynamic borrowing rules panics. It does not make Rc suitable for concurrent access.

Box::new stores an owned value behind a pointer. Rc::clone increments shared ownership. Rc::downgrade creates Weak, and upgrade returns Option because the owner may have disappeared.

Memory safety does not guarantee absence of leaks. Deep recursive drops can have stack costs. RefCell moves borrow checking to runtime and remains single-threaded.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
