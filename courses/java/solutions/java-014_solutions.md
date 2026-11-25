# java-014: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

A stream is a single-use computation pipeline over a source. Intermediate operations such as filter and map are lazy: defining them does not necessarily process elements. A terminal operation such as collect or sum triggers the computation. The pipeline describes transformations, not a mutable container. Reduction requires an identity and an associative combination rule if it is to behave predictably under partitioning. Side effects in stream operations can make execution order and parallel behavior difficult to reason about. Prefer collectors and pure mappings over appending to a shared list from a parallel forEach.

**Lazy pipeline:** A computation whose intermediate stages wait for a terminal operation.

**Terminal operation:** An operation that consumes a stream and produces a result or action.

**Associative reduction:** A combination rule unaffected by regrouping operands.

## Reading the reference

stream() creates a pipeline, filter keeps matching elements, and mapToInt selects a primitive numeric stream. sum is a terminal reduction with identity 0. groupingBy collects rows into groups; counting or summingInt defines the group aggregate. A stream cannot be reused after a terminal operation. In a parallel reduction, the identity must be neutral for every partition, and subtraction is not associative.

## Exercise 1: Filter and sum: change one input

Task: Change `int total = List.of(1, 2, 3, 4)` to `int total = List.of(2, 2, 3, 4)` in Example A and predict which assertion fails and why.

The pipeline preserves the order of conceptual operations: selection happens before squaring and reduction. The result is a scalar rather than a modified source list.

The unchanged code is the part that Example A adds:

```java
int total = List.of(1, 2, 3, 4)
  .stream()
  .filter(value -> value % 2 == 0)
  .mapToInt(value -> value * value)
  .sum();
assert total == 20;
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `total == 20`.

**Verify:** Name the value that makes `total == 20` false, then restore the line.

## Exercise 2: Observe laziness with an explicit terminal: debug a regression

Task: A regression in Example B's new code makes one line read `return value + 2;`. Repair it using the failing assertion.

The counter is a teaching probe, not a recommended business side effect. toList requires mapped values, while some terminals may optimize away unnecessary stages.

The unchanged code is the part that Example B adds:

```java
var calls = new java.util.concurrent.atomic.AtomicInteger();
var pipeline = List.of(1, 2, 3)
  .stream()
  .map(value -> {
    calls.incrementAndGet();
    return value * 2;
  });
assert calls.get() == 0;
assert pipeline.toList().equals(List.of(2, 4, 6)) && calls.get() == 3;
```

**Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `pipeline.toList().equals(List.of(2, 4, 6)) && calls.get() == 3`; the repaired line reads `return value * 2;`.

**Verify:** Explain how the changed token alters the value that `pipeline.toList().equals(List.of(2, 4, 6)) && calls.get() == 3` tests.

## Exercise 3: Group with a collector

Task: Count red, blue, red with groupingBy and counting.

The collector owns accumulation rather than relying on shared external mutation. The map ordering is unspecified unless a specific ordered map supplier is chosen.

```java
Map<String, Long> counts = List.of("red", "blue", "red")
  .stream()
  .collect(
    java.util.stream.Collectors.groupingBy(
      value -> value,
      java.util.stream.Collectors.counting()
    )
  );
assert counts.equals(Map.of("red", 2L, "blue", 1L));
```

**Expected:** red 2L, blue 1L.

**Verify:** Control: changing `Map<String, Long> counts = List.of("red", "blue", "red")` to `Map<String, Long> counts = List.of("red!", "blue", "red")` must fail the assertion on `counts.equals(Map.of("red", 2L, "blue", 1L))`.

## Exercise 4: Reject stream reuse

Task: Consume a stream once, then attempt another terminal operation.

A stream represents one traversal. Create a new stream from the source when another computation is required.

```java
var once = List.of(1, 2).stream();
long counted = once.count();
assert counted == 2;
boolean reused = false;
try {
  once.toList();
} catch (IllegalStateException expected) {
  reused = true;
}
assert reused;
```

**Expected:** IllegalStateException.

**Verify:** Control: changing `reused = true;` to `reused = false;` must fail the assertion on `reused`.

## Exercise 5: Check the reduction identity

Task: Compare sum reduction with identity 0 against a deliberately wrong identity 10.

An identity is not an arbitrary initial offset when parallel partitions may each receive it. The neutral value for addition is 0.

```java
int correct = List.of(1, 2, 3).stream().reduce(0, Integer::sum);
int wrong = List.of(1, 2, 3).stream().reduce(10, Integer::sum);
assert correct == 6 && wrong == 16;
```

**Expected:** correct 6; wrong 16 in the sequential fixture.

**Verify:** Control: changing `int correct = List.of(1, 2, 3).stream().reduce(0, Integer::sum);` to `int correct = List.of(2, 2, 3).stream().reduce(0, Integer::sum);` must fail the assertion on `correct == 6 && wrong == 16`.

## Exercise 6: Expose nonassociative subtraction

Task: Compare (10-3)-2 with 10-(3-2), then use an associative sum for a parallel fixture.

Subtraction changes under regrouping, so it is unsuitable as a general parallel reduction operator. Correctness must come before any performance experiment.

```java
assert (10 - 3) - 2 == 5 && 10 - (3 - 2) == 9;
assert java.util.stream.IntStream.rangeClosed(1, 100).parallel().sum() == 5050;
```

**Expected:** 5 versus 9; parallel sum 5050.

**Verify:** Control: changing `assert (10 - 3) - 2 == 5 && 10 - (3 - 2) == 9;` to `assert (10 + 3) - 2 == 5 && 10 - (3 - 2) == 9;` inside the assertion must make it fail.

## After comparing the answer

Run your reduction from Exercise 5 with the wrong identity on a parallel stream in your copy, and observe that the result can exceed 16 because each partition adds its own 10.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
