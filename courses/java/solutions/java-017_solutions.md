# java-017: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Optional represents the presence or absence of a value in a return contract. It can make a missing lookup explicit, but it does not replace every null or every domain error. An absent record is different from a malformed identifier, an unavailable service or a zero numeric value. Use Optional for an expected missing result and exceptions or a richer result type for invalid inputs and operational failures. A method returning Optional should not return null. Optional itself is a value container; calling get without checking simply moves an unchecked absence failure to a later line.

**Optional:** A container explicitly representing presence or absence.

**Domain error:** An input or operation violating the accepted business contract.

**Lazy fallback:** A fallback computation invoked only when the value is absent.

## Reading the reference

Optional.of rejects null, ofNullable maps null to empty, and map transforms only a present value. orElse evaluates its fallback argument eagerly, while orElseGet invokes a supplier only when needed. flatMap avoids nested Optional when the mapper already returns one. A boundary parser can validate text before performing a lookup so malformed input does not masquerade as an ordinary miss.

## Exercise 1: Represent a missing lookup: change one input

Task: Copy Example A into a scratch `Main.java` and change `Map<String, Integer> data = Map.of("a", 7);` to `Map<String, Integer> data = Map.of("a", 8);`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.

The absence ofb is an expected lookup outcome. It is not represented as zero because zero could be a valid stored value.

The unchanged code is the part that Example A adds:

```java
Map<String, Integer> data = Map.of("a", 7);
Optional<Integer> known = Optional.ofNullable(data.get("a"));
Optional<Integer> missing = Optional.ofNullable(data.get("b"));
assert known.orElseThrow() == 7 && missing.isEmpty();
```

**Expected:** The changed run fails with an `AssertionError` from the assertion on `known.orElseThrow() == 7 && missing.isEmpty()`. Restoring the original line brings back the worked observation: a present with 7; b empty.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `known.orElseThrow() == 7 && missing.isEmpty()` false. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Transform only present values: diagnose an edited check

Task: A careless edit changed the assertion that Example B adds after Example A so that it reads `assert known.map(value -> value + 2).orElseThrow() == 14;`. Run Example B with that line, explain why the edited assertion now fails for the same program state, and restore it.

The mapping function is not called for an empty Optional. This keeps the absence policy visible without repeated null conditionals.

The unchanged code is the part that Example B adds:

```java
assert known.map(value -> value * 2).orElseThrow() == 14;
assert missing.map(value -> value * 2).isEmpty();
```

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `known.map(value -> value * 2).orElseThrow() == 14`; after it the line reads `assert known.map(value -> value * 2).orElseThrow() == 14;` again and 14 and empty.

**Verify:** Keep the failing and the repaired runs. Explain why the edited assertion rejects the same program state that `known.map(value -> value * 2).orElseThrow() == 14` accepts.

## Exercise 3: Compare eager and lazy fallback

Task: Use a counter-producing fallback with orElse and orElseGet on a present value.

Method arguments are evaluated before orElse is invoked. A supplier delays the computation and avoids unnecessary expensive or side-effecting work.

```java
var calls = new java.util.concurrent.atomic.AtomicInteger();
int eager = known.orElse(calls.incrementAndGet());
assert eager == 7 && calls.get() == 1;
int lazy = known.orElseGet(calls::incrementAndGet);
assert lazy == 7 && calls.get() == 1;
```

**Expected:** orElse increments; orElseGet does not.

**Verify:** Keep an assertion equivalent to `lazy == 7 && calls.get() == 1`. As a control, change `assert lazy == 7 && calls.get() == 1;` to `assert lazy != 7 && calls.get() == 1;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

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

**Verify:** Keep an assertion equivalent to `invalid && lookup(data, "b").isEmpty()`. As a control, change `invalid = true;` to `invalid = false;`: the run must fail with an `AssertionError` from the assertion on `invalid && lookup(data, "b").isEmpty()`. Restore the line before continuing.

## Exercise 5: Flatten a nullable transformation

Task: Parse an optional numeric string through a helper returning Optional<Integer>.

The helper deliberately treats parse failure as absence for this small API. A richer application may need to retain the error reason instead of discarding it.

```java
assert Optional.of("12").flatMap(Main::tryParse).orElseThrow() == 12;
assert Optional.of("bad").flatMap(Main::tryParse).isEmpty();
```

**Expected:** valid 12 present; bad text empty under this declared parser policy.

**Verify:** Keep an assertion equivalent to `Optional.of("12").flatMap(Main::tryParse).orElseThrow() == 12`. As a control, change `assert Optional.of("12").flatMap(Main::tryParse).orElseThrow() == 12;` to `assert Optional.of("13").flatMap(Main::tryParse).orElseThrow() == 12;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

## Exercise 6: Expose unsafe get

Task: Call get on empty and catchNoSuchElementException.

Optional does not make unchecked access safe. Prefer an explicit fallback, orElseThrow with context, or a branching operation that matches the caller contract.

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

**Verify:** Keep an assertion equivalent to `absent`. As a control, change `absent = true;` to `absent = false;`: the run must fail with an `AssertionError` from the assertion on `absent`. Restore the line before continuing.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
