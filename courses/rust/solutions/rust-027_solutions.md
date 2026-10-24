# rust-027: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-027_solution.rs](rust-027_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Borrow local input safely:** The scope guarantees the worker cannot outlive the owner of the borrowed vector. The borrowed input remains usable after the joined scope.

**Return independent results:** No shared writable accumulator is needed for this decomposition. The parent combines two completed results.

## Reason through the six tasks

1. **Predict and explain.** Identify who owns input and each thread handle.

2. **Guided modification.** Split an array into two borrowed halves and combine their totals.

3. **Independent construction.** Build a scoped parallel computation returning values to the parent.

4. **Diagnose a defect.** Diagnose dropping a handle and assuming the work finished.

5. **Boundary evidence.** Test empty partitions and an intentional worker panic in a controlled external test.

6. **Transfer and justify.** Choose threads or sequential work using workload size and synchronization cost.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A thread can run concurrently with its creator and must have a clear lifetime owner. Unscoped thread spawn requires captured references to satisfy the required lifetime, often leading to owned move captures. Scoped threads instead guarantee joining before the scope returns, allowing safe borrowing of suitable local data.

Joining observes completion and panic outcomes. Do not infer completion from a sleep. Independent tasks can compute values and return them to one owner, avoiding shared mutable state. Threads are an execution mechanism, not an automatic speedup for tiny workloads or blocked external systems.

std::thread::scope bounds child lifetimes. scope.spawn creates a scoped worker. join returns its result or panic information. Immutable borrowed inputs can be shared when their types satisfy the concurrency requirements.

Sleep is not a synchronization guarantee. A joined panic is a distinct failure that should not become a default successful result. More threads can increase overhead and resource pressure.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
