# spark-002: Scala values, types, expressions, and the REPL

Scala programs are built from expressions that produce values, and every value has a type. This lesson prices a small basket with immutable `Long` values, shows where an `Int` would overflow, chooses a message with an `if` expression and repairs an attempt to reassign a `val`. It also explains what a REPL is, even though the classroom compiles the whole file and shows results through `println`.

## Level and prerequisites

Beginner; 60 minutes. Direct prerequisites: `spark-001`. Pinned versions: [execution baseline](../execution-baseline.md). Shared run steps: [study guide](../STUDY-GUIDE.md#run-a-language-lesson).

Learner artifact: [spark-002.scala](../lessons/spark-002.scala). Keep [solutions](../solutions/spark-002_solutions.md) closed until an attempt or explicit reveal.

## Learning objectives

- Read Scala 2.13 syntax and use immutable typed values and expression results.
- Produce the exact bounded evidence named by the six exercises and explain one counterexample.

## Vocabulary and concepts

Scala evaluates expressions to values. `val total: Long = ...` binds a name to one value; it does not create a spreadsheet cell that continually recalculates. A val cannot be reassigned. `var` permits reassignment but is unnecessary for this basket. The type follows a colon; the literal suffix L makes an integer a Long. `if` is an expression, so its branches can produce the String assigned to message.

The worker entry point is `object Main` with `def main(args: Array[String]): Unit`. Read it as a named singleton containing the program start function. Array[String] holds optional launch arguments, which this lesson ignores; Unit means the start function returns no useful value. Braces group statements. println writes one output line. The [Scala basics tour](https://docs.scala-lang.org/tour/basics.html) distinguishes immutable values, variables, blocks and functions.

The REPL in this lesson's title is Scala's read-eval-print loop: an interactive prompt that reads one expression, evaluates it, prints the result and waits for the next one. The [Scala REPL overview](https://docs.scala-lang.org/overviews/repl/overview.html) explains that each input line is compiled separately and earlier results stay in scope. This classroom does not open a REPL. It compiles the whole lesson file and runs `main`, so `println` is how you see a value. If you install [Scala CLI](https://scala-cli.virtuslab.org/docs/commands/repl) on your own machine, `scala-cli repl -S 2.13.18` opens a Scala 2.13 prompt where typing `120L + 30L` shows the `Long` result 150. Use it to try one expression, then move that expression into the lesson file.

- **val:** an immutable name binding
- **Long:** a signed 64-bit integral value; use L on these small literal examples
- **String:** text inside double quotes
- **expression:** code that produces a value
- **interpolation:** s"total=$total" inserts a named value into text
- **REPL:** an interactive read-eval-print loop that evaluates one expression at a time; this classroom compiles a file instead

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

**Inputs/evidence:** 125L, 200L, 75L.

**Expected result/shape:** Total is 400L.

**Verify:** Assert total==400L and print the named value.

**Progressive hints:**

1. Keep each price named.
2. All literals use L.
3. Add first+second+third.

### Exercise 2: Preserve the type boundary

Compare Int and Long at a documented boundary.

**Inputs/evidence:** 2147483647L+1L and an intentionally reviewed Int-only variant.

**Expected result/shape:** Long result 2147483648L; reject relying on the overflowing Int value as money.

**Verify:** Run the Long assertion; explain why the narrower arithmetic is a different contract.

**Progressive hints:**

1. Inspect the literal suffix.
2. The result type follows the operands.
3. Use Long before arithmetic, not after an overflow.

### Exercise 3: Calculate remaining budget

Bind a `450L` budget and compute remaining cents.

**Inputs/evidence:** Budget 450L, total 400L.

**Expected result/shape:** Remaining 50L.

**Verify:** Assert the difference, not merely the total.

**Progressive hints:**

1. Which amount is available first?
2. Remaining means budget minus spending.
3. 450L-400L is 50L.

### Exercise 4: Return a branch value

Use an if expression for the budget label.

**Inputs/evidence:** Remaining 50L, threshold 0L.

**Expected result/shape:** String message is within budget.

**Verify:** Assert the exact String and its nonnegative condition.

**Progressive hints:**

1. An if can produce a value.
2. Both branches should have the same useful type.
3. Assign if(condition) "within budget" else "over budget".

### Exercise 5: Diagnose reassignment

Review `val budget=450L; budget=350L` and repair without mutation.

**Inputs/evidence:** One immutable binding and a proposed reassignment.

**Expected result/shape:** Compile-time rejection; repaired code uses a new name revisedBudget with 350L.

**Verify:** Retain the compiler error category and show the new-name repair; do not include broken code in the final reference.

**Progressive hints:**

1. Read the binding keyword.
2. A second scenario deserves another value name.
3. Use val revisedBudget: Long=350L.

### Exercise 6: Transfer the budget

Repeat the calculation with 350L and predict the sign.

**Inputs/evidence:** Same 400L basket, new 350L budget.

**Expected result/shape:** Remaining-50L and over budget label.

**Verify:** Assert both changed outputs while the original total stays 400L.

**Progressive hints:**

1. Keep the three prices.
2. Only one input changes.
3. 350L-400L=-50L, so the negative branch applies.

## Self-check

- The basket total is `400L`. Why does `val total` keep that value even if a later line computes a different amount, and how would you show the new amount instead?
- `2147483647L + 1L` gives `2147483648L`, but the same sum computed as `Int` wraps around to a negative number. Why is the `Long` result the right contract for money in cents?
- `budget = 350L` after `val budget = 450L` fails to compile. Why is introducing `revisedBudget` a repair rather than a workaround?
- With a 350L budget the remainder becomes `-50L` and the label switches to over budget. Which expression chose the label, and why does the total stay `400L`?

## Retrieval and transfer

Close the source. Explain the mechanism in your own words, name the boundary that a plausible wrong answer crosses, and predict a changed fixture before running again.

## Common pitfalls

A printed number can hide a String/Long mismatch. Int overflow is not repaired by converting the already-overflowed result. Do not put println branches into a String expression, and do not use var merely to avoid naming a second scenario.

## Next step

Continue with [spark-003](spark-003.md), which puts these expression rules behind explicit function contracts.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach spark-002.
Read courses/scala-spark/guides/spark-002.md and courses/scala-spark/lessons/spark-002.scala.
Direct prerequisites: `spark-001`. This lesson is authored; check its current runtime readiness and direct prerequisites.
Explain one mechanism, ask me to predict, let me attempt one exercise, then give one hint at a time.
Do not read courses/scala-spark/solutions/ until I make an honest attempt or explicitly ask for a reveal.
Review my exact values, diagnostics or written evidence; distinguish source inspection, process success and verified understanding.
Finish with a changed fixture and retrieval in my own words. Do not install tools, download assets or select an ambient cluster for me.
```
