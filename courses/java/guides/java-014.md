# java-014: Streams and collectors

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-013`

## Learning objectives

Build stream pipelines with collectors, explain laziness and single use, and choose a reduction identity that is safe.

The six exercises practice these steps:

- Filter and sum.
- Observe laziness with an explicit terminal.
- Group with a collector.
- Reject stream reuse.
- Check the reduction identity.
- Expose nonassociative subtraction.

## Purpose and mental model

A stream is a single-use computation pipeline over a source. Intermediate operations such as filter and map are lazy: defining them does not necessarily process elements. A terminal operation such as collect or sum triggers the computation. The pipeline describes transformations, not a mutable container. Reduction requires an identity and an associative combination rule if it is to behave predictably under partitioning. Side effects in stream operations can make execution order and parallel behavior difficult to reason about. Prefer collectors and pure mappings over appending to a shared list from a parallel forEach.

## Vocabulary and concepts

**Lazy pipeline:** A computation whose intermediate stages wait for a terminal operation.

**Terminal operation:** An operation that consumes a stream and produces a result or action.

**Associative reduction:** A combination rule unaffected by regrouping operands.

## How to run this lesson

Exercise 2 counts mapper calls with an `AtomicInteger` purely as a teaching probe; the remaining checks are pure pipelines, and Exercise 6 runs one parallel sum, which returns the same total on any machine.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

stream() creates a pipeline, filter keeps matching elements, and mapToInt selects a primitive numeric stream. sum is a terminal reduction with identity 0. groupingBy collects rows into groups; counting or summingInt defines the group aggregate. A stream cannot be reused after a terminal operation. In a parallel reduction, the identity must be neutral for every partition, and subtraction is not associative.

## Worked example / walkthrough

### Example A: Filter and sum

The pipeline preserves the order of conceptual operations: selection happens before squaring and reduction. The result is a scalar rather than a modified source list.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    int total = List.of(1, 2, 3, 4)
      .stream()
      .filter(value -> value % 2 == 0)
      .mapToInt(value -> value * value)
      .sum();
    assert total == 20;
  }
}
```

**Expected:** 20.

### Example B: Observe laziness with an explicit terminal

The counter is a teaching probe, not a recommended business side effect. toList requires mapped values, while some terminals may optimize away unnecessary stages.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    int total = List.of(1, 2, 3, 4)
      .stream()
      .filter(value -> value % 2 == 0)
      .mapToInt(value -> value * value)
      .sum();
    assert total == 20;

    var calls = new java.util.concurrent.atomic.AtomicInteger();
    var pipeline = List.of(1, 2, 3)
      .stream()
      .map(value -> {
        calls.incrementAndGet();
        return value * 2;
      });
    assert calls.get() == 0;
    assert pipeline.toList().equals(List.of(2, 4, 6)) && calls.get() == 3;
  }
}
```

**Expected:** counter 0 before terminal and 3 after.

## Prediction before your attempt

Before running Example A, list the elements that survive the even filter, their squares and the final sum. For Example B, predict the counter value right after the pipeline is defined and after `toList()` runs, and explain why defining `map` alone does nothing. Then predict what a second terminal operation on the same stream object does (it throws `IllegalStateException`).

## Exercises

1. **Filter and sum: change one input.** Change `int total = List.of(1, 2, 3, 4)` to `int total = List.of(2, 2, 3, 4)` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `total == 20`.
   **Verify:** Name the value that makes `total == 20` false, then restore the line.

2. **Observe laziness with an explicit terminal: debug a regression.** A regression in Example B's new code makes one line read `return value + 2;`. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `pipeline.toList().equals(List.of(2, 4, 6)) && calls.get() == 3`; the repaired line reads `return value * 2;`.
   **Verify:** Explain how the changed token alters the value that `pipeline.toList().equals(List.of(2, 4, 6)) && calls.get() == 3` tests.

3. **Group with a collector.** Count red, blue, red with groupingBy and counting.
   **Expected:** red 2L, blue 1L.
   **Verify:** Control: changing `Map<String, Long> counts = List.of("red", "blue", "red")` to `Map<String, Long> counts = List.of("red!", "blue", "red")` must fail the assertion on `counts.equals(Map.of("red", 2L, "blue", 1L))`.

4. **Reject stream reuse.** Consume a stream once, then attempt another terminal operation.
   **Expected:** IllegalStateException.
   **Verify:** Control: changing `reused = true;` to `reused = false;` must fail the assertion on `reused`.

5. **Check the reduction identity.** Compare sum reduction with identity 0 against a deliberately wrong identity 10.
   **Expected:** correct 6; wrong 16 in the sequential fixture.
   **Verify:** Control: changing `int correct = List.of(1, 2, 3).stream().reduce(0, Integer::sum);` to `int correct = List.of(2, 2, 3).stream().reduce(0, Integer::sum);` must fail the assertion on `correct == 6 && wrong == 16`.

6. **Expose nonassociative subtraction.** Compare (10-3)-2 with 10-(3-2), then use an associative sum for a parallel fixture.
   **Expected:** 5 versus 9; parallel sum 5050.
   **Verify:** Control: changing `assert (10 - 3) - 2 == 5 && 10 - (3 - 2) == 9;` to `assert (10 + 3) - 2 == 5 && 10 - (3 - 2) == 9;` inside the assertion must make it fail.

## Common pitfalls and diagnosis

Streams are single use, so storing one in a field and consuming it twice fails at run time. Laziness surprises people who put logging or counting inside `map` and see nothing until a terminal operation runs. A wrong reduction identity, such as 10 for addition, is added once per partition in a parallel run, and a nonassociative operator such as subtraction gives results that depend on how the work was split. Prefer `groupingBy` and `counting` over appending to an external list from `forEach`.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First apply the even filter to the edited source 2, 2, 3, 4. Then square the survivors and add them. Finally, compare the sum with 20 and explain which stage of the pipeline the edit affected.
- **Exercise 2:** First write the values the edited mapper produces for 1, 2 and 3. Then compare them with 2, 4, 6 while noting that the call counter still reaches 3. Finally, restore the multiplication and explain why the counter alone could not catch this regression.
- **Exercise 3:** First stream red, blue and red and collect with `Collectors.groupingBy(color -> color, Collectors.counting())`. Then compare the map with red 2L and blue 1L, using `Long` values. Finally, explain why no external map was mutated during the collection.
- **Exercise 4:** First create a stream and consume it with one terminal operation. Then call a second terminal operation on the same object inside a `try` block and catch `IllegalStateException`. Finally, explain why you must create a new stream from the source instead.
- **Exercise 5:** First reduce 1, 2 and 3 with identity 0 and `Integer::sum`. Then reduce the same list with identity 10. Finally, compare 6 and 16 and explain what a parallel run could add for each partition.
- **Exercise 6:** First evaluate `(10 - 3) - 2` and `10 - (3 - 2)` and assert 5 and 9. Then sum 1 to 100 with a parallel `IntStream` and assert 5050. Finally, explain why addition is safe to regroup while subtraction is not.

## Self-check and retrieval

Without notes, explain the difference between an intermediate and a terminal operation, why the counter is 0 before `toList()`, what makes 0 the correct identity for an addition reduction, and why `(10 - 3) - 2` and `10 - (3 - 2)` show that subtraction is unsafe as a parallel reducer.

## Next step

Continue with `java-015`: Dates, time zones and formatting. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/Stream.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-014: Streams and collectors.
Read courses/java/guides/java-014.md and courses/java/lessons/java-014.java. Direct prerequisites: `java-013`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
