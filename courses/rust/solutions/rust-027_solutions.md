# rust-027: explanation and comparison

Executable reference: [rust-027_solution.rs](rust-027_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Borrow local input safely:** The scope guarantees the worker cannot outlive the owner of the borrowed vector. The borrowed input remains usable after the joined scope.

**Return independent results:** No shared writable accumulator is needed for this decomposition. The parent combines two completed results.

## Task answers

### Task 1: Predict and explain

Identify who owns input and each thread handle.

**Written answer.** In Example A the outer block owns `values`. The spawned closure only borrows it through `values.iter()`, and `std::thread::scope` guarantees the thread ends before the scope returns. `handle` is a `ScopedJoinHandle` owned by the scope closure, and `join()` consumes it to return the sum. In Example B each of `left` and `right` owns one handle, and each is consumed by its own `join`.

**Why it is correct.** Joining takes the handle by value, so a result can be collected only once, and the scope's end is the point after which no borrow from the parent may still be in use.

**Plausible wrong approach.** Saying the thread owns `values` would require a `move` closure and would make `values.len()` after the scope fail with E0382.

**How to verify.** Add `move` before the closure in Example A and read E0382 on `values.len()`.

### Task 2: Guided modification

Split an array into two borrowed halves and combine their totals.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 2` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let values = [3, 1, 4, 1, 5];
    let (left, right) = values.split_at(values.len() / 2);
    assert_eq!((left.len(), right.len()), (2, 3));
    let total = std::thread::scope(|scope| {
        let low = scope.spawn(|| left.iter().sum::<i32>());
        let high = scope.spawn(|| right.iter().sum::<i32>());
        low.join().expect("left half") + high.join().expect("right half")
    });
    assert_eq!(total, 14);
    assert_eq!(total, values.iter().sum::<i32>());
    Ok(())
}
```

**Observe:** With five values the halves hold two and three elements, and the threaded total matches the sequential sum, 14.

`split_at` returns two non-overlapping borrowed slices, so no element is copied or counted twice. With an odd length, integer division puts the extra element in the right half, which the length assertion records.

**Plausible wrong approach.** Computing the halves as `&values[..mid]` and `&values[mid - 1..]` double-counts one element and still looks plausible on small inputs.

**How to verify.** Run the block, then change the second slice to start one element earlier and the sequential comparison fails.

### Task 3: Independent construction

Build a scoped parallel computation returning values to the parent.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

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

**Written answer.** The defect is `std::thread::spawn(move || write_report(rows));` with the returned `JoinHandle` discarded. An unscoped handle that is dropped detaches the thread: `main` can return and end the process before the report is written, and a panic in the worker is never observed. Keep the handle and call `join()`, or use `std::thread::scope`, which joins everything before returning.

**Why it is correct.** `join` is the only point where completion and panic become visible to the parent. Without it, success is an assumption about timing, not a fact.

**Plausible wrong approach.** Adding `std::thread::sleep(Duration::from_millis(100))` before returning makes it pass on a fast machine and fail under load.

**How to verify.** Spawn a thread that sleeps 200 ms and then sets an `AtomicBool`, drop its handle, and check the flag immediately: it is still false.

### Task 5: Boundary evidence

Test empty partitions and an intentional worker panic in a controlled external test.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 5` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let empty: [i32; 0] = [];
    let (left, right) = empty.split_at(0);
    let total = std::thread::scope(|scope| {
        let low = scope.spawn(|| left.iter().sum::<i32>());
        let high = scope.spawn(|| right.iter().sum::<i32>());
        low.join().expect("left half") + high.join().expect("right half")
    });
    assert_eq!(total, 0);
    let previous = std::panic::take_hook();
    std::panic::set_hook(Box::new(|_| {}));
    let outcome = std::thread::scope(|scope| {
        let worker = scope.spawn(|| -> i32 { panic!("worker failed") });
        worker.join()
    });
    std::panic::set_hook(previous);
    assert!(outcome.is_err());
    Ok(())
}
```

**Observe:** Two empty partitions sum to 0, and the intentionally panicking worker is reported to the parent as Err from join.

Summing an empty slice is 0, so empty partitions need no special case. A worker panic is caught at its `join`, which returns `Err` instead of a value; the parent then decides what that means. The panic hook is silenced only around the deliberate panic and restored afterward, so the test output stays clean.

**Plausible wrong approach.** Writing `worker.join().unwrap_or(0)` turns a crashed worker into a plausible zero, exactly the default success the lesson warns about.

**How to verify.** Run the block, then remove the `panic!` so the worker returns `1`, and the `is_err` assertion fails.

### Task 6: Transfer and justify

Choose threads or sequential work using workload size and synchronization cost.

**Judging criteria.** A strong answer measures before choosing. Spawning and joining a thread costs far more than adding a few integers, so Example B's two sums are faster done sequentially; threads pay only when each chunk is large and independent. Compare a sequential baseline with a scoped version over the same input at several sizes, count any lock or channel traffic as cost, and keep the combined result independent of finishing order. State one limitation: timings in a shared container are noisy, so repeat runs and report a range.

## Mechanism and diagnostic reasoning

A thread can run concurrently with its creator and must have a clear lifetime owner. Unscoped thread spawn requires captured references to satisfy the required lifetime, often leading to owned move captures. Scoped threads instead guarantee joining before the scope returns, allowing safe borrowing of suitable local data.

Joining observes completion and panic outcomes. Do not infer completion from a sleep. Independent tasks can compute values and return them to one owner, avoiding shared mutable state. Threads are an execution mechanism, not an automatic speedup for tiny workloads or blocked external systems.

std::thread::scope bounds child lifetimes. scope.spawn creates a scoped worker. join returns its result or panic information. Immutable borrowed inputs can be shared when their types satisfy the concurrency requirements.

Sleep is not a synchronization guarantee. A joined panic is a distinct failure that should not become a default successful result. More threads can increase overhead and resource pressure.

## Review before continuing

Rebuild Example B (Return independent results) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
