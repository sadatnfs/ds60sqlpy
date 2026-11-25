# java-023: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

Synchronization protects a state transition, not merely a variable name. A synchronized block uses a monitor and provides mutual exclusion plus visibility when all participants follow the same locking policy. AtomicInteger supports individual atomic operations such as increment and compare-and-set. ConcurrentHashMap provides thread-safe operations, but a separate get followed by put is still a compound sequence unless a method such as compute or merge makes it atomic for a key.

Locks also create lifetime and ordering obligations. Always release an explicit lock in finally. Acquiring multiple locks in inconsistent order can deadlock; using one global order removes that cycle for the declared lock set. A timed tryLock can make contention a bounded outcome rather than an indefinite wait. This lesson tests exact counts and controlled contention, not a universal concurrency performance claim.

**Critical section:** The state transition protected by one mutual-exclusion policy.

**Compare-and-set:** An atomic conditional update based on an expected current value.

**Lock ordering:** A consistent acquisition order preventing a declared class of cycles.

## Reading the reference

Use synchronized around the entire read-modify-write. AtomicInteger.incrementAndGet performs one atomic increment. compareAndSet succeeds only when the current value matches the expected value. ConcurrentHashMap.merge combines updates atomically for a key. ReentrantLock.tryLock(timeout, unit) returns false on bounded contention; unlock belongs in finally after a successful acquisition.

## Exercise 1: Protect a compound counter: change one input

Task: Change `for (int i = 0; i < 1000; i++) counter.increment();` to `for (int i = 1; i < 1000; i++) counter.increment();` in Example A and predict which assertion fails and why.

The lock covers the complete increment. Synchronizing only a read or only a write would still permit lost updates.

The unchanged code is the part that Example A adds:

```java
Counter counter = new Counter();
runTwo(() -> {
  for (int i = 0; i < 1000; i++) counter.increment();
});
assert counter.value() == 2000;
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `counter.value() == 2000`.

**Verify:** Name the value that makes `counter.value() == 2000` false, then restore the line.

## Exercise 2: Use an atomic increment: debug a regression

Task: A regression in Example B's new code makes one line read `for (int i = 0; i <= 1000; i++) atomic.incrementAndGet();`. Repair it using the failing assertion.

The atomic operation matches this simple counter contract. More complex multi-field invariants may still require a larger critical section.

The unchanged code is the part that Example B adds:

```java
var atomic = new java.util.concurrent.atomic.AtomicInteger();
runTwo(() -> {
  for (int i = 0; i < 1000; i++) atomic.incrementAndGet();
});
assert atomic.get() == 2000;
```

**Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `atomic.get() == 2000`; the repaired line reads `for (int i = 0; i < 1000; i++) atomic.incrementAndGet();`.

**Verify:** Explain how the changed token alters the value that `atomic.get() == 2000` tests.

## Exercise 3: Inspect compare-and-set

Task: Change 0 to 1 with CAS, then retry expecting 0.

CAS reports whether its expected-state condition held. A failed attempt must be handled according to the algorithm rather than assumed to have updated.

```java
var state = new java.util.concurrent.atomic.AtomicInteger();
boolean firstSwap = state.compareAndSet(0, 1);
boolean staleSwap = state.compareAndSet(0, 2);
assert firstSwap && !staleSwap && state.get() == 1;
```

**Expected:** first true; second false; value 1.

**Verify:** Control: changing `boolean firstSwap = state.compareAndSet(0, 1);` to `boolean firstSwap = state.compareAndSet(1, 1);` must fail the assertion on `firstSwap && !staleSwap && state.get() == 1`.

## Exercise 4: Combine map updates atomically

Task: Use ConcurrentHashMap.merge for 2000 total increments ofkeyx.

The map operation covers the per-key combination. Thread safety of the container would not make an arbitrary get-plus-put sequence atomic.

```java
var counts = new java.util.concurrent.ConcurrentHashMap<String, Integer>();
runTwo(() -> {
  for (int i = 0; i < 1000; i++) counts.merge("x", 1, Integer::sum);
});
assert counts.get("x") == 2000;
```

**Expected:** stored count 2000.

**Verify:** Control: changing `for (int i = 0; i < 1000; i++) counts.merge("x", 1, Integer::sum);` to `for (int i = 0; i <= 1000; i++) counts.merge("x", 1, Integer::sum);` must fail the assertion on `counts.get("x") == 2000`.

## Exercise 5: Bound lock contention

Task: Hold a ReentrantLock in the caller while a worker tries to acquire it with a short timeout.

The owner deliberately retains the lock until the timed attempt ends. The result is a controlled contention outcome, not a race-dependent timing guess.

```java
var lock = new java.util.concurrent.locks.ReentrantLock();
var acquired = new java.util.concurrent.atomic.AtomicBoolean(true);
lock.lock();
try {
  Thread contender = Thread.ofPlatform().start(() -> {
    try {
      boolean ok = lock.tryLock(50, java.util.concurrent.TimeUnit.MILLISECONDS);
      acquired.set(ok);
      if (ok) lock.unlock();
    } catch (InterruptedException error) {
      Thread.currentThread().interrupt();
    }
  });
  join(contender);
  assert !acquired.get();
} finally {
  lock.unlock();
}
assert !lock.isLocked();
```

**Expected:** worker returns false; lock released in finally.

**Verify:** Control: changing `assert !lock.isLocked();` to `assert lock.isLocked();` inside the assertion must make it fail.

## Exercise 6: Use one global order for two locks

Task: Have both workers acquire first then second before incrementing shared state.

The same acquisition order removes the opposite-order cycle for these two locks. It does not prove that a larger program has no other lock or resource cycles.

```java
Object first = new Object(),
  second = new Object();
int[] total = { 0 };
runTwo(() -> {
  for (int i = 0; i < 1000; i++) {
    synchronized (first) {
      synchronized (second) {
        total[0]++;
      }
    }
  }
});
assert total[0] == 2000;
```

**Expected:** 2000 increments and no blocked worker after bounded joins.

**Verify:** Control: changing `for (int i = 0; i < 1000; i++) {` to `for (int i = 0; i <= 1000; i++) {` must fail the assertion on `total[0] == 2000`.

## After comparing the answer

Rewrite Exercise 4 in your copy as `get` followed by `put` on the same `ConcurrentHashMap` and run it a few times; a total below 2,000 shows the lost update that `merge` prevents.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
