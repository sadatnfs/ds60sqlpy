# spark-002: Scala values, types, expressions, and the REPL

Authored classroom lesson. Content availability and runtime readiness are separate checks. Read the current capability notice before running. No opening or saving this lesson installs tools, starts a cluster or proves mastery.

## Level and prerequisites

Beginner; 60 minutes. Direct design prerequisites: `spark-001`. Use the subject browser to open prerequisite lessons or review their concepts. Runtime readiness is checked separately before execution.

Learner artifact: [spark-002.scala](../lessons/spark-002.scala). Keep [solutions](../solutions/spark-002_solutions.md) closed until an attempt or explicit reveal.

## Learning objectives

- Read Scala 2.13 syntax and use immutable typed values and expression results.
- Produce the exact bounded evidence named by the six exercises and explain one counterexample.

## Vocabulary and concepts

Scala evaluates expressions to values. `val total: Long = ...` binds a name to one value; it does not create a spreadsheet cell that continually recalculates. A val cannot be reassigned. `var` permits reassignment but is unnecessary for this basket. The type follows a colon; the literal suffix L makes an integer a Long. `if` is an expression, so its branches can produce the String assigned to message.

The worker entry point is `object Main` with `def main(args: Array[String]): Unit`. Read it as a named singleton containing the program start function. Array[String] holds optional launch arguments, which this lesson ignores; Unit means the start function returns no useful value. Braces group statements. println writes one output line. The [Scala basics tour](https://docs.scala-lang.org/tour/basics.html) distinguishes immutable values, variables, blocks and functions.

- **val:** an immutable name binding
- **Long:** a signed64-bit integral value; use L on these small literal examples
- **String:** text inside double quotes
- **expression:** code that produces a value
- **interpolation:** s"total=$total" inserts a named value into text

## Worked example / walkthrough

### Worked example 1: Name an exact subtotal

Both operands are Long values, so the money calculation remains integral.

```scala
val subtotal: Long = 120L + 30L
assert(subtotal == 150L)
println(subtotal)
```

**Expected:** 150; the assertion passes.

### Worked example 2: Choose text using an expression

The branches return values; no mutable label is needed.

```scala
val change: Long = -5L
val label: String = if (change >= 0L) "available" else "short"
assert(label == "short")
println(label)
```

**Expected:** short; only one branch supplies the assigned String.

## Exercises

### Exercise 1: Compute the basket

Keep three named prices and calculate their total.

**Inputs/evidence:** For spark-002 Exercise 1, 125L,200L,75L.

**Expected result/shape:** For spark-002 Exercise 1, total is400L.

**Verify:** For spark-002 Exercise 1, assert total==400L and print the named value.

**Progressive hints:**

1. Keep each price named.
2. All literals use L.
3. Add first+second+third.

### Exercise 2: Preserve the type boundary

Compare Int and Long at a documented boundary.

**Inputs/evidence:** For spark-002 Exercise 2, 2147483647L+1L and an intentionally reviewed Int-only variant.

**Expected result/shape:** For spark-002 Exercise 2, Long result2147483648L; reject relying on the overflowing Int value as money.

**Verify:** For spark-002 Exercise 2, run the Long assertion; explain why the narrower arithmetic is a different contract.

**Progressive hints:**

1. Inspect the literal suffix.
2. The result type follows the operands.
3. Use Long before arithmetic, not after an overflow.

### Exercise 3: Calculate remaining budget

Bind a450L budget and compute remaining cents.

**Inputs/evidence:** For spark-002 Exercise 3, budget450L,total400L.

**Expected result/shape:** For spark-002 Exercise 3, remaining50L.

**Verify:** For spark-002 Exercise 3, assert the difference, not merely the total.

**Progressive hints:**

1. Which amount is available first?
2. Remaining means budget minus spending.
3. 450L-400L is50L.

### Exercise 4: Return a branch value

Use an if expression for the budget label.

**Inputs/evidence:** For spark-002 Exercise 4, remaining50L, threshold0L.

**Expected result/shape:** For spark-002 Exercise 4, String message is within budget.

**Verify:** For spark-002 Exercise 4, assert the exact String and its nonnegative condition.

**Progressive hints:**

1. An if can produce a value.
2. Both branches should have the same useful type.
3. Assign if(condition) "within budget" else "over budget".

### Exercise 5: Diagnose reassignment

Review `val budget=450L; budget=350L` and repair without mutation.

**Inputs/evidence:** For spark-002 Exercise 5, one immutable binding and a proposed reassignment.

**Expected result/shape:** For spark-002 Exercise 5, compile-time rejection; repaired code uses a new name revisedBudget with350L.

**Verify:** For spark-002 Exercise 5, retain the compiler error category and show the new-name repair; do not include broken code in the final reference.

**Progressive hints:**

1. Read the binding keyword.
2. A second scenario deserves another value name.
3. Use val revisedBudget: Long=350L.

### Exercise 6: Transfer the budget

Repeat the calculation with350L and predict the sign.

**Inputs/evidence:** For spark-002 Exercise 6, same400L basket,new350L budget.

**Expected result/shape:** For spark-002 Exercise 6, remaining-50L and over budget label.

**Verify:** For spark-002 Exercise 6, assert both changed outputs while the original total stays400L.

**Progressive hints:**

1. Keep the three prices.
2. Only one input changes.
3. 350L-400L=-50L, so the negative branch applies.

## Self-check

- Can you reproduce each exact observation without reading the official answer?
- Can you explain a failed check using the lesson's model, rather than changing an expected value?

## Retrieval and transfer

Close the source. Explain the mechanism in your own words, name the boundary that a plausible wrong answer crosses, and predict a changed fixture before running again.

## Common pitfalls

A printed number can hide a String/Long mismatch. Int overflow is not repaired by converting the already-overflowed result. Do not put println branches into a String expression, and do not use var merely to avoid naming a second scenario.

## Next step

Continue with [spark-003](spark-003.md), which puts these expression rules behind explicit function contracts.

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach spark-002.
Read courses/scala-spark/guides/spark-002.md and courses/scala-spark/lessons/spark-002.scala.
Direct design prerequisites: `spark-001`. This is authored beta content; check actual runtime capability and unpublished prerequisites.
Explain one mechanism, ask me to predict, let me attempt one exercise, then give one hint at a time.
Do not read courses/scala-spark/solutions/ until I make an honest attempt or explicitly ask for a reveal.
Review my exact values, diagnostics or written evidence; distinguish source inspection, process success and verified understanding.
Finish with a changed fixture and retrieval in my own words. Do not install tools, download assets or select an ambient cluster for me.
```
