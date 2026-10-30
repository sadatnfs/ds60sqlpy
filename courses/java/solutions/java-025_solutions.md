# java-025: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

The JVM manages heap memory through reachability,not by immediately freeing an object when a local variable changes. References in collections,static fields,thread locals or listeners can keep objects alive after a caller no longer needs them. Stack frames hold local execution state and references,while objects and arrays generally live in managed heap storage. An unreachable object becomes eligible for collection,but collection timing is not a deterministic application contract.

System.gc is a request rather than proof that a particular object was reclaimed. Memory counters are observations affected by allocation,collection and implementation details. This lesson uses bounded arrays and explicit ownership changes to explain retention without allocating until failure or relying on a forced collection. Weak references can observe optional reachability,but application correctness should not depend on when a weakly reachable object disappears.

**Reachability:** Whether an object can be reached through active reference paths.

**Retention:** Keeping an object alive through a reference that still exists.

**Garbage collection:** Reclaiming managed memory according to runtime policy.

**Allocation rate:** The amount of new storage created over a period of work.

## Reading the reference

A collection holding an array retains a strong reference. Clearing the collection removes that particular ownership path,but other references may remain. WeakReference.get may return the referent or null depending on reachability and collection. Runtime memory values describe the current process and should not be treated as exact per-object size measurements. Avoid finalizers as a resource-lifetime mechanism;use explicit close for files,sockets and executors.

## Exercise 1: Expose a strong retention path

Task: Store a small byte array in a list and drop the local variable reference.

The local reference disappearing does not remove the list's ownership path. This is a common source of unbounded cache or listener retention.

```java
List<byte[]> retained = new ArrayList<>();
byte[] payload = new byte[1024];
payload[0] = 7;
retained.add(payload);
payload = null;
assert retained.get(0)[0] == 7 && retained.get(0).length == 1024;
```

**Expected:** list still exposes the same array contents.

**Verify:** Compare the program values or named exception with list still exposes the same array contents. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Remove one ownership path deliberately

Task: Keep a separate reference,clear the list,and inspect the separate reference.

Clearing a container removes its references,but another strong reference can keep the object reachable. Reachability is a graph property.

```java
byte[] separate = retained.get(0);
retained.clear();
assert retained.isEmpty() && separate[0] == 7;
```

**Expected:** list empty;separate array still valid.

**Verify:** Compare the program values or named exception with list empty;separate array still valid. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Inspect a weak reference without timing assumptions

Task: Create a WeakReference to the still-strongly-referenced array.

The reachability fence makes the intended lifetime explicit for this observation. The exercise does not assert when collection occurs after strong references disappear.

```java
var weak = new java.lang.ref.WeakReference<>(separate);
assert weak.get() == separate;
java.lang.ref.Reference.reachabilityFence(separate);
```

**Expected:** weakget returns the same object while strong reference exists.

**Verify:** Compare the program values or named exception with weakget returns the same object while strong reference exists. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Separate value size from allocation count

Task: Create ten arrays of 128 bytes and count logical payload bytes.

Array headers,alignment,references and container overhead are additional. Logical payload arithmetic is not a measured object-layout receipt.

```java
List<byte[]> blocks = new ArrayList<>();
for (int i = 0; i < 10; i++) blocks.add(new byte[128]);
int logical = blocks
  .stream()
  .mapToInt(block -> block.length)
  .sum();
assert logical == 1280;
```

**Expected:** 1280 logical bytes;no exact heap-overhead claim.

**Verify:** Compare the program values or named exception with 1280 logical bytes;no exact heap-overhead claim. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Reuse a bounded working buffer

Task: Fill one array repeatedly rather than retaining every intermediate array.

Reuse can reduce allocations when ownership permits mutation. It can also create aliasing bugs if callers expect historical snapshots,so the contract matters.

```java
byte[] buffer = new byte[16];
int identity = System.identityHashCode(buffer);
for (int i = 0; i < 10; i++) Arrays.fill(buffer, (byte) i);
assert System.identityHashCode(buffer) == identity && buffer[0] == 9;
```

**Expected:** same buffer identity;final value9.

**Verify:** Compare the program values or named exception with same buffer identity;final value9. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Record process memory cautiously

Task: ReadRuntime total/free/max memory and check only valid ordering relationships.

Counters can change between reads and include runtime behavior outside this fixture. Profiling and controlled measurement are needed for a memory diagnosis.

```java
Runtime runtime = Runtime.getRuntime();
long total = runtime.totalMemory(),
  free = runtime.freeMemory(),
  maximum = runtime.maxMemory();
assert total >= 0 && free >= 0 && maximum >= total;
```

**Expected:** nonnegative counters; max at least total; no claim of exact object size.

**Verify:** Compare the program values or named exception with nonnegative counters; max at least total; no claim of exact object size. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
