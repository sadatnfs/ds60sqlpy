# java-021: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

Threads can execute concurrently while sharing memory. Correct communication requires a happens-before relationship, not an assumption that another thread has probably finished. Starting a thread publishes prior actions to it, and a successful join makes its completed actions visible to the joining thread. Volatile writes and reads establish a publication relationship for associated state, but volatile does not make a compound read-modify-write atomic. A counter increment reads, adds and writes, so two threads can lose an update even if each individual access is visible.

This lesson uses bounded joins, latches and a barrier to make ordering deliberate. A controlled lost-update fixture forces both workers to read the same starting value before either writes. That demonstrates the mechanism without hoping a random stress run happens to fail. Interruption is a cooperative request, not forcible termination; blocking code should respond or preserve the interrupt status when it cannot complete its work.

**Happens-before:** A memory-ordering relationship guaranteeing visibility of earlier actions.

**Atomic operation:** An operation that cannot be observed as separate interleaved steps.

**Interruption:** A cooperative signal requesting that a thread stop or change its work.

## Reading the reference

Thread.start begins a new execution; calling run directly is an ordinary method call. join(timeout) waits only up to a bound, so check isAlive afterward. CountDownLatch coordinates a one-time event, and CyclicBarrier can align two reads before their writes. A volatile ready flag can publish a preceding data assignment. InterruptedException clears the interrupted status, so a handler that propagates cancellation through state should restore it with interrupt().

## Exercise 1: Publish a result through join: change one input

Task: Change `Thread worker = Thread.ofPlatform().start(() -> result[0] = 42);` to `Thread worker = Thread.ofPlatform().start(() -> result[1] = 42);` in Example A and predict which assertion fails and why.

The join establishes the required visibility after completion. A timed sleep would not provide the same guarantee.

The unchanged code is the part that Example A adds:

```java
int[] result = { 0 };
Thread worker = Thread.ofPlatform().start(() -> result[0] = 42);
joinBounded(worker);
assert result[0] == 42;
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `result[0] == 42`.

**Verify:** Name the value that makes `result[0] == 42` false, then restore the line.

## Exercise 2: Publish initial state through start: debug a regression

Task: A regression in Example B's new code makes one line read `int[] input = { 8 };`. Repair it using the failing assertion.

Actions before start happen-before actions in the started thread. The fixture does not rely on the worker noticing an unsynchronized later mutation.

The unchanged code is the part that Example B adds:

```java
int[] input = { 7 };
var observed = new java.util.concurrent.atomic.AtomicInteger();
Thread reader = Thread.ofPlatform().start(() -> observed.set(input[0]));
joinBounded(reader);
assert observed.get() == 7;
```

**Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `observed.get() == 7`; the repaired line reads `int[] input = { 7 };`.

**Verify:** Explain how the changed token alters the value that `observed.get() == 7` tests.

## Exercise 3: Force a lost update

Task: Make two workers read counter 0, wait at a barrier, then each write its saved value plus 1.

Both reads occur before either write, so both workers write 1. Visibility alone cannot make the compound operation atomic.

```java
int[] counter = { 0 };
var barrier = new java.util.concurrent.CyclicBarrier(2);
var failure = new java.util.concurrent.atomic.AtomicReference<Throwable>();
Runnable increment = () -> {
  try {
    int saved = counter[0];
    barrier.await(2, java.util.concurrent.TimeUnit.SECONDS);
    counter[0] = saved + 1;
  } catch (Throwable error) {
    failure.set(error);
  }
};
Thread a = Thread.ofPlatform().start(increment),
  b = Thread.ofPlatform().start(increment);
joinBounded(a);
joinBounded(b);
assert failure.get() == null && counter[0] == 1;
```

**Expected:** final counter 1 despite two increments.

**Verify:** Control: changing `counter[0] = saved + 1;` to `counter[0] = saved - 1;` must fail the assertion on `failure.get() == null && counter[0] == 1`.

## Exercise 4: Use a volatile publication flag

Task: Write data 99 before setting a volatile ready flag; read after observing that flag.

The volatile flag publishes the preceding data write. The deadline makes a failed communication contract visible rather than leaving an infinite spin loop.

```java
Publication publication = new Publication();
var seen = new java.util.concurrent.atomic.AtomicInteger(-1);
Thread consumer = Thread.ofPlatform().start(() -> {
  long deadline = System.nanoTime() + 2_000_000_000L;
  while (!publication.ready && System.nanoTime() < deadline) Thread.onSpinWait();
  if (publication.ready) seen.set(publication.data);
});
Thread producer = Thread.ofPlatform().start(() -> {
  publication.data = 99;
  publication.ready = true;
});
joinBounded(producer);
joinBounded(consumer);
assert seen.get() == 99;
```

**Expected:** reader sees 99 and finishes within the bound.

**Verify:** Control: changing `long deadline = System.nanoTime() + 2_000_000_000L;` to `long deadline = System.nanoTime() - 2_000_000_000L;` must fail the assertion on `seen.get() == 99`.

## Exercise 5: Distinguish run from start

Task: Invoke a Runnable directly and compare its thread identity with the caller.

A Runnable describes work. It does not create concurrency until an executor or started Thread schedules it.

```java
Thread caller = Thread.currentThread();
var identity = new java.util.concurrent.atomic.AtomicReference<Thread>();
Runnable action = () -> identity.set(Thread.currentThread());
action.run();
assert identity.get() == caller;
```

**Expected:** same thread identity for direct run.

**Verify:** Control: changing `assert identity.get() == caller;` to `assert identity.get() != caller;` inside the assertion must make it fail.

## Exercise 6: Respond to interruption

Task: Interrupt a worker waiting on a latch, restore its flag in the catch, and verify termination.

The worker cooperates with cancellation at a blocking point. Ignoring the exception would discard the request and could leave a larger task running unexpectedly.

```java
var started = new java.util.concurrent.CountDownLatch(1);
var waiting = new java.util.concurrent.CountDownLatch(1);
var interrupted = new java.util.concurrent.atomic.AtomicBoolean();
Thread blocked = Thread.ofPlatform().start(() -> {
  started.countDown();
  try {
    waiting.await();
  } catch (InterruptedException expected) {
    Thread.currentThread().interrupt();
    interrupted.set(Thread.currentThread().isInterrupted());
  }
});
boolean blockedStarted = started.await(2, java.util.concurrent.TimeUnit.SECONDS);
assert blockedStarted;
blocked.interrupt();
joinBounded(blocked);
assert interrupted.get();
```

**Expected:** interruption observed and worker terminated.

**Verify:** Name an input that would make `interrupted.get()` false and the value that changes.

## After comparing the answer

Replace the counter in Exercise 3 of your copy with an `AtomicInteger` and `incrementAndGet()`, keep the barrier, and confirm that the final value is 2.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
