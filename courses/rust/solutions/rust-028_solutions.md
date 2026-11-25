# rust-028: explanation and comparison

Executable reference: [rust-028_solution.rs](rust-028_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Protect concurrent increments:** The lock protects the complete read-modify-write transition, not merely its final assignment. All four hundred increments are retained.

**Protect a relationship in one value:** Grouping related state makes the invariant's synchronization boundary visible. The transfer preserves the total under one protected tuple.

## Task answers

### Task 1: Predict and explain

Draw shared ownership separately from mutable access.

**Written answer.** Shared ownership: one heap allocation holds the `Mutex<i32>`, and `Arc::clone` gives each of the four workers its own `Arc` handle to it, so the strong count is five while they run and drops back to one when the scope ends. Mutable access is a separate path: a worker may change the integer only through the `MutexGuard` returned by `lock()`, and only one guard exists at a time.

**Why it is correct.** `Arc` answers who keeps the value alive, and `Mutex` answers who may change it now. Example A needs both answers, which is why the type is `Arc<Mutex<i32>>` and not either one alone.

**Plausible wrong approach.** Drawing each `Arc::clone` as a copy of the counter predicts four separate counts of 100. The final 400 shows that all clones point to the same protected integer.

**How to verify.** Print `Arc::strong_count(&count)` inside one worker and after the scope: the first is greater than 1, the second is 1.

### Task 2: Guided modification

Add another worker while keeping the exact expected total.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 2` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use std::sync::{Arc, Mutex};
    let workers = 5;
    let per_worker = 100;
    let count = Arc::new(Mutex::new(0));
    std::thread::scope(|scope| {
        for _ in 0..workers {
            let count = Arc::clone(&count);
            scope.spawn(move || {
                for _ in 0..per_worker {
                    *count.lock().unwrap() += 1;
                }
            });
        }
    });
    assert_eq!(*count.lock().unwrap(), workers * per_worker);
    assert_eq!(Arc::strong_count(&count), 1);
    Ok(())
}
```

**Observe:** Five workers of 100 increments each produce exactly 500, and only the original Arc remains afterward.

The expected total is computed from the same two numbers that drive the loops, so adding a worker cannot leave a stale literal behind. Each increment happens under the lock as one read-modify-write step, which is why no update is lost.

**Plausible wrong approach.** Locking once to read, releasing, and locking again to write the incremented value can lose updates between the two locks, and the total falls below 500 on some runs.

**How to verify.** Run the block several times; the total is always 500. Change `workers` to 6 and the expectation follows to 600 without another edit.

### Task 3: Independent construction

Implement a locked bounded reservation operation.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

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

**Written answer.** The defect is `let from = Mutex::new(10); let to = Mutex::new(0);` with a transfer that does `*from.lock().unwrap() -= 3;` and then, in a separate statement, `*to.lock().unwrap() += 3;`. Between those two statements neither lock is held, so another thread can lock both and see a total of 7 instead of 10. Put the related values in one `Mutex<(i32, i32)>`, as Example B does, so the invariant has one synchronization boundary.

**Why it is correct.** Each lock protects only its own value. The relationship `from + to == 10` spans both, so it needs a lock that covers both updates at once.

**Plausible wrong approach.** Holding both locks but acquiring them in opposite orders in two different transfer directions closes the gap and introduces a deadlock instead.

**How to verify.** In one thread, after the first update and before the second, lock both values and assert their sum: it is 7.

### Task 5: Boundary evidence

Test zero operations and an explicitly handled poisoned lock in a separate controlled case.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 5` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let total = std::sync::Mutex::new(0);
    std::thread::scope(|scope| {
        for _ in 0..0 {
            scope.spawn(|| *total.lock().unwrap() += 1);
        }
    });
    assert_eq!(*total.lock().unwrap(), 0);
    let previous = std::panic::take_hook();
    std::panic::set_hook(Box::new(|_| {}));
    let balances = std::sync::Mutex::new((10, 0));
    let crashed = std::thread::scope(|scope| {
        scope
            .spawn(|| -> i32 {
                let mut guard = balances.lock().unwrap();
                guard.0 -= 3;
                panic!("crashed mid-transfer");
            })
            .join()
    });
    std::panic::set_hook(previous);
    assert!(crashed.is_err());
    assert!(balances.is_poisoned());
    let recovered = match balances.lock() {
        Ok(guard) => *guard,
        Err(poisoned) => *poisoned.into_inner(),
    };
    assert_eq!(recovered, (7, 0));
    assert_ne!(recovered.0 + recovered.1, 10);
    Ok(())
}
```

**Observe:** Zero operations leave the total at 0. The worker that panics while holding the guard poisons the mutex, and the recovered value is (7, 0), a half-finished transfer.

Zero workers is a legal workload, so the result must be the initial value, not an error. Poisoning is the signal that a panic happened inside the critical section; `into_inner` deliberately reads the data anyway, and the last assertion shows why that needs a policy: the invariant is broken.

**Plausible wrong approach.** Recovering with `lock().unwrap_or_else(|p| p.into_inner())` everywhere and carrying on treats (7, 0) as a valid state and silently loses three units.

**How to verify.** Run the block. Move `guard.0 -= 3;` after the panic (making it unreachable) and the recovered value becomes (10, 0), still poisoned but consistent.

### Task 6: Transfer and justify

Choose message passing or shared locking for a service and justify the invariant owner.

**Judging criteria.** A strong answer names the invariant first, such as Example B's pair keeping its total of 10, and then the owner that enforces it. With message passing, one task owns the state and others send requests, so the invariant lives in one loop and needs no lock. With shared locking, every holder of the `Arc<Mutex<_>>` must update both fields under one guard. Prefer the design in which the fewest places can break the invariant. State one limitation: a single owner task serializes every request and adds a channel hop to each read.

## Mechanism and diagnostic reasoning

Arc provides atomically reference-counted shared ownership. It does not make the stored value safely mutable by itself. Mutex provides mutually exclusive access to a protected value, and its guard releases the lock when dropped. Put the whole invariant inside that protected transition.

Several separately protected fields can still violate a relationship if updated under different locks or at different times. Lock ordering matters when several locks are involved. Keep protected work small and avoid calling unknown code while holding a lock. Poisoning reports a panic while a lock was held and requires an explicit recovery policy.

Arc::clone shares ownership rather than deep-copying the value. Mutex::lock returns a result containing a guard. Dereferencing the mutable guard grants access until its scope ends.

Arc is not a lock and clone does not copy its inner state. Holding a guard longer than needed can block unrelated work. Do not ignore poisoning without understanding whether the invariant survived.

## Review before continuing

Rebuild Example B (Protect a relationship in one value) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
