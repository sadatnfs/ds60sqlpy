# java-014: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

A stream is a single-use computation pipeline over a source. Intermediate operations such as filter and map are lazy: defining them does not necessarily process elements. A terminal operation such as collect or sum triggers the computation. The pipeline describes transformations, not a mutable container. Reduction requires an identity and an associative combination rule if it is to behave predictably under partitioning. Side effects in stream operations can make execution order and parallel behavior difficult to reason about. Prefer collectors and pure mappings over appending to a shared list from a parallelforEach.

**Lazy pipeline:** A computation whose intermediate stages wait for a terminal operation.

**Terminal operation:** An operation that consumes a stream and produces a result or action.

**Associative reduction:** A combination rule unaffected by regrouping operands.

## Reading the reference

stream() creates a pipeline,filter keeps matching elements,andmapToInt selects a primitive numeric stream. sum is a terminal reduction with identity0. groupingBy collects rows into groups;counting or summingInt defines the group aggregate. A stream cannot be reused after a terminal operation. In a parallel reduction, the identity must be neutral for every partition, and subtraction is not associative.

## Exercise 1: Filter and sum

Task: Keep even values from 1,2,3,4 and sum their squares.

The pipeline preserves the order of conceptual operations: selection happens before squaring and reduction. The result is a scalar rather than a modified source list.

```java
int total = List.of(1,2,3,4).stream().filter(value -> value % 2 == 0).mapToInt(value -> value * value).sum();
assert total == 20;
```

**Expected:** 20.

**Verify:** Compare the program values or named exception with 20. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Observe laziness with an explicit terminal

Task: Create a mapped stream that increments a counter,then consumetoList.

The counter is a teaching probe, not a recommended business side effect. toList requires mapped values, while some terminals may optimize away unnecessary stages.

```java
var calls = new java.util.concurrent.atomic.AtomicInteger();
var pipeline = List.of(1,2,3).stream().map(value -> { calls.incrementAndGet(); return value * 2; });
assert calls.get() == 0;
assert pipeline.toList().equals(List.of(2,4,6)) && calls.get() == 3;
```

**Expected:** counter0 before terminal and3 after.

**Verify:** Compare the program values or named exception with counter0 before terminal and3 after. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Group with a collector

Task: Count red,blue,red withgroupingBy and counting.

The collector owns accumulation rather than relying on shared external mutation. The map ordering is unspecified unless a specific ordered map supplier is chosen.

```java
Map<String,Long> counts = List.of("red","blue","red").stream().collect(java.util.stream.Collectors.groupingBy(value -> value, java.util.stream.Collectors.counting()));
assert counts.equals(Map.of("red",2L,"blue",1L));
```

**Expected:** red2L,blue1L.

**Verify:** Compare the program values or named exception with red2L,blue1L. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Reject stream reuse

Task: Consume a stream once,then attempt another terminal operation.

A stream represents one traversal. Create a new stream from the source when another computation is required.

```java
var once = List.of(1,2).stream(); assert once.count() == 2;
boolean reused = false;
try { once.toList(); } catch(IllegalStateException expected) { reused = true; }
assert reused;
```

**Expected:** IllegalStateException.

**Verify:** Compare the program values or named exception with IllegalStateException. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Check the reduction identity

Task: Compare sum reduction with identity0 against a deliberately wrong identity10.

An identity is not an arbitrary initial offset when parallel partitions may each receive it. The neutral value for addition is 0.

```java
int correct = List.of(1,2,3).stream().reduce(0,Integer::sum);
int wrong = List.of(1,2,3).stream().reduce(10,Integer::sum);
assert correct == 6 && wrong == 16;
```

**Expected:** correct6;wrong16 in the sequential fixture.

**Verify:** Compare the program values or named exception with correct6;wrong16 in the sequential fixture. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Expose nonassociative subtraction

Task: Compare(10-3)-2 with10-(3-2),then use an associative sum for a parallel fixture.

Subtraction changes under regrouping, so it is unsuitable as a general parallel reduction operator. Correctness must come before any performance experiment.

```java
assert (10-3)-2 == 5 && 10-(3-2) == 9;
assert java.util.stream.IntStream.rangeClosed(1,100).parallel().sum() == 5050;
```

**Expected:** 5 versus 9; parallel sum 5050.

**Verify:** Compare the program values or named exception with 5 versus 9; parallel sum 5050. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
