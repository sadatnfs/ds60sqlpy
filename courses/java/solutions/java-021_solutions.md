# java-021: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Threads can execute concurrently while sharing memory. Correct communication requires a happens-before relationship, not an assumption that another thread has probably finished. Starting a thread publishes prior actions to it, and a successful join makes its completed actions visible to the joining thread. Volatile writes and reads establish a publication relationship for associated state, but volatile does not make a compound read-modify-write atomic. A counter increment reads, adds and writes, so two threads can lose an update even if each individual access is visible.

This lesson uses bounded joins, latches and a barrier to make ordering deliberate. A controlled lost-update fixture forces both workers to read the same starting value before either writes. That demonstrates the mechanism without hoping a random stress run happens to fail. Interruption is a cooperative request, not forcible termination; blocking code should respond or preserve the interrupt status when it cannot complete its work.

**Happens-before:** A memory-ordering relationship guaranteeing visibility of earlier actions.

**Atomic operation:** An operation that cannot be observed as separate interleaved steps.

**Interruption:** A cooperative signal requesting that a thread stop or change its work.

## Reading the reference

Thread.start begins a new execution; calling run directly is an ordinary method call. join(timeout) waits only up to a bound, so check isAlive afterward. CountDownLatch coordinates a one-time event, and CyclicBarrier can align two reads before their writes. A volatile ready flag can publish a preceding data assignment. InterruptedException clears the interrupted status, so a handler that propagates cancellation through state should restore it with interrupt().

## Exercise 1: Publish a result through join: change one input

Task: Copy Example A into a scratch `Main.java` and change `Thread worker = Thread.ofPlatform().start(() -> result[0] = 42);` to `Thread worker = Thread.ofPlatform().start(() -> result[1] = 42);`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.

The join establishes the required visibility after completion. A timed sleep would not provide the same guarantee.

The unchanged code is the part that Example A adds:

```java
int[] result = { 0 };
Thread worker = Thread.ofPlatform().start(() -> result[0] = 42);
joinBounded(worker);
assert result[0] == 42;
```

**Expected:** The changed run fails with an `AssertionError` from the assertion on `result[0] == 42`. Restoring the original line brings back the worked observation: worker terminated; result 42.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `result[0] == 42` false. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Publish initial state through start: debug a regression

Task: A regression changed one token in the code that Example B adds after Example A, so one line now reads `int[] input = { 8 };`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.

Actions before start happen-before actions in the started thread. The fixture does not rely on the worker noticing an unsynchronized later mutation.

The unchanged code is the part that Example B adds:

```java
int[] input = { 7 };
var observed = new java.util.concurrent.atomic.AtomicInteger();
Thread reader = Thread.ofPlatform().start(() -> observed.set(input[0]));
joinBounded(reader);
assert observed.get() == 7;
```

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `observed.get() == 7`; after it the line reads `int[] input = { 7 };` again and worker observes 7.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `observed.get() == 7` for this input.

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

**Verify:** Keep an assertion equivalent to `failure.get() == null && counter[0] == 1`. As a control, change `counter[0] = saved + 1;` to `counter[0] = saved - 1;`: the run must fail with an `AssertionError` from the assertion on `failure.get() == null && counter[0] == 1`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `seen.get() == 99`. As a control, change `long deadline = System.nanoTime() + 2_000_000_000L;` to `long deadline = System.nanoTime() - 2_000_000_000L;`: the run must fail with an `AssertionError` from the assertion on `seen.get() == 99`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `identity.get() == caller`. As a control, change `assert identity.get() == caller;` to `assert identity.get() != caller;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

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

**Verify:** Keep an assertion equivalent to `interrupted.get()` and confirm that `java -ea Main` completes. Then name an input that would make it fail and explain which value changes.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
