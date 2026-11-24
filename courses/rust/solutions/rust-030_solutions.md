# rust-030: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-030_solution.rs](rust-030_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Transfer owned data:** String's ownership and Send contract make the transfer valid without shared mutation. Owned text crosses the thread boundary and returns its length.

**Check capabilities at compile time:** Compile-time capability evidence is different from a runtime stress test. The compiler accepts the declared safe capability combinations.

## Task answers

### Task 1: Predict and explain

Separate ownership transfer from shared access.

**Written answer.** Example A is ownership transfer: `move` puts `text` into the closure, the closure moves into the new thread, and `main` can no longer use `text`; the length comes back as the join result. Example B is about shared access: `Sync` means a `&String` may be used from several threads at once, and `Arc<Mutex<i32>>` is `Send`, so a handle can be given to another thread while the data stays shared.

**Why it is correct.** `Send` is about moving a value to another thread, while `Sync` is about sharing references to it. A type can satisfy one without the other, so the two questions must be asked separately.

**Plausible wrong approach.** Treating `move` as making a copy for the thread predicts that `text` is still usable in `main`; using it after the spawn is E0382.

**How to verify.** Add `println!("{text}");` after the spawn in Example A and read E0382, borrow of moved value.

### Task 2: Guided modification

Move a Vec into a worker and return a derived value.

**Reference answer.** The same statements run as the `Task 2` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let readings = vec![4, 8, 15, 16];
    let worker = std::thread::spawn(move || {
        let total: i32 = readings.iter().sum();
        (readings.len(), total)
    });
    assert_eq!(worker.join().unwrap(), (4, 43));
    Ok(())
}
```

**Observe:** The worker reports four readings with total 43.

`move` transfers the whole `Vec`, including its heap buffer, into the worker, which is valid because `Vec<i32>` is `Send`. The worker returns a small derived tuple, so the parent receives results without sharing the vector at all.

**Plausible wrong approach.** Dropping `move` makes the closure borrow `readings`, and `std::thread::spawn` rejects that with E0373 because the thread could outlive the vector.

**How to verify.** Run the block. Then add `readings.len()` after the spawn and read E0382.

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

**Written answer.** The defect is `let shared = std::rc::Rc::new(5); std::thread::spawn(move || *shared + 1);`. rustc reports E0277, `Rc<i32>` cannot be sent between threads safely, because `Send` is not implemented for `Rc<i32>`. `Rc` updates its reference count with ordinary, non-atomic arithmetic, so two threads cloning or dropping it could corrupt the count. Use `Arc`, whose count is atomic.

**Why it is correct.** The marker traits encode which operations are safe across threads, and the compiler derives them from a type's members. `Rc` is deliberately not `Send`, so the rejection is a correct proof failure, not a limitation to work around.

**Plausible wrong approach.** Wrapping the `Rc` in a struct with `unsafe impl Send` silences the error and reintroduces the data race the diagnostic was preventing.

**How to verify.** Compile the defect and read E0277. Replace `std::rc::Rc` with `std::sync::Arc` and it compiles and returns 6.

### Task 5: Boundary evidence

Test a scoped borrowed input and compare its lifetime requirement with spawn.

**Reference answer.** The same statements run as the `Task 5` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let rows = vec![String::from("a"), String::from("bc")];
    let total = std::thread::scope(|scope| {
        let worker = scope.spawn(|| rows.iter().map(String::len).sum::<usize>());
        worker.join().unwrap()
    });
    assert_eq!(total, 3);
    assert_eq!(rows.len(), 2);
    let empty: Vec<String> = Vec::new();
    let count = std::thread::scope(|scope| scope.spawn(|| empty.len()).join().unwrap());
    assert_eq!(count, 0);
    Ok(())
}
```

**Observe:** The scoped worker reads the borrowed rows and returns 3, the rows are still usable afterward, and an empty input gives 0.

A scoped thread may borrow `rows` because the scope cannot return until the thread has finished, so the borrow cannot outlive its owner. `std::thread::spawn` requires a `'static` closure instead: the same borrowing closure is rejected with E0373, and the fix there is `move` plus ownership.

**Plausible wrong approach.** Assuming `'static` means the data must live for the whole program leads to leaking or using global data. It only means the closure holds no borrowed references that could expire.

**How to verify.** Run the block. Replace `scope.spawn` with `std::thread::spawn` in the first worker and read E0373, closure may outlive the current function.

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
