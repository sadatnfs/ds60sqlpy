# java-025: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

The JVM manages heap memory through reachability, not by immediately freeing an object when a local variable changes. References in collections, static fields, thread locals or listeners can keep objects alive after a caller no longer needs them. Stack frames hold local execution state and references, while objects and arrays generally live in managed heap storage. An unreachable object becomes eligible for collection, but collection timing is not a deterministic application contract.

System.gc is a request rather than proof that a particular object was reclaimed. Memory counters are observations affected by allocation, collection and implementation details. This lesson uses bounded arrays and explicit ownership changes to explain retention without allocating until failure or relying on a forced collection. Weak references can observe optional reachability, but application correctness should not depend on when a weakly reachable object disappears.

**Reachability:** Whether an object can be reached through active reference paths.

**Retention:** Keeping an object alive through a reference that still exists.

**Garbage collection:** Reclaiming managed memory according to runtime policy.

**Allocation rate:** The amount of new storage created over a period of work.

## Reading the reference

A collection holding an array retains a strong reference. Clearing the collection removes that particular ownership path, but other references may remain. WeakReference.get may return the referent or null depending on reachability and collection. Runtime memory values describe the current process and should not be treated as exact per-object size measurements. Avoid finalizers as a resource-lifetime mechanism; use explicit close for files, sockets and executors.

## Exercise 1: Expose a strong retention path: change one input

Task: Change `byte[] payload = new byte[1024];` to `byte[] payload = new byte[1025];` in Example A and predict which assertion fails and why.

The local reference disappearing does not remove the list's ownership path. This is a common source of unbounded cache or listener retention.

The unchanged code is the part that Example A adds:

```java
List<byte[]> retained = new ArrayList<>();
byte[] payload = new byte[1024];
payload[0] = 7;
retained.add(payload);
payload = null;
assert retained.get(0)[0] == 7 && retained.get(0).length == 1024;
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `retained.get(0)[0] == 7 && retained.get(0).length == 1024`.

**Verify:** Name the value that makes `retained.get(0)[0] == 7 && retained.get(0).length == 1024` false, then restore the line.

## Exercise 2: Remove one ownership path deliberately: diagnose an edited check

Task: Example B's new assertion was edited to `assert retained.isEmpty() && separate[1] == 7;`. Explain why it fails for unchanged state and restore it.

Clearing a container removes its references, but another strong reference can keep the object reachable. Reachability is a graph property.

The unchanged code is the part that Example B adds:

```java
byte[] separate = retained.get(0);
retained.clear();
assert retained.isEmpty() && separate[0] == 7;
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `retained.isEmpty() && separate[0] == 7`; the restored assertion passes.

**Verify:** Explain why the edited assertion rejects the state that `retained.isEmpty() && separate[0] == 7` accepts.

## Exercise 3: Inspect a weak reference without timing assumptions

Task: Create a WeakReference to the still-strongly-referenced array.

The reachability fence makes the intended lifetime explicit for this observation. The exercise does not assert when collection occurs after strong references disappear.

```java
var weak = new java.lang.ref.WeakReference<>(separate);
assert weak.get() == separate;
java.lang.ref.Reference.reachabilityFence(separate);
```

**Expected:** weak get returns the same object while strong reference exists.

**Verify:** Control: changing `assert weak.get() == separate;` to `assert weak.get() != separate;` inside the assertion must make it fail.

## Exercise 4: Separate value size from allocation count

Task: Create ten arrays of 128 bytes and count logical payload bytes.

Array headers, alignment, references and container overhead are additional. Logical payload arithmetic is not a measured object-layout receipt.

```java
List<byte[]> blocks = new ArrayList<>();
for (int i = 0; i < 10; i++) blocks.add(new byte[128]);
int logical = blocks
  .stream()
  .mapToInt(block -> block.length)
  .sum();
assert logical == 1280;
```

**Expected:** 1280 logical bytes; no exact heap-overhead claim.

**Verify:** Control: changing `for (int i = 0; i < 10; i++) blocks.add(new byte[128]);` to `for (int i = 0; i <= 10; i++) blocks.add(new byte[128]);` must fail the assertion on `logical == 1280`.

## Exercise 5: Reuse a bounded working buffer

Task: Fill one array repeatedly rather than retaining every intermediate array.

Reuse can reduce allocations when ownership permits mutation. It can also create aliasing bugs if callers expect historical snapshots, so the contract matters.

```java
byte[] buffer = new byte[16];
int identity = System.identityHashCode(buffer);
for (int i = 0; i < 10; i++) Arrays.fill(buffer, (byte) i);
assert System.identityHashCode(buffer) == identity && buffer[0] == 9;
```

**Expected:** same buffer identity; final value 9.

**Verify:** Control: changing `for (int i = 0; i < 10; i++) Arrays.fill(buffer, (byte) i);` to `for (int i = 0; i <= 10; i++) Arrays.fill(buffer, (byte) i);` must fail the assertion on `System.identityHashCode(buffer) == identity && buffer[0] == 9`.

## Exercise 6: Record process memory cautiously

Task: Read Runtime total/free/max memory and check only valid ordering relationships.

Counters can change between reads and include runtime behavior outside this fixture. Profiling and controlled measurement are needed for a memory diagnosis.

```java
Runtime runtime = Runtime.getRuntime();
long total = runtime.totalMemory(),
  free = runtime.freeMemory(),
  maximum = runtime.maxMemory();
assert total >= 0 && free >= 0 && maximum >= total;
```

**Expected:** nonnegative counters; max at least total; no claim of exact object size.

**Verify:** Name an input that would make `total >= 0 && free >= 0 && maximum >= total` false and the value that changes.

## After comparing the answer

In your copy, put the array from Example A into a `HashMap` stored in a static field and trace the path that keeps it reachable after `main` drops every local reference.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
