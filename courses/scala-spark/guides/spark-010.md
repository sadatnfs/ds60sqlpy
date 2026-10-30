# spark-010: Laziness, iterators, and safe side effects

Authored tutorial and practice content. The prepared Scala/JVM worker executes a bounded program; process success and understanding remain distinct. No source file installs a tool or downloads a dependency.

## Level and prerequisites

Beginner; approximately 105 minutes. Direct design prerequisites: `spark-009`. The lesson uses Scala 2.13 syntax and the prepared JDK 17 worker. The older design document proposed a different Spark/JDK tuple; use the current [execution baseline](../execution-baseline.md) for this authored material.

## How to run this lesson

Open `spark-010` in the classroom, select the Scala source, prepare the `scala-jvm` profile and run the saved pad. The worker stages the single source as `Main.scala` and invokes `object Main`. Read the terminal output and exact assertions. The [learner source](../lessons/spark-010.scala) runs two complete demonstrations; its six task functions remain explicit stubs until you implement them. Preserve your saved attempt. The [reference program](../solutions/spark-010_solution.scala) and [explained solutions](../solutions/spark-010_solutions.md) are separate and should be opened after an attempt or an explicit worked-comparison request. If the profile is unavailable, reading and saving remain available; opening this guide does not prepare a runtime.

## Learning objectives

- Predict when local lazy transformations run and explain why retryable distributed work must not hide side effects.
- Explain the result of both worked examples before running them.
- Implement the six contracts, inspect normal and boundary evidence, and explain a counterexample in your own words.

## Vocabulary and concepts

- **Iterator:** A consumable traversal whose elements are produced on demand and usually cannot be traversed again after exhaustion.

- **Strict collection:** A collection whose values are already materialized, so a normal map/filter computes a new collection when called.

- **Evaluation boundary:** The operation that requests values from a lazy pipeline and causes its deferred work to run.

- **Retryable side effect:** An externally visible action that may occur again when work is re-evaluated or retried, requiring a separate delivery contract.

Laziness concerns when work happens. A strict Seq.map evaluates its transformation while building the output. An Iterator.map describes a transformation applied as elements are requested. Creating the iterator therefore need not run the transformation at all. Calling next, taking a prefix or collecting values moves the evaluation boundary and can trigger work.

Iterator is one-shot state. After toVector consumes it, a second toVector is normally empty. A function returning a fresh iterator can support repeated traversals of the same immutable source. That factory differs from storing one iterator and returning the same exhausted object repeatedly. A LazyList has its own memoization behavior and should not be treated as interchangeable with an Iterator.

The lesson uses an ArrayBuffer of trace strings only as a local diagnostic. Filter and map steps append messages so you can predict exactly which source values were examined for a requested prefix. That trace is not a business counter or a payment mechanism. A filter may examine several source elements before producing one output, and checking hasNext can cause filtering work before next returns a value.

A pure transformation can be recomputed safely because its result depends only on its inputs. An external increment, email or database write inside a transformation can happen again if evaluation is repeated. Spark introduces distributed task retries and recomputation on top of laziness, so a function that appeared to run once in a small local example does not establish exactly-once side effects.

The retry illustration calculates naive delivered totals and a logical identity-based total from a tiny ledger. Equal event IDs with conflicting amounts are rejected; repeated identical IDs represent delivery replay. This pure calculation shows the difference in quantities, but it is not an implementation of an atomic production sink. Durable idempotency needs an explicit transaction or publication boundary, which later streaming lessons will examine.

Bounded consumption is another contract. Taking three values from an infinite iterator is safe when the consumer never asks for more; collecting the whole iterator would never terminate. The exercise permits only limits from 0 through 1000 and confirms that limit 0 does not consume the first value. A count of returned rows is not enough to prove a filter did bounded source work when matching values are rare, so input and output budgets must be distinguished.

These are Scala collection semantics. They prepare the mental model for Spark transformations and actions, but Spark may perform planning, metadata reads or schema inference before a familiar action. Later lessons use explicit schemas and actual plan/runtime evidence rather than transferring the local iterator trace as an exact description of engine behavior.

## Worked example / walkthrough

### Worked example 1

```scala
var visits = 0
val pipeline = Seq(1, 2, 3).iterator.map { value => visits += 1; value * 2 }
assert(visits == 0)
assert(pipeline.next() == 2 && visits == 1)
assert(pipeline.toVector == Vector(4, 6) && visits == 3)
assert(pipeline.toVector.isEmpty)
println(s"visits=$visits after complete consumption")
```

Creating the mapped iterator does no mapped work. Each requested value increments the diagnostic counter once, and the second full traversal is empty because the iterator was exhausted. The mutable counter is confined to this demonstration and is deliberately not used to define the numerical result.

### Worked example 2

```scala
val source = Seq(1, 2, 3, 4)
def fresh(): Iterator[Int] = source.iterator.filter(_ % 2 == 0).map(_ * 2)
assert(fresh().toVector == Vector(4, 8))
assert(fresh().toVector == Vector(4, 8))
assert(source == Seq(1, 2, 3, 4))
println("A factory creates a new traversal each time")
```

Each call constructs a fresh iterator over unchanged source values. Repetition produces equal data without depending on the state of a previously consumed iterator. This is a useful pattern when repeated local evaluation is intended, and it keeps the repeatability claim separate from external side effects.

## Exercises

### Exercise 1: Establish a pure strict result

For inputs between-1000000 and 1000000, retain even values and double them in order. Preserve input and duplicates. Reject values outside the bound so Int multiplication is safe.

**Expected result/shape:** Seq(1,2,3,4) becomes Seq(4,8); Seq(0,2,2) becomes Seq(0,4,4); empty remains empty.

**Verify:** Assert the exact results, input preservation and the out-of-domain rejection.

**Progressive hint:** Separate the even predicate from the doubling map and validate the domain first.

### Exercise 2: Locate the evaluation boundary

Return a lazy even-filter/double-map iterator with local trace messages filter: value and map: value. Validate the same numeric domain before construction. The trace should remain empty until consumption.

**Expected result/shape:** Taking one output from 1,2,3,4 yields 4 with trace filter:1, filter:2, map:2. Consuming the rest yields 8 and appends filter:3, filter:4, map:4.

**Verify:** Assert the empty initial trace, both exact output pieces and all six messages in order.

**Progressive hint:** Put diagnostic appends inside filter/map lambdas, not in an eager preprocessing loop.

### Exercise 3: Expose one-shot traversal state

Consume a supplied iterator into a Vector twice and return both results. Do not cache or recreate the iterator inside this function. Explain why this intentionally returns an empty second traversal.

**Expected result/shape:** A fresh iterator over 1,2,3 yields (Vector(1,2,3), Vector.empty). An already empty iterator yields two empty Vectors.

**Verify:** Assert both tuple components and the already-exhausted case.

**Progressive hint:** Call toVector twice on the same iterator reference.

### Exercise 4: Provide repeatability deliberately

Return a factory creating a fresh bounded even-filter/double-map iterator on each call. Validate source values once and preserve them. Do not return the same iterator object repeatedly.

**Expected result/shape:** Two factory calls both yield Vector(4,8) for 1,2,3,4, even after the first is exhausted.

**Verify:** Consume two independently obtained iterators and assert both exact results; verify the immutable source remains unchanged.

**Progressive hint:** Put values.iterator inside the returned zero-argument lambda.

### Exercise 5: Separate repeated delivery from logical identity

For bounded nonnegative event amounts and nonblank IDs, compute naive delivered cents over attempts and logical once-per-ID cents when attempts>0. Reject conflicting amounts for one ID and negative attempt counts. This is a pure ledger calculation, not a real sink.

**Expected result/shape:** Records(a,100),(b,50),(a,100) with two attempts give naive 500, logical 150. Zero attempts gives (0,0); same ID with 100 and 101 is rejected.

**Verify:** Assert both totals, the zero-attempt identity and a conflicting-payload failure.

**Progressive hint:** Validate payload consistency per ID, then compare every-delivery summation with one value per identity.

### Exercise 6: Consume only a declared bounded prefix

Return at most limit values from an iterator, requiring 0<=limit<=1000. Support infinite iterators without collecting the whole source. Limit 0 must leave the next source value unconsumed.

**Expected result/shape:** Taking three values from Iterator.from(1) yields 1,2,3 and leaves 4 next. Limit 0 yields empty and leaves 1 next; limit 1001 is rejected.

**Verify:** Use a local next-value counter to assert three produced values, and test zero consumption and the upper-budget failure.

**Progressive hint:** Use take(limit).toVector after validating the budget.

## Common pitfalls

If a trace appears before consumption, find an eager collection operation or side effect outside the iterator body. If the second traversal is empty, check whether a cursor rather than a factory was reused. If retry totals grow, move external effects out of pure transformations and define a durable idempotency boundary instead of trusting a local counter. If an infinite iterator hangs, inspect for an unbounded terminal collection. If a prefix limit appears safe but a rare filter scans indefinitely, distinguish output count from source-work budget.

## Self-check

Without opening the reference, trace the listed boundary case through `strictPipeline`. Then explain why `boundedTake` needs its declared invariant or input restriction. Name the exact assertion that would reject one tempting wrong implementation. Retain the observed values and explain how they support the lesson outcome: Predict when local lazy transformations run and explain why retryable distributed work must not hide side effects.

## Next step

Continue to the next lesson only after you can explain the boundary behavior. The [course route](../README.md) shows authored material and runtime evidence separately.

## Primary sources and official APIs

- [Scala 2.13 iterator semantics](https://docs.scala-lang.org/overviews/collections-2.13/iterators.html).

- [Spark 4.0.1 RDD laziness and closure semantics](https://spark.apache.org/docs/4.0.1/rdd-programming-guide.html).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-010: Laziness, iterators, and safe side effects.
Read courses/scala-spark/guides/spark-010.md and courses/scala-spark/lessons/spark-010.scala. Direct prerequisites: spark-009.
Explain the Scala 2.13 syntax and data contract, ask me to predict a concrete result, then inspect my attempt. Give one hint at a time, review exact assertion evidence and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt. Use only the prepared scala-jvm profile and preserve my saved work; do not install or download dependencies.
Done when all six contracts and their boundary cases have inspected evidence and I can explain why an incorrect implementation fails.
```
