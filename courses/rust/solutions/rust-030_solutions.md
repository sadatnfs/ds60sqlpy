# rust-030: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-030_solution.rs](rust-030_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Transfer owned data:** String's ownership and Send contract make the transfer valid without shared mutation. Owned text crosses the thread boundary and returns its length.

**Check capabilities at compile time:** Compile-time capability evidence is different from a runtime stress test. The compiler accepts the declared safe capability combinations.

## Task answers

### Task 1: Predict and explain

Separate ownership transfer from shared access.

No separate reference answer has been written for this task. Example A is the evidence to compare with: String's ownership and Send contract make the transfer valid without shared mutation. Owned text crosses the thread boundary and returns its length.

### Task 2: Guided modification

Move a Vec into a worker and return a derived value.

No separate reference answer has been written for this task. Start from Example B: Compile-time capability evidence is different from a runtime stress test. The compiler accepts the declared safe capability combinations.

### Task 3: Independent construction

Choose a safe shared-state type for a small concurrent counter.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use std::sync::Arc;
    use std::sync::atomic::{AtomicUsize, Ordering};
    let counter = Arc::new(AtomicUsize::new(0));
    let mut handles = Vec::new();
    for _ in 0..4 {
        let counter = Arc::clone(&counter);
        handles.push(std::thread::spawn(move || {
            for _ in 0..100 {
                counter.fetch_add(1, Ordering::Relaxed);
            }
        }));
    }
    for handle in handles {
        handle.join().unwrap();
    }
    assert_eq!(counter.load(Ordering::Relaxed), 400);
    Ok(())
}
```

**Observe:** Four threads adding 100 each produce exactly 400.

Arc<AtomicUsize> is Send and Sync, so the compiler accepts sharing it; a single counter needs no lock, and joining every thread makes the final load see all updates.

### Task 4: Diagnose a defect

Try sending Rc across threads and explain the diagnostic rather than adding unsafe.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Send does not mean simultaneous mutation is safe. Static does not mean allocated forever; it constrains borrowed references in the value. Never add unsafe impl solely to silence a compiler error.

### Task 5: Boundary evidence

Test a scoped borrowed input and compare its lifetime requirement with spawn.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Transfer owned data) and Example B (Check capabilities at compile time).

### Task 6: Transfer and justify

Document why a proposed custom type is or is not Send and Sync from its members.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Send**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Send describes whether ownership of a value can cross thread boundaries. Sync describes whether shared references can be safely used across threads, with the relationship that a shared reference to T is Send when T is Sync. These marker traits express safety properties, not performance or automatic synchronization.

Rc is single-threaded shared ownership; Arc supports concurrent reference counts. Interior-mutability types have different synchronization rules. The compiler rejects unsafe combinations, but user-defined unsafe implementations can bypass that protection only under a rigorous invariant. Prefer composing known safe types before declaring manual marker implementations.

A generic bound `T: Send` requires cross-thread transfer capability. `T: Sync` requires safe shared access. Thread spawn also imposes a lifetime requirement; Send and static solve different constraints.

Send does not mean simultaneous mutation is safe. Static does not mean allocated forever; it constrains borrowed references in the value. Never add unsafe impl solely to silence a compiler error.

## Review before continuing

Run the reference and confirm that it prints `rust-030: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
