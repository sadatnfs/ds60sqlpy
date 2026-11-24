# spark-003: explanatory solutions

Compare after an attempt or an explicit reveal. The [guide](../guides/spark-003.md) defines the learner contract. An authored reference is not a platform acceptance receipt.

## Vocabulary and concepts

A function names a rule with input parameters and a result type. `def addCents(left: Long, right: Long): Long = left + right` reads: accept two Long values, return a Long, and evaluate their sum. Calling it supplies argument values; defining it does not run it. A pure function has no hidden state change and returns the same answer for the same inputs. An explicit return type makes the contract visible to both the reader and compiler.

The fee domain is deliberately bounded to amounts from -1000000 through 1000000 cents. Nonpositive amounts cost zero. A nonmember with a positive amount pays 20 cents. A member pays zero below 500 cents and five percent at or above 500, rounded down by integer division. This makes every branch and numeric boundary inspectable. Multiplication is safe inside this domain; the lesson does not promise arbitrary Long multiplication cannot overflow.

- **def:** introduces a named function
- **parameter:** a named input inside the definition
- **argument:** a value supplied in a call
- **Boolean:** true or false, used by the branch
- **pure function:** a repeatable input-to-result rule with no externally visible mutation

## Worked example / walkthrough

### Worked example 1: Call a function twice

Arguments vary while the rule remains fixed. Assertions state the return contract.

```scala
def addCents(a: Long, b: Long): Long = a + b
assert(addCents(30L, 5L) == 35L)
assert(addCents(0L, 5L) == 5L)
```

**Expected:** 35L and 5L, from the same function definition.

### Worked example 2: Make a total bounded branch

The equality boundary belongs to one branch deliberately; testing only 20 would miss it.

```scala
def bonus(points: Long): Long = if (points >= 10L) 2L else 0L
assert(bonus(9L) == 0L)
assert(bonus(10L) == 2L)
```

**Expected:** 9 maps to 0L and 10 maps to 2L.

## Exercises and explanatory solutions

### Exercise 1: Separate definition and call

**Inputs/evidence:** `AddCents(100L, 25L)`, `addCents(0L, 25L)`.

**Expected result/shape:** 125L and 25L.

**Verify:** Assert both returned values; distinguish parameter names from arguments.

left/right name inputs in the definition. 100L and 25L are arguments in a call. The function definition is reused rather than copied and edited.

### Exercise 2: Implement branch order

**Inputs/evidence:** 0L with both membership values; 100L with both values.

**Expected result/shape:** Fees 0/0 for zero and 0/20 for 100.

**Verify:** Assert all four cases and inspect guard order.

If nonmember is checked first, zero can incorrectly receive the flat 20-cent fee. The boundary guard must take precedence over membership.

### Exercise 3: Test the membership threshold

**Inputs/evidence:** Member 499L, 500L, 501L.

**Expected result/shape:** Fees 0L, 25L, 25L.

**Verify:** Assert the exact three outputs and explain integer division.

The 500 equality belongs to the percentage branch. 501*5/100 floors 25.05 to 25 integer cents under the stated policy; this is a deliberate rounding rule.

### Exercise 4: Use named arguments

**Inputs/evidence:** `feeCents(isMember=true, amount=1000L)`.

**Expected result/shape:** 50L, equal to the positional call.

**Verify:** Assert both calls give 50L; do not change the definition.

Named arguments bind by parameter name. Reordering them is a readability choice and does not change the fee rule or types.

### Exercise 5: Reject hidden state

**Inputs/evidence:** Two consecutive `feeCents(1000L, true)` calls and negative amount-1L.

**Expected result/shape:** Both calls 50L; negative amount yields 0L even for a nonmember.

**Verify:** Repeat exact calls and explain why a call counter must not alter the returned fee.

Counting calls inside a pricing rule can make retries change business output. Preserve a pure calculation and keep operational counting separate.

### Exercise 6: Transfer and explain the domain

**Inputs/evidence:** 2000L, true/false and 2000000L.

**Expected result/shape:** 100L/20L; the out-of-domain input is rejected by the reference precondition.

**Verify:** Assert the two valid results and identify the violated bound for the third.

The rule scales within the bounded domain. The require guard is evidence of that domain, not a claim that all financial products can use this rounding or fee policy.

## Retrieval review

Close the source. Explain the mechanism in your own words, name the boundary that a plausible wrong answer crosses, and predict a changed fixture before running again.

A complete review accounts for every named expected value and one deliberately incorrect alternative. A process exit by itself does not grade reasoning.
