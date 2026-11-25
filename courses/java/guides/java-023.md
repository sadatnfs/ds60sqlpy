# java-023: Locks, atomics and concurrent collections

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-022`

## Learning objectives

Protect shared state with locks, atomics and concurrent maps, and avoid deadlock with a single lock order.

The six exercises practice these steps:

- Protect a compound counter.
- Use an atomic increment.
- Inspect compare-and-set.
- Combine map updates atomically.
- Bound lock contention.
- Use one global order for two locks.

## Purpose and mental model

Synchronization protects a state transition, not merely a variable name. A synchronized block uses a monitor and provides mutual exclusion plus visibility when all participants follow the same locking policy. AtomicInteger supports individual atomic operations such as increment and compare-and-set. ConcurrentHashMap provides thread-safe operations, but a separate get followed by put is still a compound sequence unless a method such as compute or merge makes it atomic for a key.

Locks also create lifetime and ordering obligations. Always release an explicit lock in finally. Acquiring multiple locks in inconsistent order can deadlock; using one global order removes that cycle for the declared lock set. A timed tryLock can make contention a bounded outcome rather than an indefinite wait. This lesson tests exact counts and controlled contention, not a universal concurrency performance claim.

## Vocabulary and concepts

**Critical section:** The state transition protected by one mutual-exclusion policy.

**Compare-and-set:** An atomic conditional update based on an expected current value.

**Lock ordering:** A consistent acquisition order preventing a declared class of cycles.

## How to run this lesson

`runTwo` starts two platform workers on the same action and joins each with a bound, rethrowing any worker failure, so a broken increment shows up as a wrong total rather than a silent thread death.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

Use synchronized around the entire read-modify-write. AtomicInteger.incrementAndGet performs one atomic increment. compareAndSet succeeds only when the current value matches the expected value. ConcurrentHashMap.merge combines updates atomically for a key. ReentrantLock.tryLock(timeout, unit) returns false on bounded contention; unlock belongs in finally after a successful acquisition.

## Worked example / walkthrough

### Example A: Protect a compound counter

The lock covers the complete increment. Synchronizing only a read or only a write would still permit lost updates.

```java
import java.util.*;

public class Main {

  static final class Counter {

    private int value;

    synchronized void increment() {
      value++;
    }

    synchronized int value() {
      return value;
    }
  }

  static void join(Thread thread) throws InterruptedException {
    thread.join(2500);
    if (thread.isAlive()) {
      thread.interrupt();
      throw new AssertionError("worker did not stop");
    }
  }

  static void runTwo(Runnable action) throws Exception {
    var failure = new java.util.concurrent.atomic.AtomicReference<Throwable>();
    Runnable checked = () -> {
      try {
        action.run();
      } catch (Throwable error) {
        failure.set(error);
      }
    };
    Thread a = Thread.ofPlatform().start(checked),
      b = Thread.ofPlatform().start(checked);
    join(a);
    join(b);
    if (failure.get() != null) throw new AssertionError("worker failed", failure.get());
  }

  public static void main(String[] args) throws Exception {
    Counter counter = new Counter();
    runTwo(() -> {
      for (int i = 0; i < 1000; i++) counter.increment();
    });
    assert counter.value() == 2000;
  }
}
```

**Expected:** counter 2000.

### Example B: Use an atomic increment

The atomic operation matches this simple counter contract. More complex multi-field invariants may still require a larger critical section.

```java
import java.util.*;

public class Main {

  static final class Counter {

    private int value;

    synchronized void increment() {
      value++;
    }

    synchronized int value() {
      return value;
    }
  }

  static void join(Thread thread) throws InterruptedException {
    thread.join(2500);
    if (thread.isAlive()) {
      thread.interrupt();
      throw new AssertionError("worker did not stop");
    }
  }

  static void runTwo(Runnable action) throws Exception {
    var failure = new java.util.concurrent.atomic.AtomicReference<Throwable>();
    Runnable checked = () -> {
      try {
        action.run();
      } catch (Throwable error) {
        failure.set(error);
      }
    };
    Thread a = Thread.ofPlatform().start(checked),
      b = Thread.ofPlatform().start(checked);
    join(a);
    join(b);
    if (failure.get() != null) throw new AssertionError("worker failed", failure.get());
  }

  public static void main(String[] args) throws Exception {
    Counter counter = new Counter();
    runTwo(() -> {
      for (int i = 0; i < 1000; i++) counter.increment();
    });
    assert counter.value() == 2000;

    var atomic = new java.util.concurrent.atomic.AtomicInteger();
    runTwo(() -> {
      for (int i = 0; i < 1000; i++) atomic.incrementAndGet();
    });
    assert atomic.get() == 2000;
  }
}
```

**Expected:** value 2000.

## Prediction before your attempt

Before running Example A, decide whether two workers each calling a `synchronized` `increment` 1,000 times can ever finish below 2,000. For Example B, predict the same total with `AtomicInteger.incrementAndGet()` and no lock. Before Exercise 3, predict the return values of `compareAndSet(0, 1)` called twice on a fresh `AtomicInteger`, and the final value.

## Exercises

1. **Protect a compound counter: change one input.** Change `for (int i = 0; i < 1000; i++) counter.increment();` to `for (int i = 1; i < 1000; i++) counter.increment();` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `counter.value() == 2000`.
   **Verify:** Name the value that makes `counter.value() == 2000` false, then restore the line.

2. **Use an atomic increment: debug a regression.** A regression in Example B's new code makes one line read `for (int i = 0; i <= 1000; i++) atomic.incrementAndGet();`. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `atomic.get() == 2000`; the repaired line reads `for (int i = 0; i < 1000; i++) atomic.incrementAndGet();`.
   **Verify:** Explain how the changed token alters the value that `atomic.get() == 2000` tests.

3. **Inspect compare-and-set.** Change 0 to 1 with CAS, then retry expecting 0.
   **Expected:** first true; second false; value 1.
   **Verify:** Control: changing `boolean firstSwap = state.compareAndSet(0, 1);` to `boolean firstSwap = state.compareAndSet(1, 1);` must fail the assertion on `firstSwap && !staleSwap && state.get() == 1`.

4. **Combine map updates atomically.** Use ConcurrentHashMap.merge for 2000 total increments ofkeyx.
   **Expected:** stored count 2000.
   **Verify:** Control: changing `for (int i = 0; i < 1000; i++) counts.merge("x", 1, Integer::sum);` to `for (int i = 0; i <= 1000; i++) counts.merge("x", 1, Integer::sum);` must fail the assertion on `counts.get("x") == 2000`.

5. **Bound lock contention.** Hold a ReentrantLock in the caller while a worker tries to acquire it with a short timeout.
   **Expected:** worker returns false; lock released in finally.
   **Verify:** Control: changing `assert !lock.isLocked();` to `assert lock.isLocked();` inside the assertion must make it fail.

6. **Use one global order for two locks.** Have both workers acquire first then second before incrementing shared state.
   **Expected:** 2000 increments and no blocked worker after bounded joins.
   **Verify:** Control: changing `for (int i = 0; i < 1000; i++) {` to `for (int i = 0; i <= 1000; i++) {` must fail the assertion on `total[0] == 2000`.

## Common pitfalls and diagnosis

Thread-safe parts do not make a thread-safe whole: `ConcurrentHashMap.get` followed by `put` can still lose an update, which is why `merge` and `compute` exist. Synchronizing the write but not the read gives stale reads. An explicit `lock()` without `unlock()` in `finally` leaks the lock on the first exception. Two locks taken in opposite orders by two threads can deadlock even though each block looks correct. And a failed `compareAndSet` changed nothing, so it must be retried or reported, never ignored.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the edit starts the loop at 1, so each worker performs 999 increments. Then add the two workers' contributions. Finally, compare 1,998 with the expected 2,000 and explain why the synchronized counter itself is still correct.
- **Exercise 2:** First note that the edit uses `i <= 1000`, so each worker runs 1,001 times. Then compute the total the atomic counter reports. Finally, compare 2,002 with 2,000 and decide whether atomicity or the loop bound is wrong.
- **Exercise 3:** First call `compareAndSet(0, 1)` on an `AtomicInteger` holding 0 and keep the result. Then call `compareAndSet(0, 1)` again with the now stale expectation. Finally, assert true, false and a final value of 1.
- **Exercise 4:** First give each worker a loop of 1,000 calls to `counts.merge("x", 1, Integer::sum)`. Then run the loop on two workers with `runTwo`. Finally, assert that the stored count is 2,000 and explain why `merge` is atomic per key.
- **Exercise 5:** First lock a `ReentrantLock` in the caller and start a contender that calls `tryLock(50, MILLISECONDS)`. Then join the contender and assert that it failed to acquire. Finally, unlock in a `finally` block and assert that the lock is free.
- **Exercise 6:** First let both workers take `first` and then `second` in nested `synchronized` blocks. Then increment the shared total inside the inner block 1,000 times per worker. Finally, assert 2,000 and explain which opposite order would create a deadlock cycle.

## Self-check and retrieval

Without the guide, explain why `count++` is three steps and how a monitor, an atomic and `merge` each make it safe. State what `compareAndSet` returns when the expected value is stale, why `tryLock` with a timeout bounds contention, and what single rule prevents the two-lock deadlock.

## Next step

Continue with `java-024`: Virtual threads and blocking work. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/AtomicInteger.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-023: Locks, atomics and concurrent collections.
Read courses/java/guides/java-023.md and courses/java/lessons/java-023.java. Direct prerequisites: `java-022`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
