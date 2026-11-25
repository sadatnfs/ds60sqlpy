# java-002: Values, numeric types and conversion

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-001`

## Learning objectives

Predict integer and decimal arithmetic, widen before overflow, and use BigDecimal value and scale deliberately.

The six exercises practice these steps:

- Compare integer and decimal division.
- Widen before multiplication.
- Detect overflow explicitly.
- Preserve decimal source meaning.
- Distinguish value from scale.
- Reject an unsupported exact division.

## Purpose and mental model

A numeric type defines both a range and a set of operations. Java int arithmetic uses fixed-width signed integers and can wrap on overflow. Integer division discards the fractional part toward zero, while a floating-point operand changes the operation to approximate real-number arithmetic. A cast can narrow a value and lose information; it does not prove the value fits. BigDecimal represents decimal arithmetic with explicit precision and rounding choices, useful when exact decimal meaning matters. Construct it from text when the source is decimal text, because constructing from a binary floating-point value preserves that prior approximation. Choose types from the domain contract rather than from the apparent size of one example.

## Vocabulary and concepts

**Primitive:** A built-in value type such as int or boolean.

**Overflow:** A result outside the range of its chosen representation.

**Narrowing conversion:** A conversion that can lose range or precision.

## How to run this lesson

Every check here is arithmetic on literals, so any surprise you see comes from the types you chose and when conversions happen, never from input or the environment.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

L suffix creates a long literal. A widening conversion from int to long preserves the integer value, but the multiplication must occur after widening if it would overflow int. Math.addExact throws on overflow rather than wrapping. BigDecimal.add returns a new value because BigDecimal is immutable. compareTo compares numeric value, while equals also considers scale, so 1.0 and 1.00 need a declared equality policy.

## Worked example / walkthrough

### Example A: Compare integer and decimal division

The operand types select the operation. Assigning 7/2 to a double afterward would preserve the already-truncated value 3.0.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    int whole = 7 / 2;
    double fractional = 7 / 2.0;
    assert whole == 3 && fractional == 3.5;
  }
}
```

**Expected:** integer 3 and double 3.5.

### Example B: Widen before multiplication

The cast affects the multiplication itself. Casting the wrapped int result to long afterward cannot recover lost information.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    int whole = 7 / 2;
    double fractional = 7 / 2.0;
    assert whole == 3 && fractional == 3.5;

    long safe = (long) 50_000 * 50_000;
    int wrapped = 50_000 * 50_000;
    assert safe == 2_500_000_000L;
    assert wrapped != safe;
  }
}
```

**Expected:** 2500000000L; int product differs.

## Prediction before your attempt

Before running Example A, write the values of `7 / 2` and `7 / 2.0` and the type of each result. For Example B, predict what `50_000 * 50_000` gives as an `int` (it wraps to a negative number, because the true product exceeds `Integer.MAX_VALUE`) and whether casting that product to `long` afterward repairs it. Then predict whether `new BigDecimal("1.0").equals(new BigDecimal("1.00"))` is true before Exercise 5 shows you.

## Exercises

1. **Compare integer and decimal division: change one input.** Change `int whole = 7 / 2;` to `int whole = 8 / 2;` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `whole == 3 && fractional == 3.5`.
   **Verify:** Name the value that makes `whole == 3 && fractional == 3.5` false, then restore the line.

2. **Widen before multiplication: debug a regression.** A regression in Example B's new code makes one line read `long safe = (long) 50_000 + 50_000;`. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `safe == 2_500_000_000L`; the repaired line reads `long safe = (long) 50_000 * 50_000;`.
   **Verify:** Explain how the changed token alters the value that `safe == 2_500_000_000L` tests.

3. **Detect overflow explicitly.** Add 1 to Integer.MAX_VALUE with Math.addExact.
   **Expected:** ArithmeticException.
   **Verify:** Control: changing `rejected = true;` to `rejected = false;` must fail the assertion on `rejected`.

4. **Preserve decimal source meaning.** Add BigDecimal values constructed from strings 0.10 and 0.20.
   **Expected:** exact decimal 0.30.
   **Verify:** Control: changing `var amount = new java.math.BigDecimal("0.10").add(new java.math.BigDecimal("0.20"));` to `var amount = new java.math.BigDecimal("1.10").add(new java.math.BigDecimal("0.20"));` must fail the assertion on `amount.equals(new java.math.BigDecimal("0.30"))`.

5. **Distinguish value from scale.** Compare BigDecimal 1.0 and 1.00 with compareTo and equals.
   **Expected:** compareTo 0; equals false.
   **Verify:** Control: changing `var one = new java.math.BigDecimal("1.0");` to `var one = new java.math.BigDecimal("2.0");` must fail the assertion on `one.compareTo(scaled) == 0 && !one.equals(scaled)`.

6. **Reject an unsupported exact division.** Divide decimal 1 by 3 without a rounding policy, then supply scale 2 and HALF_UP.
   **Expected:** exact division throws; rounded result 0.33.
   **Verify:** Control: changing `2,` to `3,` inside the assertion must make it fail.

## Common pitfalls and diagnosis

The most common mistake is converting too late. `(long) (a * b)` widens an `int` product that has already wrapped, while `(long) a * b` widens before the multiplication. The same timing error explains `double half = 7 / 2`, which stores 3.0 because the integer division ran first. With `BigDecimal`, constructing from a `double` such as `new BigDecimal(0.1)` copies the binary approximation into the decimal, and `equals` compares scale as well as numeric value, so `1.0` and `1.00` are different keys in a `HashMap`.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First evaluate `8 / 2` as integer division; it divides evenly, so nothing is truncated. Then compare that value with the 3 the assertion expects, remembering that `fractional` is unchanged. Finally, explain why the original `7 / 2` produced 3 rather than 3.5.
- **Exercise 2:** First compute what the edited line stores in `safe`: the cast still widens the left operand, but the operator now adds. Then compare that sum with 2,500,000,000. Finally, restore the multiplication and explain why the cast must apply to an operand rather than to the finished product.
- **Exercise 3:** First call `Math.addExact(Integer.MAX_VALUE, 1)` inside a `try` block. Then catch `ArithmeticException` and set `rejected` to true in the handler. Finally, compare with `Integer.MAX_VALUE + 1`, which silently wraps to `Integer.MIN_VALUE`, to see what the exact helper protects you from.
- **Exercise 4:** First construct both operands from the strings `"0.10"` and `"0.20"` rather than from `double` literals. Then combine them with `add`, which keeps every decimal digit. Finally, compare the sum with a `BigDecimal` built from `"0.30"`; `equals` works here because both sides have scale 2.
- **Exercise 5:** First write down the unscaled value and the scale of `1.0` and of `1.00`. Then call `compareTo`, which compares only numeric value, and `equals`, which also compares scale. Finally, decide which of the two methods a sorted set and a hash map would each rely on.
- **Exercise 6:** First call `divide` with only the divisor and expect `ArithmeticException`, because one third has no finite decimal expansion. Then call the overload that takes a scale of 2 and `RoundingMode.HALF_UP`. Finally, compare `toPlainString()` of the result with `"0.33"` and explain why the rounding policy belongs to the calculation.

## Self-check and retrieval

From memory, explain why `7 / 2` is 3 but `7 / 2.0` is 3.5, where `int` overflow happens in `50_000 * 50_000` and how `Math.addExact` changes what you observe, and why `1.0` and `1.00` compare as equal with `compareTo` but not with `equals`.

## Next step

Continue with `java-003`: Decisions, loops and invariants. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-002: Values, numeric types and conversion.
Read courses/java/guides/java-002.md and courses/java/lessons/java-002.java. Direct prerequisites: `java-001`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
