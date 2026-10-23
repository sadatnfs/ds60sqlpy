# java-002: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

A numeric type defines both a range and a set of operations. Java int arithmetic uses fixed-width signed integers and can wrap on overflow. Integer division discards the fractional part toward zero, while a floating-point operand changes the operation to approximate real-number arithmetic. A cast can narrow a value and lose information; it does not prove the value fits. BigDecimal represents decimal arithmetic with explicit precision and rounding choices, useful when exact decimal meaning matters. Construct it from text when the source is decimal text, because constructing from a binary floating-point value preserves that prior approximation. Choose types from the domain contract rather than from the apparent size of one example.

**Primitive:** A built-in value type such asint orboolean.

**Overflow:** A result outside the range of its chosen representation.

**Narrowing conversion:** A conversion that can lose range or precision.

## Reading the reference

L suffix creates a long literal. A widening conversion fromint tolong preserves the integer value, but the multiplication must occur after widening if it would overflowint. Math.addExact throws on overflow rather than wrapping. BigDecimal.add returns a new value because BigDecimal is immutable. compareTo compares numeric value, while equals also considers scale, so1.0 and1.00 need a declared equality policy.

## Exercise 1: Compare integer and decimal division

Task: Calculate7/2 and7/2.0.

The operand types select the operation. Assigning7/2 to a double afterward would preserve the already-truncated value3.0.

```java
int whole = 7 / 2;
double fractional = 7 / 2.0;
assert whole == 3 && fractional == 3.5;
```

**Expected:** integer3 and double3.5.

**Verify:** Compare the program values or named exception with integer3 and double3.5. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Widen before multiplication

Task: Compute50000 squared with an explicitly widened left operand.

The cast affects the multiplication itself. Casting the wrappedint result tolong afterward cannot recover lost information.

```java
long safe = (long) 50_000 * 50_000;
int wrapped = 50_000 * 50_000;
assert safe == 2_500_000_000L;
assert wrapped != safe;
```

**Expected:** 2500000000L;int product differs.

**Verify:** Compare the program values or named exception with 2500000000L;int product differs. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Detect overflow explicitly

Task: Add1 to Integer.MAX_VALUE withMath.addExact.

Exact arithmetic helpers turn silent wraparound into a named boundary failure. Use them when overflow violates the domain contract.

```java
boolean rejected = false;
try { Math.addExact(Integer.MAX_VALUE, 1); }
catch (ArithmeticException expected) { rejected = true; }
assert rejected;
```

**Expected:** ArithmeticException.

**Verify:** Compare the program values or named exception with ArithmeticException. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Preserve decimal source meaning

Task: Add BigDecimal values constructed from strings0.10 and0.20.

Text construction preserves the supplied decimal digits. A binary floating-point constructor can introduce a long decimal expansion before the addition begins.

```java
var amount = new java.math.BigDecimal("0.10").add(new java.math.BigDecimal("0.20"));
assert amount.equals(new java.math.BigDecimal("0.30"));
```

**Expected:** exact decimal0.30.

**Verify:** Compare the program values or named exception with exact decimal0.30. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Distinguish value from scale

Task: Compare BigDecimal1.0 and1.00 withcompareTo andequals.

The two objects have the same numeric value but different scale. Collection keys and domain equality need an explicit policy rather than a casual interchange of the two methods.

```java
var one = new java.math.BigDecimal("1.0");
var scaled = new java.math.BigDecimal("1.00");
assert one.compareTo(scaled) == 0 && !one.equals(scaled);
```

**Expected:** compareTo0;equalsfalse.

**Verify:** Compare the program values or named exception with compareTo0;equalsfalse. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Reject an unsupported exact division

Task: Divide decimal1 by3 without a rounding policy, then supply scale2 andHALF_UP.

One third has no finite decimal expansion. A rounding policy is part of the calculation definition, not merely a display setting.

```java
boolean repeating = false;
try { java.math.BigDecimal.ONE.divide(new java.math.BigDecimal("3")); }
catch (ArithmeticException expected) { repeating = true; }
assert repeating;
assert java.math.BigDecimal.ONE.divide(new java.math.BigDecimal("3"), 2, java.math.RoundingMode.HALF_UP).toPlainString().equals("0.33");
```

**Expected:** exact division throws;rounded result0.33.

**Verify:** Compare the program values or named exception with exact division throws;rounded result0.33. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
