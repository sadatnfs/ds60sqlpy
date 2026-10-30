# java-017: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Optional represents the presence or absence of a value in a return contract. It can make a missing lookup explicit,but it does not replace every null or every domain error. An absent record is different from a malformed identifier,an unavailable service or a zero numeric value. UseOptional for an expected missing result and exceptions or a richer result type for invalid inputs and operational failures. A method returningOptional should not return null. Optional itself is a value container; callingget without checking simply moves an unchecked absence failure to a later line.

**Optional:** A container explicitly representing presence or absence.

**Domain error:** An input or operation violating the accepted business contract.

**Lazy fallback:** A fallback computation invoked only when the value is absent.

## Reading the reference

Optional.of rejects null,ofNullable maps null to empty,and map transforms only a present value. orElse evaluates its fallback argument eagerly,whileorElseGet invokes a supplier only when needed. flatMap avoids nestedOptional when the mapper already returns one. A boundary parser can validate text before performing a lookup so malformed input does not masquerade as an ordinary miss.

## Exercise 1: Represent a missing lookup

Task: Look up known a and unknown b in a fixed map through Optional.

The absence ofb is an expected lookup outcome. It is not represented as zero because zero could be a valid stored value.

```java
Map<String, Integer> data = Map.of("a", 7);
Optional<Integer> known = Optional.ofNullable(data.get("a"));
Optional<Integer> missing = Optional.ofNullable(data.get("b"));
assert known.orElseThrow() == 7 && missing.isEmpty();
```

**Expected:** a present with 7; b empty.

**Verify:** Compare the program values or named exception with a present with 7; b empty. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Transform only present values

Task: Map the known value to double and apply the same mapping to empty.

The mapping function is not called for an emptyOptional. This keeps the absence policy visible without repeated null conditionals.

```java
assert known.map(value -> value * 2).orElseThrow() == 14;
assert missing.map(value -> value * 2).isEmpty();
```

**Expected:** 14 and empty.

**Verify:** Compare the program values or named exception with 14 and empty. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Compare eager and lazy fallback

Task: Use a counter-producing fallback withorElse andorElseGet on a present value.

Method arguments are evaluated beforeorElse is invoked. A supplier delays the computation and avoids unnecessary expensive or side-effecting work.

```java
var calls = new java.util.concurrent.atomic.AtomicInteger();
assert known.orElse(calls.incrementAndGet()) == 7 && calls.get() == 1;
assert known.orElseGet(calls::incrementAndGet) == 7 && calls.get() == 1;
```

**Expected:** orElse increments;orElseGet does not.

**Verify:** Compare the program values or named exception with orElse increments;orElseGet does not. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Reject malformed lookup input

Task: Validate an empty identifier before consulting the map.

An invalid request and a valid request with no result are different outcomes. Conflating them makes error diagnosis and user feedback less precise.

```java
boolean invalid = false;
try {
  lookup(data, " ");
} catch (IllegalArgumentException expected) {
  invalid = true;
}
assert invalid && lookup(data, "b").isEmpty();
```

**Expected:** IllegalArgumentException rather than empty.

**Verify:** Compare the program values or named exception with IllegalArgumentException rather than empty. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Flatten a nullable transformation

Task: Parse an optional numeric string through a helper returningOptional<Integer>.

The helper deliberately treats parse failure as absence for this small API. A richer application may need to retain the error reason instead of discarding it.

```java
assert Optional.of("12").flatMap(Main::tryParse).orElseThrow() == 12;
assert Optional.of("bad").flatMap(Main::tryParse).isEmpty();
```

**Expected:** valid12 present;badtext empty under this declared parser policy.

**Verify:** Compare the program values or named exception with valid12 present;badtext empty under this declared parser policy. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Expose unsafeget

Task: Callget on empty and catchNoSuchElementException.

Optional does not make unchecked access safe. Prefer an explicit fallback,orElseThrow with context,or a branching operation that matches the caller contract.

```java
boolean absent = false;
try {
  Optional.empty().get();
} catch (NoSuchElementException expected) {
  absent = true;
}
assert absent;
```

**Expected:** specific absence failure.

**Verify:** Compare the program values or named exception with specific absence failure. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
