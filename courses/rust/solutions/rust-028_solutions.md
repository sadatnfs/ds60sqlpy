# rust-028: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-028_solution.rs](rust-028_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Protect concurrent increments:** The lock protects the complete read-modify-write transition, not merely its final assignment. All four hundred increments are retained.

**Protect a relationship in one value:** Grouping related state makes the invariant's synchronization boundary visible. The transfer preserves the total under one protected tuple.

## Task answers

### Task 1: Predict and explain

Draw shared ownership separately from mutable access.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The lock protects the complete read-modify-write transition, not merely its final assignment. All four hundred increments are retained.

### Task 2: Guided modification

Add another worker while keeping the exact expected total.

No separate reference answer has been written for this task. Start from Example B: Grouping related state makes the invariant's synchronization boundary visible. The transfer preserves the total under one protected tuple.

### Task 3: Independent construction

Implement a locked bounded reservation operation.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let stock = std::sync::Mutex::new(5_u32);
    let reserve = |amount: u32| {
        let mut available = stock.lock().unwrap();
        let granted = amount <= *available;
        if granted {
            *available -= amount;
        }
        granted
    };
    let results: Vec<bool> = std::thread::scope(|scope| {
        let handles: Vec<_> = (0..4).map(|_| scope.spawn(|| reserve(2))).collect();
        handles
            .into_iter()
            .map(|handle| handle.join().unwrap())
            .collect()
    });
    assert_eq!(results.iter().filter(|granted| **granted).count(), 2);
    assert_eq!(*stock.lock().unwrap(), 1);
    Ok(())
}
```

**Observe:** Of four concurrent requests for 2 units from a stock of 5, exactly two succeed and 1 unit remains.

The check and the decrement happen under one lock guard, so no other thread can reserve between them and the stock never goes negative.

### Task 4: Diagnose a defect

Diagnose protecting each half of a transfer with unrelated locks.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Arc is not a lock and clone does not copy its inner state. Holding a guard longer than needed can block unrelated work. Do not ignore poisoning without understanding whether the invariant survived.

### Task 5: Boundary evidence

Test zero operations and an explicitly handled poisoned lock in a separate controlled case.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Protect concurrent increments) and Example B (Protect a relationship in one value).

### Task 6: Transfer and justify

Choose message passing or shared locking for a service and justify the invariant owner.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Arc**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Arc provides atomically reference-counted shared ownership. It does not make the stored value safely mutable by itself. Mutex provides mutually exclusive access to a protected value, and its guard releases the lock when dropped. Put the whole invariant inside that protected transition.

Several separately protected fields can still violate a relationship if updated under different locks or at different times. Lock ordering matters when several locks are involved. Keep protected work small and avoid calling unknown code while holding a lock. Poisoning reports a panic while a lock was held and requires an explicit recovery policy.

Arc::clone shares ownership rather than deep-copying the value. Mutex::lock returns a result containing a guard. Dereferencing the mutable guard grants access until its scope ends.

Arc is not a lock and clone does not copy its inner state. Holding a guard longer than needed can block unrelated work. Do not ignore poisoning without understanding whether the invariant survived.

## Review before continuing

Run the reference and confirm that it prints `rust-028: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
