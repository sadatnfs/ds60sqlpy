# spark-002: explanatory solutions

Compare after an attempt or an explicit reveal. The [guide](../guides/spark-002.md) defines the learner contract. An authored reference is not a platform acceptance receipt.

## Vocabulary and concepts

Scala evaluates expressions to values. `val total: Long = ...` binds a name to one value; it does not create a spreadsheet cell that continually recalculates. A val cannot be reassigned. `var` permits reassignment but is unnecessary for this basket. The type follows a colon; the literal suffix L makes an integer a Long. `if` is an expression, so its branches can produce the String assigned to message.

The worker entry point is `object Main` with `def main(args: Array[String]): Unit`. Read it as a named singleton containing the program start function. Array[String] holds optional launch arguments, which this lesson ignores; Unit means the start function returns no useful value. Braces group statements. println writes one output line. The [Scala basics tour](https://docs.scala-lang.org/tour/basics.html) distinguishes immutable values, variables, blocks and functions.

- **val:** an immutable name binding
- **Long:** a signed 64-bit integral value; use L on these small literal examples
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

## Exercises and explanatory solutions

### Exercise 1: Compute the basket

**Inputs/evidence:** 125L, 200L, 75L.

**Expected result/shape:** Total is 400L.

**Verify:** Assert total==400L and print the named value.

Addition preserves all three prices. A literal String "400" can look correct when printed but is not the required Long result.

### Exercise 2: Preserve the type boundary

**Inputs/evidence:** 2147483647L+1L and an intentionally reviewed Int-only variant.

**Expected result/shape:** Long result 2147483648L; reject relying on the overflowing Int value as money.

**Verify:** Run the Long assertion; explain why the narrower arithmetic is a different contract.

The expected number exceeds the positive Int range. This small example shows type choice before data grows, without requiring an overflow as a valid answer.

### Exercise 3: Calculate remaining budget

**Inputs/evidence:** Budget 450L, total 400L.

**Expected result/shape:** Remaining 50L.

**Verify:** Assert the difference, not merely the total.

A separate immutable budget keeps the meaning of each input visible. Subtract total from budget; reversing operands yields -50 and a different statement.

### Exercise 4: Return a branch value

**Inputs/evidence:** Remaining 50L, threshold 0L.

**Expected result/shape:** String message is within budget.

**Verify:** Assert the exact String and its nonnegative condition.

Both branches must return meaningful labels. Writing println inside each branch would make the assigned result Unit rather than the intended String.

### Exercise 5: Diagnose reassignment

**Inputs/evidence:** One immutable binding and a proposed reassignment.

**Expected result/shape:** Compile-time rejection; repaired code uses a new name revisedBudget with 350L.

**Verify:** Retain the compiler error category and show the new-name repair; do not include broken code in the final reference.

Reassignment violates val. The lesson asks for a new scenario, so name that scenario rather than replacing the original input or switching to var without a reason.

### Exercise 6: Transfer the budget

**Inputs/evidence:** Same 400L basket, new 350L budget.

**Expected result/shape:** Remaining -50L and over budget label.

**Verify:** Assert both changed outputs while the original total stays 400L.

Only the budget changes. A result that also changes spending has mixed the two scenarios; preserve the original bindings to expose that error.

Notice that the same `if` expression from Exercise 4 now produces the other label without any edit to its code. The label depends only on the sign of the remaining value, so a negative Long selects the over budget branch. If your message still reads within budget, check whether the comparison uses the new remaining value or a stale binding from the first scenario.

## Retrieval review

Close the source. Explain the mechanism in your own words, name the boundary that a plausible wrong answer crosses, and predict a changed fixture before running again.

A complete review accounts for every named expected value and one deliberately incorrect alternative. A process exit by itself does not grade reasoning.
