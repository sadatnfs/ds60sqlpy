# java-002: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

A numeric type defines both a range and a set of operations. Java int arithmetic uses fixed-width signed integers and can wrap on overflow. Integer division discards the fractional part toward zero, while a floating-point operand changes the operation to approximate real-number arithmetic. A cast can narrow a value and lose information; it does not prove the value fits. BigDecimal represents decimal arithmetic with explicit precision and rounding choices, useful when exact decimal meaning matters. Construct it from text when the source is decimal text, because constructing from a binary floating-point value preserves that prior approximation. Choose types from the domain contract rather than from the apparent size of one example.

**Primitive:** A built-in value type such as int or boolean.

**Overflow:** A result outside the range of its chosen representation.

**Narrowing conversion:** A conversion that can lose range or precision.

## Reading the reference

L suffix creates a long literal. A widening conversion from int to long preserves the integer value, but the multiplication must occur after widening if it would overflow int. Math.addExact throws on overflow rather than wrapping. BigDecimal.add returns a new value because BigDecimal is immutable. compareTo compares numeric value, while equals also considers scale, so 1.0 and 1.00 need a declared equality policy.

## Exercise 1: Compare integer and decimal division: change one input

Task: Change `int whole = 7 / 2;` to `int whole = 8 / 2;` in Example A and predict which assertion fails and why.

The operand types select the operation. Assigning 7/2 to a double afterward would preserve the already-truncated value 3.0.

The unchanged code is the part that Example A adds:

```java
int whole = 7 / 2;
double fractional = 7 / 2.0;
assert whole == 3 && fractional == 3.5;
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `whole == 3 && fractional == 3.5`.

**Verify:** Name the value that makes `whole == 3 && fractional == 3.5` false, then restore the line.

## Exercise 2: Widen before multiplication: debug a regression

Task: A regression in Example B's new code makes one line read `long safe = (long) 50_000 + 50_000;`. Repair it using the failing assertion.

The cast affects the multiplication itself. Casting the wrapped int result to long afterward cannot recover lost information.

The unchanged code is the part that Example B adds:

```java
long safe = (long) 50_000 * 50_000;
int wrapped = 50_000 * 50_000;
assert safe == 2_500_000_000L;
assert wrapped != safe;
```

**Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `safe == 2_500_000_000L`; the repaired line reads `long safe = (long) 50_000 * 50_000;`.

**Verify:** Explain how the changed token alters the value that `safe == 2_500_000_000L` tests.

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

**Verify:** Control: changing `rejected = true;` to `rejected = false;` must fail the assertion on `rejected`.

## Exercise 4: Preserve decimal source meaning

Task: Add BigDecimal values constructed from strings 0.10 and 0.20.

Text construction preserves the supplied decimal digits. A binary floating-point constructor can introduce a long decimal expansion before the addition begins.

```java
var amount = new java.math.BigDecimal("0.10").add(new java.math.BigDecimal("0.20"));
assert amount.equals(new java.math.BigDecimal("0.30"));
```

**Expected:** exact decimal 0.30.

**Verify:** Control: changing `var amount = new java.math.BigDecimal("0.10").add(new java.math.BigDecimal("0.20"));` to `var amount = new java.math.BigDecimal("1.10").add(new java.math.BigDecimal("0.20"));` must fail the assertion on `amount.equals(new java.math.BigDecimal("0.30"))`.

## Exercise 5: Distinguish value from scale

Task: Compare BigDecimal 1.0 and 1.00 with compareTo and equals.

The two objects have the same numeric value but different scale. Collection keys and domain equality need an explicit policy rather than a casual interchange of the two methods.

```java
var one = new java.math.BigDecimal("1.0");
var scaled = new java.math.BigDecimal("1.00");
assert one.compareTo(scaled) == 0 && !one.equals(scaled);
```

**Expected:** compareTo 0; equals false.

**Verify:** Control: changing `var one = new java.math.BigDecimal("1.0");` to `var one = new java.math.BigDecimal("2.0");` must fail the assertion on `one.compareTo(scaled) == 0 && !one.equals(scaled)`.

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

**Verify:** Control: changing `2,` to `3,` inside the assertion must make it fail.

## After comparing the answer

Add one more boundary to your copy: subtract 1 from `Integer.MIN_VALUE` with `Math.subtractExact`, predict the exception, and compare it with what plain `-` does to the same value.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
