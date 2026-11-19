# java-014: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

A stream is a single-use computation pipeline over a source. Intermediate operations such as filter and map are lazy: defining them does not necessarily process elements. A terminal operation such as collect or sum triggers the computation. The pipeline describes transformations, not a mutable container. Reduction requires an identity and an associative combination rule if it is to behave predictably under partitioning. Side effects in stream operations can make execution order and parallel behavior difficult to reason about. Prefer collectors and pure mappings over appending to a shared list from a parallel forEach.

**Lazy pipeline:** A computation whose intermediate stages wait for a terminal operation.

**Terminal operation:** An operation that consumes a stream and produces a result or action.

**Associative reduction:** A combination rule unaffected by regrouping operands.

## Reading the reference

stream() creates a pipeline, filter keeps matching elements, and mapToInt selects a primitive numeric stream. sum is a terminal reduction with identity 0. groupingBy collects rows into groups; counting or summingInt defines the group aggregate. A stream cannot be reused after a terminal operation. In a parallel reduction, the identity must be neutral for every partition, and subtraction is not associative.

## Exercise 1: Filter and sum: change one input

Task: Copy Example A into a scratch `Main.java` and change `int total = List.of(1, 2, 3, 4)` to `int total = List.of(2, 2, 3, 4)`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.

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

**Expected:** The changed run fails with an `AssertionError` from the assertion on `total == 20`. Restoring the original line brings back the worked observation: 20.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `total == 20` false. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Observe laziness with an explicit terminal: debug a regression

Task: A regression changed one token in the code that Example B adds after Example A, so one line now reads `return value + 2;`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.

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

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `pipeline.toList().equals(List.of(2, 4, 6)) && calls.get() == 3`; after it the line reads `return value * 2;` again and counter 0 before terminal and 3 after.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `pipeline.toList().equals(List.of(2, 4, 6)) && calls.get() == 3` for this input.

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

**Verify:** Keep an assertion equivalent to `counts.equals(Map.of("red", 2L, "blue", 1L))`. As a control, change `Map<String, Long> counts = List.of("red", "blue", "red")` to `Map<String, Long> counts = List.of("red!", "blue", "red")`: the run must fail with an `AssertionError` from the assertion on `counts.equals(Map.of("red", 2L, "blue", 1L))`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `reused`. As a control, change `reused = true;` to `reused = false;`: the run must fail with an `AssertionError` from the assertion on `reused`. Restore the line before continuing.

## Exercise 5: Check the reduction identity

Task: Compare sum reduction with identity 0 against a deliberately wrong identity 10.

An identity is not an arbitrary initial offset when parallel partitions may each receive it. The neutral value for addition is 0.

```java
int correct = List.of(1, 2, 3).stream().reduce(0, Integer::sum);
int wrong = List.of(1, 2, 3).stream().reduce(10, Integer::sum);
assert correct == 6 && wrong == 16;
```

**Expected:** correct 6; wrong 16 in the sequential fixture.

**Verify:** Keep an assertion equivalent to `correct == 6 && wrong == 16`. As a control, change `int correct = List.of(1, 2, 3).stream().reduce(0, Integer::sum);` to `int correct = List.of(2, 2, 3).stream().reduce(0, Integer::sum);`: the run must fail with an `AssertionError` from the assertion on `correct == 6 && wrong == 16`. Restore the line before continuing.

## Exercise 6: Expose nonassociative subtraction

Task: Compare (10-3)-2 with 10-(3-2), then use an associative sum for a parallel fixture.

Subtraction changes under regrouping, so it is unsuitable as a general parallel reduction operator. Correctness must come before any performance experiment.

```java
assert (10 - 3) - 2 == 5 && 10 - (3 - 2) == 9;
assert java.util.stream.IntStream.rangeClosed(1, 100).parallel().sum() == 5050;
```

**Expected:** 5 versus 9; parallel sum 5050.

**Verify:** Keep an assertion equivalent to `(10 - 3) - 2 == 5 && 10 - (3 - 2) == 9`. As a control, change `assert (10 - 3) - 2 == 5 && 10 - (3 - 2) == 9;` to `assert (10 + 3) - 2 == 5 && 10 - (3 - 2) == 9;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
