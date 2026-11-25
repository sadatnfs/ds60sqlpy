# java-017: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

Optional represents the presence or absence of a value in a return contract. It can make a missing lookup explicit, but it does not replace every null or every domain error. An absent record is different from a malformed identifier, an unavailable service or a zero numeric value. Use Optional for an expected missing result and exceptions or a richer result type for invalid inputs and operational failures. A method returning Optional should not return null. Optional itself is a value container; calling get without checking simply moves an unchecked absence failure to a later line.

**Optional:** A container explicitly representing presence or absence.

**Domain error:** An input or operation violating the accepted business contract.

**Lazy fallback:** A fallback computation invoked only when the value is absent.

## Reading the reference

Optional.of rejects null, ofNullable maps null to empty, and map transforms only a present value. orElse evaluates its fallback argument eagerly, while orElseGet invokes a supplier only when needed. flatMap avoids nested Optional when the mapper already returns one. A boundary parser can validate text before performing a lookup so malformed input does not masquerade as an ordinary miss.

## Exercise 1: Represent a missing lookup: change one input

Task: Change `Map<String, Integer> data = Map.of("a", 7);` to `Map<String, Integer> data = Map.of("a", 8);` in Example A and predict which assertion fails and why.

The absence ofb is an expected lookup outcome. It is not represented as zero because zero could be a valid stored value.

The unchanged code is the part that Example A adds:

```java
Map<String, Integer> data = Map.of("a", 7);
Optional<Integer> known = Optional.ofNullable(data.get("a"));
Optional<Integer> missing = Optional.ofNullable(data.get("b"));
assert known.orElseThrow() == 7 && missing.isEmpty();
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `known.orElseThrow() == 7 && missing.isEmpty()`.

**Verify:** Name the value that makes `known.orElseThrow() == 7 && missing.isEmpty()` false, then restore the line.

## Exercise 2: Transform only present values: diagnose an edited check

Task: Example B's new assertion was edited to `assert known.map(value -> value + 2).orElseThrow() == 14;`. Explain why it fails for unchanged state and restore it.

The mapping function is not called for an empty Optional. This keeps the absence policy visible without repeated null conditionals.

The unchanged code is the part that Example B adds:

```java
assert known.map(value -> value * 2).orElseThrow() == 14;
assert missing.map(value -> value * 2).isEmpty();
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `known.map(value -> value * 2).orElseThrow() == 14`; the restored assertion passes.

**Verify:** Explain why the edited assertion rejects the state that `known.map(value -> value * 2).orElseThrow() == 14` accepts.

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

**Verify:** Control: changing `assert lazy == 7 && calls.get() == 1;` to `assert lazy != 7 && calls.get() == 1;` inside the assertion must make it fail.

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

**Verify:** Control: changing `invalid = true;` to `invalid = false;` must fail the assertion on `invalid && lookup(data, "b").isEmpty()`.

## Exercise 5: Flatten a nullable transformation

Task: Parse an optional numeric string through a helper returning Optional<Integer>.

The helper deliberately treats parse failure as absence for this small API. A richer application may need to retain the error reason instead of discarding it.

```java
assert Optional.of("12").flatMap(Main::tryParse).orElseThrow() == 12;
assert Optional.of("bad").flatMap(Main::tryParse).isEmpty();
```

**Expected:** valid 12 present; bad text empty under this declared parser policy.

**Verify:** Control: changing `assert Optional.of("12").flatMap(Main::tryParse).orElseThrow() == 12;` to `assert Optional.of("13").flatMap(Main::tryParse).orElseThrow() == 12;` inside the assertion must make it fail.

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

**Verify:** Control: changing `absent = true;` to `absent = false;` must fail the assertion on `absent`.

## After comparing the answer

Change `tryParse` in your copy to return a small result record that keeps the parse error message, and decide which callers in this lesson actually need that extra information.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
