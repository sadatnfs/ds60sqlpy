# java-002: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

A numeric type defines both a range and a set of operations. Java int arithmetic uses fixed-width signed integers and can wrap on overflow. Integer division discards the fractional part toward zero, while a floating-point operand changes the operation to approximate real-number arithmetic. A cast can narrow a value and lose information; it does not prove the value fits. BigDecimal represents decimal arithmetic with explicit precision and rounding choices, useful when exact decimal meaning matters. Construct it from text when the source is decimal text, because constructing from a binary floating-point value preserves that prior approximation. Choose types from the domain contract rather than from the apparent size of one example.

**Primitive:** A built-in value type such as int or boolean.

**Overflow:** A result outside the range of its chosen representation.

**Narrowing conversion:** A conversion that can lose range or precision.

## Reading the reference

L suffix creates a long literal. A widening conversion from int to long preserves the integer value, but the multiplication must occur after widening if it would overflow int. Math.addExact throws on overflow rather than wrapping. BigDecimal.add returns a new value because BigDecimal is immutable. compareTo compares numeric value, while equals also considers scale, so 1.0 and 1.00 need a declared equality policy.

## Exercise 1: Compare integer and decimal division: change one input

Task: Copy Example A into a scratch `Main.java` and change `int whole = 7 / 2;` to `int whole = 8 / 2;`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.

The operand types select the operation. Assigning 7/2 to a double afterward would preserve the already-truncated value 3.0.

The unchanged code is the part that Example A adds:

```java
int whole = 7 / 2;
double fractional = 7 / 2.0;
assert whole == 3 && fractional == 3.5;
```

**Expected:** The changed run fails with an `AssertionError` from the assertion on `whole == 3 && fractional == 3.5`. Restoring the original line brings back the worked observation: integer 3 and double 3.5.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `whole == 3 && fractional == 3.5` false. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Widen before multiplication: debug a regression

Task: A regression changed one token in the code that Example B adds after Example A, so one line now reads `long safe = (long) 50_000 + 50_000;`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.

The cast affects the multiplication itself. Casting the wrapped int result to long afterward cannot recover lost information.

The unchanged code is the part that Example B adds:

```java
long safe = (long) 50_000 * 50_000;
int wrapped = 50_000 * 50_000;
assert safe == 2_500_000_000L;
assert wrapped != safe;
```

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `safe == 2_500_000_000L`; after it the line reads `long safe = (long) 50_000 * 50_000;` again and 2500000000L; int product differs.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `safe == 2_500_000_000L` for this input.

## Exercise 3: Detect overflow explicitly

Task: Add 1 to Integer.MAX_VALUE with Math.addExact.

Exact arithmetic helpers turn silent wraparound into a named boundary failure. Use them when overflow violates the domain contract.

```java
boolean rejected = false;
try {
  Math.addExact(Integer.MAX_VALUE, 1);
} catch (ArithmeticException expected) {
  rejected = true;
}
assert rejected;
```

**Expected:** ArithmeticException.

**Verify:** Keep an assertion equivalent to `rejected`. As a control, change `rejected = true;` to `rejected = false;`: the run must fail with an `AssertionError` from the assertion on `rejected`. Restore the line before continuing.

## Exercise 4: Preserve decimal source meaning

Task: Add BigDecimal values constructed from strings 0.10 and 0.20.

Text construction preserves the supplied decimal digits. A binary floating-point constructor can introduce a long decimal expansion before the addition begins.

```java
var amount = new java.math.BigDecimal("0.10").add(new java.math.BigDecimal("0.20"));
assert amount.equals(new java.math.BigDecimal("0.30"));
```

**Expected:** exact decimal 0.30.

**Verify:** Keep an assertion equivalent to `amount.equals(new java.math.BigDecimal("0.30"))`. As a control, change `var amount = new java.math.BigDecimal("0.10").add(new java.math.BigDecimal("0.20"));` to `var amount = new java.math.BigDecimal("1.10").add(new java.math.BigDecimal("0.20"));`: the run must fail with an `AssertionError` from the assertion on `amount.equals(new java.math.BigDecimal("0.30"))`. Restore the line before continuing.

## Exercise 5: Distinguish value from scale

Task: Compare BigDecimal 1.0 and 1.00 with compareTo and equals.

The two objects have the same numeric value but different scale. Collection keys and domain equality need an explicit policy rather than a casual interchange of the two methods.

```java
var one = new java.math.BigDecimal("1.0");
var scaled = new java.math.BigDecimal("1.00");
assert one.compareTo(scaled) == 0 && !one.equals(scaled);
```

**Expected:** compareTo 0; equals false.

**Verify:** Keep an assertion equivalent to `one.compareTo(scaled) == 0 && !one.equals(scaled)`. As a control, change `var one = new java.math.BigDecimal("1.0");` to `var one = new java.math.BigDecimal("2.0");`: the run must fail with an `AssertionError` from the assertion on `one.compareTo(scaled) == 0 && !one.equals(scaled)`. Restore the line before continuing.

## Exercise 6: Reject an unsupported exact division

Task: Divide decimal 1 by 3 without a rounding policy, then supply scale 2 and HALF_UP.

One third has no finite decimal expansion. A rounding policy is part of the calculation definition, not merely a display setting.

```java
boolean repeating = false;
try {
  java.math.BigDecimal.ONE.divide(new java.math.BigDecimal("3"));
} catch (ArithmeticException expected) {
  repeating = true;
}
assert repeating;
assert java.math.BigDecimal.ONE.divide(
  new java.math.BigDecimal("3"),
  2,
  java.math.RoundingMode.HALF_UP
)
  .toPlainString()
  .equals("0.33");
```

**Expected:** exact division throws; rounded result 0.33.

**Verify:** Keep an assertion equivalent to `java.math.BigDecimal.ONE.divide(new java.math.BigDecimal("3"), 2, java.math.RoundingMode.HALF_UP).toPlainString().equals("0.33")`. As a control, change `2,` to `3,` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
