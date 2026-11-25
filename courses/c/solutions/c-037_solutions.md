# c-037: explained solutions

`c-037_solution.c` assembles the "protect a shared count" case through the "transfer count invariance" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

A mutex protects shared state only when every relevant reader and writer follows the same locking protocol. A condition variable lets a thread wait for a state predicate to become true while releasing the mutex atomically during the wait. Notifications are not stored as durable messages, and waking does not prove the predicate is true. Always recheck it in a loop to handle spurious wakeups and other consumers. Change the predicate under the same mutex used by waiters. Keep lock ownership and destruction explicit, and do not destroy a mutex or condition variable while another thread can still use it.

pthread_mutex_lock and unlock delimit the protected region. pthread_cond_wait expects the mutex to be locked, releases it while waiting, and reacquires it before returning. while(!ready) wait is the correct shape for this fixture. Signal after updating the protected state. Join the worker before destroying synchronization objects. A sleep cannot replace the predicate protocol.

## Exercise 1: Protect a shared count: predict an edited check

In worked example 1, change `CHECK(locked_total(4, 100) == 400);` to `CHECK(locked_total(5, 100) == 400);`. Predict whether the CHECK still holds and why, then run and restore.

The unchanged code is worked example 1:

```c
CHECK(locked_total(4, 100) == 400);
```

**Expected:** `Check failed`: `CHECK(locked_total(5, 100) == 400);` is false, although the final count is 400.

Every increment is inside the same critical section, and the parent joins all writers before reading the final value.

**Approach.** Multiply workers by iterations: 5 workers each adding 100 under the mutex give exactly 500.

**Why it holds here.** 5 is still within the `workers <= 5` guard for the `threads[5]` array, and each increment is a locked read-modify-write, so none are lost and 500 is not 400.

**A plausible wrong approach.** Predicting a count that varies from run to run near 400 or 500, as with an unprotected counter. The mutex serializes every `s->count++`, so the total is exact on every run; only the interleaving changes.

**Verify.** Print `locked_total(5, 100)` several times and see 500 each time.

## Exercise 2: Handle one worker: diagnose an edited check

Worked example 2's CHECK now reads `CHECK(locked_total(2, 7) == 7);`. Explain why it fails although the result is 7, then restore it.

The unchanged code is worked example 2:

```c
CHECK(locked_total(1, 7) == 7);
```

**Expected:** `Check failed` until the CHECK reads `CHECK(locked_total(1, 7) == 7);` again, though the result is 7.

The sequential boundary exercises the same synchronization implementation without depending on contention.

**Approach.** Note that `iterations` is per worker: with 2 workers each running 7 increments the total is 14.

**Why it holds here.** Each thread runs the full `for` loop over `s->iterations`, so adding a worker adds another 7, and the edited CHECK compares 14 with 7.

**A plausible wrong approach.** Reading the second argument as a total split among the workers and predicting 7. Nothing in `increment_worker` divides the work, so the count scales with the number of threads.

**Verify.** Print `locked_total(2, 7)` and see 14, and `locked_total(1, 7)` and see 7.

## Exercise 3: Handle zero loop iterations

Run two workers whose increment loops are empty.

```c
CHECK(locked_total(2, 0) == 0);
```

**Expected:** The result remains zero.

Worker creation and cleanup still occur even though the protected state never changes.

**Approach.** Create and join both workers even though each loop body runs zero times.

**Why it holds here.** Each worker reads `s->iterations` as 0, never locks the mutex and returns, so `count` stays 0; joining before the mutex is destroyed keeps the cleanup order valid.

**A plausible wrong approach.** Skipping `pthread_join` when there is no work to wait for. The workers still read `s->iterations` through a pointer to `locked_total`'s local `s`, so returning first leaves them reading a dead object, which is undefined.

**Verify.** Run the CHECK under AddressSanitizer and UndefinedBehaviorSanitizer and see a clean run with 0.

## Exercise 4: Wait for a predicate

Wait until a worker publishes ready with value 42.

```c
CHECK(wait_for_value() == 42);
```

**Expected:** The parent observes value 42.

The while loop checks actual state after every wakeup. The signal itself is not treated as the result payload.

**Approach.** Hold the mutex and wait in `while (!s.ready)`, then read `s.value` while still holding the lock.

**Why it holds here.** The worker sets `value` and `ready` under the same mutex before signaling, so when the loop exits the predicate is true and `value` is the published 42, whether the signal came before or after the wait began.

**A plausible wrong approach.** Writing `if (!s.ready)` instead of `while`. `pthread_cond_wait` may return without a signal (a spurious wakeup), and with `if` the parent then reads `value` while `ready` is still false and can return 0.

**Verify.** Print `wait_for_value()` and see 42; the loop re-tests `ready` after every return from `pthread_cond_wait`.

## Exercise 5: Repeat independent synchronization

Create and destroy the predicate fixture twice.

```c
CHECK(wait_for_value() == 42 && wait_for_value() == 42);
```

**Expected:** Both operations return 42.

Each invocation owns fresh synchronization objects and joins before destruction, avoiding cross-run state leakage.

**Approach.** Call the fixture twice; each call initializes its own mutex, condition variable and `ready` flag and destroys them after joining.

**Why it holds here.** Nothing survives between calls, so the second wait depends only on its own worker's publication and returns 42.

**A plausible wrong approach.** Making `struct ReadyState s` static to avoid reinitializing it. Its initializer runs once, so the second call sees `ready` already true, skips the wait and returns the first run's value. The CHECK still passes because both values are 42, so publish a different value per run to expose it.

**Verify.** Print both calls in separate statements and see 42 and 42; give each run a distinct value to make stale state visible.

## Exercise 6: Transfer count invariance

Compare two workers times five increments with five workers times two.

```c
CHECK(locked_total(2, 5) == 10 && locked_total(5, 2) == 10);
```

**Expected:** Both totals are 10.

Scheduling changes but the protected update count remains invariant. This is correctness evidence, not a performance comparison.

**Approach.** Run 2 workers of 5 increments and 5 workers of 2, each under the same locked increment.

**Why it holds here.** Every protected increment is counted exactly once, so both totals equal the product, 10, regardless of how the threads are scheduled.

**A plausible wrong approach.** Dropping the lock because the counts are small, `s->count++;` alone. Unsynchronized concurrent writes are a data race and undefined behavior; a small test may still print 10 by luck, so a passing run proves nothing, and ThreadSanitizer is the tool that reports it. Describe it rather than run it.

**Verify.** Print `locked_total(2, 5)` and `locked_total(5, 2)` in separate statements and see 10 and 10.

## After comparison

Write `int wait_for_count(int target)` that starts 3 workers, each adding 1 to a shared count under a mutex and broadcasting with `pthread_cond_broadcast`, while the parent waits in a `while (count < target)` loop. Check targets 0, 1 and 3, joining every worker before destroying the objects. Explain why waiting with `while (count != target)` can block forever when several increments land before the parent wakes, while `count < target` cannot.
