# c-037: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

A mutex protects shared state only when every relevant reader and writer follows the same locking protocol. A condition variable lets a thread wait for a state predicate to become true while releasing the mutex atomically during the wait. Notifications are not stored as durable messages, and waking does not prove the predicate is true. Always recheck it in a loop to handle spurious wakeups and other consumers. Change the predicate under the same mutex used by waiters. Keep lock ownership and destruction explicit, and do not destroy a mutex or condition variable while another thread can still use it.

pthread_mutex_lock and unlock delimit the protected region. pthread_cond_wait expects the mutex to be locked, releases it while waiting, and reacquires it before returning. while(!ready) wait is the correct shape for this fixture. Signal after updating the protected state. Join the worker before destroying synchronization objects. A sleep cannot replace the predicate protocol.

## Exercise 1: Protect a shared count: predict an edited check

Copy worked example 1 into a scratch pad and change `CHECK(locked_total(4, 100) == 400);` to `CHECK(locked_total(5, 100) == 400);` inside its CHECK. Before running, predict whether the CHECK still holds and explain why; then restore it.

The unchanged code is worked example 1:

```c
CHECK(locked_total(4, 100) == 400);
```

**Expected:** The changed run stops with `Check failed` at the CHECK on `locked_total(4, 100) == 400`. Restoring the original line brings back the worked observation: the final count is 400.

Every increment is inside the same critical section, and the parent joins all writers before reading the final value.

## Exercise 2: Handle one worker: diagnose an edited check

A careless edit changed the CHECK in worked example 2 so that it reads `CHECK(locked_total(2, 7) == 7);`. Run worked example 2 with that line, explain why the edited CHECK now fails for the same program state, and restore it.

The unchanged code is worked example 2:

```c
CHECK(locked_total(1, 7) == 7);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `locked_total(1, 7) == 7`; after it the line reads `CHECK(locked_total(1, 7) == 7);` again and the result is 7.

The sequential boundary exercises the same synchronization implementation without depending on contention.

## Exercise 3: Handle zero loop iterations

Run two workers whose increment loops are empty.

```c
CHECK(locked_total(2, 0) == 0);
```

**Expected:** The result remains zero.

Worker creation and cleanup still occur even though the protected state never changes.

## Exercise 4: Wait for a predicate

Wait until a worker publishes ready with value 42.

```c
CHECK(wait_for_value() == 42);
```

**Expected:** The parent observes value 42.

The while loop checks actual state after every wakeup. The signal itself is not treated as the result payload.

## Exercise 5: Repeat independent synchronization

Create and destroy the predicate fixture twice.

```c
CHECK(wait_for_value() == 42 && wait_for_value() == 42);
```

**Expected:** Both operations return 42.

Each invocation owns fresh synchronization objects and joins before destruction, avoiding cross-run state leakage.

## Exercise 6: Transfer count invariance

Compare two workers times five increments with five workers times two.

```c
CHECK(locked_total(2, 5) == 10 && locked_total(5, 2) == 10);
```

**Expected:** Both totals are 10.

Scheduling changes but the protected update count remains invariant. This is correctness evidence, not a performance comparison.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
