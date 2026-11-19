# java-023: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Synchronization protects a state transition, not merely a variable name. A synchronized block uses a monitor and provides mutual exclusion plus visibility when all participants follow the same locking policy. AtomicInteger supports individual atomic operations such as increment and compare-and-set. ConcurrentHashMap provides thread-safe operations, but a separate get followed by put is still a compound sequence unless a method such as compute or merge makes it atomic for a key.

Locks also create lifetime and ordering obligations. Always release an explicit lock in finally. Acquiring multiple locks in inconsistent order can deadlock; using one global order removes that cycle for the declared lock set. A timed tryLock can make contention a bounded outcome rather than an indefinite wait. This lesson tests exact counts and controlled contention, not a universal concurrency performance claim.

**Critical section:** The state transition protected by one mutual-exclusion policy.

**Compare-and-set:** An atomic conditional update based on an expected current value.

**Lock ordering:** A consistent acquisition order preventing a declared class of cycles.

## Reading the reference

Use synchronized around the entire read-modify-write. AtomicInteger.incrementAndGet performs one atomic increment. compareAndSet succeeds only when the current value matches the expected value. ConcurrentHashMap.merge combines updates atomically for a key. ReentrantLock.tryLock(timeout, unit) returns false on bounded contention; unlock belongs in finally after a successful acquisition.

## Exercise 1: Protect a compound counter: change one input

Task: Copy Example A into a scratch `Main.java` and change `for (int i = 0; i < 1000; i++) counter.increment();` to `for (int i = 1; i < 1000; i++) counter.increment();`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.

The lock covers the complete increment. Synchronizing only a read or only a write would still permit lost updates.

The unchanged code is the part that Example A adds:

```java
Counter counter = new Counter();
runTwo(() -> {
  for (int i = 0; i < 1000; i++) counter.increment();
});
assert counter.value() == 2000;
```

**Expected:** The changed run fails with an `AssertionError` from the assertion on `counter.value() == 2000`. Restoring the original line brings back the worked observation: counter 2000.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `counter.value() == 2000` false. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Use an atomic increment: debug a regression

Task: A regression changed one token in the code that Example B adds after Example A, so one line now reads `for (int i = 0; i <= 1000; i++) atomic.incrementAndGet();`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.

The atomic operation matches this simple counter contract. More complex multi-field invariants may still require a larger critical section.

The unchanged code is the part that Example B adds:

```java
var atomic = new java.util.concurrent.atomic.AtomicInteger();
runTwo(() -> {
  for (int i = 0; i < 1000; i++) atomic.incrementAndGet();
});
assert atomic.get() == 2000;
```

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `atomic.get() == 2000`; after it the line reads `for (int i = 0; i < 1000; i++) atomic.incrementAndGet();` again and value 2000.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `atomic.get() == 2000` for this input.

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

**Verify:** Keep an assertion equivalent to `firstSwap && !staleSwap && state.get() == 1`. As a control, change `boolean firstSwap = state.compareAndSet(0, 1);` to `boolean firstSwap = state.compareAndSet(1, 1);`: the run must fail with an `AssertionError` from the assertion on `firstSwap && !staleSwap && state.get() == 1`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `counts.get("x") == 2000`. As a control, change `for (int i = 0; i < 1000; i++) counts.merge("x", 1, Integer::sum);` to `for (int i = 0; i <= 1000; i++) counts.merge("x", 1, Integer::sum);`: the run must fail with an `AssertionError` from the assertion on `counts.get("x") == 2000`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `!lock.isLocked()`. As a control, change `assert !lock.isLocked();` to `assert lock.isLocked();` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

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

**Verify:** Keep an assertion equivalent to `total[0] == 2000`. As a control, change `for (int i = 0; i < 1000; i++) {` to `for (int i = 0; i <= 1000; i++) {`: the run must fail with an `AssertionError` from the assertion on `total[0] == 2000`. Restore the line before continuing.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
