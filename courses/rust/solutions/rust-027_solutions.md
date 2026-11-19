# rust-027: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-027_solution.rs](rust-027_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Borrow local input safely:** The scope guarantees the worker cannot outlive the owner of the borrowed vector. The borrowed input remains usable after the joined scope.

**Return independent results:** No shared writable accumulator is needed for this decomposition. The parent combines two completed results.

## Task answers

### Task 1: Predict and explain

Identify who owns input and each thread handle.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The scope guarantees the worker cannot outlive the owner of the borrowed vector. The borrowed input remains usable after the joined scope.

### Task 2: Guided modification

Split an array into two borrowed halves and combine their totals.

No separate reference answer has been written for this task. Start from Example B: No shared writable accumulator is needed for this decomposition. The parent combines two completed results.

### Task 3: Independent construction

Build a scoped parallel computation returning values to the parent.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let values = [1, 2, 3, 4, 5, 6];
    let (left, right) = values.split_at(3);
    let (a, b) = std::thread::scope(|scope| {
        let first = scope.spawn(|| left.iter().sum::<i32>());
        let second = scope.spawn(|| right.iter().sum::<i32>());
        (first.join().unwrap(), second.join().unwrap())
    });
    assert_eq!((a, b), (6, 15));
    assert_eq!(a + b, values.iter().sum::<i32>());
    Ok(())
}
```

**Observe:** The halves sum to 6 and 15, together 21, the same as the sequential sum.

Scoped threads may borrow values because scope joins them before returning, and each join hands a result back to the parent.

### Task 4: Diagnose a defect

Diagnose dropping a handle and assuming the work finished.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Sleep is not a synchronization guarantee. A joined panic is a distinct failure that should not become a default successful result. More threads can increase overhead and resource pressure.

### Task 5: Boundary evidence

Test empty partitions and an intentional worker panic in a controlled external test.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Borrow local input safely) and Example B (Return independent results).

### Task 6: Transfer and justify

Choose threads or sequential work using workload size and synchronization cost.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Thread**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A thread can run concurrently with its creator and must have a clear lifetime owner. Unscoped thread spawn requires captured references to satisfy the required lifetime, often leading to owned move captures. Scoped threads instead guarantee joining before the scope returns, allowing safe borrowing of suitable local data.

Joining observes completion and panic outcomes. Do not infer completion from a sleep. Independent tasks can compute values and return them to one owner, avoiding shared mutable state. Threads are an execution mechanism, not an automatic speedup for tiny workloads or blocked external systems.

std::thread::scope bounds child lifetimes. scope.spawn creates a scoped worker. join returns its result or panic information. Immutable borrowed inputs can be shared when their types satisfy the concurrency requirements.

Sleep is not a synchronization guarantee. A joined panic is a distinct failure that should not become a default successful result. More threads can increase overhead and resource pressure.

## Review before continuing

Run the reference and confirm that it prints `rust-027: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
