# spark-004: Immutable collections and transformations

Authored tutorial and practice content. The prepared Scala/JVM worker executes a bounded program; process success and understanding remain distinct. No source file installs a tool or downloads a dependency.

## Level and prerequisites

Beginner; approximately 105 minutes. Direct design prerequisites: `spark-003`. The lesson uses Scala 2.13 syntax and the prepared JDK 17 worker. The older design document proposed a different Spark/JDK tuple; use the current [execution baseline](../execution-baseline.md) for this authored material.

## How to run this lesson

Open `spark-004` in the classroom, select the Scala source, prepare the `scala-jvm` profile and run the saved pad. The worker stages the single source as `Main.scala` and invokes `object Main`. Read the terminal output and exact assertions. The [learner source](../lessons/spark-004.scala) runs two complete demonstrations; its six task functions remain explicit stubs until you implement them. Preserve your saved attempt. The [reference program](../solutions/spark-004_solution.scala) and [explained solutions](../solutions/spark-004_solutions.md) are separate and should be opened after an attempt or an explicit worked-comparison request. If the profile is unavailable, reading and saving remain available; opening this guide does not prepare a runtime.

## Learning objectives

- Use Seq and Map with map, filter and fold without mutating shared state.
- Explain the result of both worked examples before running them.
- Implement the six contracts, inspect normal and boundary evidence, and explain a counterexample in your own words.

## Vocabulary and concepts

- **Seq:** An ordered collection that preserves repeated elements; its values are not automatically a set.

- **map:** A transformation that returns one output for each input while preserving sequence order.

- **filter:** A transformation that retains elements satisfying a Boolean predicate and can change the row count.

- **foldLeft:** A reduction that starts with an explicit accumulator and updates it once for each element from left to right.

- **Immutable collection:** A collection whose structure is not changed by these operations; mutable objects stored inside it still need their own ownership policy.

An immutable collection pipeline describes a sequence of transformations without rewriting the input. `values.map(value => value / 20L)` converts each amount to a five-percent integer-cent fee. The arrow separates the function's parameter from its result expression. The short form `values.map(_ / 20L)` means the same single-parameter function, but reading the expanded form first makes the data flow clearer.

Filtering is different from mapping. `filter(_ >= 0L)` retains observed zero and removes negative amounts, while `filter(_ > 0L)` would silently drop valid zero-valued events. The source fixture contains duplicate 100-cent values because two equal measurements can belong to different events. Converting it to a Set changes multiplicity and therefore changes totals. Deduplication needs a real identity rule, not equality of amount.

A reduction needs an identity and accumulator type. `foldLeft(0L)` begins with a Long zero so an empty sequence has total zero and subsequent additions stay in the intended type. Reducing without an initial value can fail on empty input. A tuple accumulator can carry count and total together, making conservation checks explicit. Pattern matching the tuple inside a fold names each part without mutable counters.

Maps describe key-based summaries rather than a reliable presentation order. This lesson compares Map values by key and sorts entries only when a human-facing order is needed. Assigning `key -> value` repeatedly can overwrite earlier observations; counting with a fold or grouping must retain their multiplicity. A map of totals does not automatically include groups with no accepted rows, so the rejection ledger remains a separate output.

Immutable structure does not mean every value reachable through it is immutable. A Seq of mutable buffers can still expose shared changes inside those buffers. The fixture uses Long values and String group labels so the boundaries stay simple. The lesson also distinguishes ordinary arithmetic from checked arithmetic: Math.addExact throws on a Long overflow rather than wrapping into a plausible negative total.

The final grouped report uses a real group label plus every accepted occurrence. Negative amounts are rejected by policy, zero remains observed, and repeated positive values both contribute. Verify accepted plus rejected count, accepted total and per-group totals before describing the report as reconciled. These are local Scala collections; the same reasoning will later define Spark row contracts, but no distributed execution is implied here.

## Worked example / walkthrough

### Worked example 1

```scala
val original = Seq(1L, 2L, 3L)
val doubled = original.map(value => value * 2L)
assert(doubled == Seq(2L, 4L, 6L))
assert(original == Seq(1L, 2L, 3L))
println(doubled.mkString(","))
```

map produces three outputs because it transforms rather than filters. The input sequence remains unchanged, and equality compares both order and values. The Long suffix keeps the numeric type visible. This small trace introduces the lambda syntax before the exercise combines several transformations.

### Worked example 2

```scala
val amounts = Seq(12L, 3L)
val total = amounts.foldLeft(0L)((sum, amount) => Math.addExact(sum, amount))
val emptyTotal = Seq.empty[Long].foldLeft(0L)(_ + _)
assert(total == 15L && emptyTotal == 0L)
println(s"total=$total empty=$emptyTotal")
```

The first argument list supplies the starting accumulator; the second supplies the update function. Checked addition exposes overflow instead of allowing silent wraparound. The empty sequence still has a defined result because the initial value is part of the reduction contract.

## Exercises

### Exercise 1: Retain observed zero and repeated values

Implement a nonnegative filter for Seq(100L,-5L,0L,100L,25L). Preserve input order and duplicate values. An empty input should remain empty.

**Expected result/shape:** The result is Seq(100L,0L,100L,25L), with four occurrences. Both 100-cent entries and the zero remain.

**Verify:** Assert the exact sequence and confirm the original five-element sequence is unchanged; also assert accepted(Seq.empty) is empty.

**Progressive hint:** Compare the policy nonnegative with strictly positive before choosing the comparison operator.

### Exercise 2: Keep a rejected ledger

Split every input amount into accepted nonnegative and rejected negative sequences, preserving order within each output. Return both sequences instead of dropping rejected data.

**Expected result/shape:** The five-value fixture yields accepted four values and rejected Seq(-5L). Accepted size plus rejected size equals five, including an all-negative or empty fixture.

**Verify:** Assert both exact outputs, their combined count and an all-negative case with empty accepted output.

**Progressive hint:** partition computes complementary outputs from one predicate.

### Exercise 3: Map a bounded numeric policy

For nonnegative Long amounts, return integer-cent five-percent fees rounded down. Reject a negative amount with IllegalArgumentException. Avoid multiplying by five before division, which could overflow on a very large Long.

**Expected result/shape:** Seq(100L,0L,100L,25L) maps to Seq(5L,0L,5L,1L). Long.MaxValue maps safely to Long.MaxValue/20L.

**Verify:** Assert the exact four fees, the maximum-Long case and rejection of Seq(-1L).

**Progressive hint:** For nonnegative integer amounts, floor(amount*5/100) equals amount/20 without the intermediate multiplication.

### Exercise 4: Fold count and total together

Return occurrence count and checked Long total for a supplied sequence. Use an explicit tuple accumulator and Math.addExact for the total. Empty input returns (0L,0L); an overflowing total raises ArithmeticException.

**Expected result/shape:** The accepted fixture returns (4L,225L), while Seq(Long.MaxValue,1L) is rejected by checked addition.

**Verify:** Assert the two-component result, the empty identity and the overflow exception independently.

**Progressive hint:** A fold accumulator can be a tuple matched as(count, total) in each update.

### Exercise 5: Represent multiplicity in a Map

Return a map from amount to occurrence count without discarding repeated values. Compare maps by keys and counts rather than assuming iteration order. Empty input returns an empty map.

**Expected result/shape:** The accepted fixture yields Map(100L->2L,0L->1L,25L->1L); the sum of counts is four.

**Verify:** Assert exact map equality and reconcile all map counts to the accepted sequence size.

**Progressive hint:** Fold an immutable Map and update one key with its previous count plus one.

### Exercise 6: Transfer the bag contract to grouped reporting

Given group/amount pairs, reject blank group labels, retain nonnegative amount occurrences and return per-group(count, total) using checked summary. Groups with only rejected amounts are absent from the accepted report and remain explainable through the rejection policy.

**Expected result/shape:** A100, A100, B0, B25, C-5 yields A:(2,200), B:(2,25). Report counts sum to four and totals to 225; a blank label is rejected even on a negative row.

**Verify:** Assert the complete map, both global reconciliations and the blank-label failure before filtering can hide it.

**Progressive hint:** Validate identity first, filter by amount second, then group and summarize each retained bag.

## Common pitfalls

If the accepted count is three instead of four, inspect whether zero was dropped or duplicate amounts were collapsed. If grouped totals differ from the global accepted total, trace each input occurrence into its group before changing arithmetic. If an empty reduction fails, use an explicit identity with foldLeft. If a large total becomes negative, distinguish ordinary wrapping addition from checked Math.addExact. If a Map prints in a surprising order, compare keyed values or sort for presentation rather than changing the data structure's meaning.

## Self-check

Explain one input-to-output trace without reading your code. Identify which function preserves repeated values, which condition distinguishes an invalid or missing input, and which assertion would fail for the tempting incorrect implementation. A printed success line alone is not the evidence; retain the exact values and the reasoning that connect them to the contract.

## Next step

Continue to the next lesson only after you can explain the boundary behavior. The [course route](../README.md) shows authored material and runtime evidence separately.

## Primary sources and official APIs

- [Scala 2 collection transformations](https://docs.scala-lang.org/overviews/scala-book/collections-methods.html).

- [Scala 2.13 immutable collections](https://docs.scala-lang.org/overviews/collections-2.13/introduction.html).

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-004: Immutable collections and transformations.
Read courses/scala-spark/guides/spark-004.md and courses/scala-spark/lessons/spark-004.scala. Direct prerequisites: spark-003.
Explain the Scala 2.13 syntax and data contract, ask me to predict a concrete result, then inspect my attempt. Give one hint at a time, review exact assertion evidence and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt. Use only the prepared scala-jvm profile and preserve my saved work; do not install or download dependencies.
Done when all six contracts and their boundary cases have inspected evidence and I can explain why an incorrect implementation fails.
```
