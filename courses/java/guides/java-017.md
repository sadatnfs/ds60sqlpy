# java-017: Optional values and validation boundaries

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-016`

## Learning objectives

Model optional results with Optional, choose eager or lazy fallbacks, and validate input at the boundary.

The six exercises practice these steps:

- Represent a missing lookup.
- Transform only present values.
- Compare eager and lazy fallback.
- Reject malformed lookup input.
- Flatten a nullable transformation.
- Expose unsafe get.

## Purpose and mental model

Optional represents the presence or absence of a value in a return contract. It can make a missing lookup explicit, but it does not replace every null or every domain error. An absent record is different from a malformed identifier, an unavailable service or a zero numeric value. Use Optional for an expected missing result and exceptions or a richer result type for invalid inputs and operational failures. A method returning Optional should not return null. Optional itself is a value container; calling get without checking simply moves an unchecked absence failure to a later line.

## Vocabulary and concepts

**Optional:** A container explicitly representing presence or absence.

**Domain error:** An input or operation violating the accepted business contract.

**Lazy fallback:** A fallback computation invoked only when the value is absent.

## How to run this lesson

All lookups use a fixed `Map.of` fixture and small helpers such as `lookup` and `tryParse`, so the only absences you see are the ones the exercises create deliberately.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

Optional.of rejects null, ofNullable maps null to empty, and map transforms only a present value. orElse evaluates its fallback argument eagerly, while orElseGet invokes a supplier only when needed. flatMap avoids nested Optional when the mapper already returns one. A boundary parser can validate text before performing a lookup so malformed input does not masquerade as an ordinary miss.

## Worked example / walkthrough

### Example A: Represent a missing lookup

The absence ofb is an expected lookup outcome. It is not represented as zero because zero could be a valid stored value.

```java
import java.util.*;

public class Main {

  static Optional<Integer> lookup(Map<String, Integer> data, String id) {
    if (id == null || id.isBlank()) throw new IllegalArgumentException("nonblank id required");
    return Optional.ofNullable(data.get(id));
  }

  static Optional<Integer> tryParse(String text) {
    try {
      return Optional.of(Integer.parseInt(text));
    } catch (NumberFormatException error) {
      return Optional.empty();
    }
  }

  public static void main(String[] args) throws Exception {
    Map<String, Integer> data = Map.of("a", 7);
    Optional<Integer> known = Optional.ofNullable(data.get("a"));
    Optional<Integer> missing = Optional.ofNullable(data.get("b"));
    assert known.orElseThrow() == 7 && missing.isEmpty();
  }
}
```

**Expected:** a present with 7; b empty.

### Example B: Transform only present values

The mapping function is not called for an empty Optional. This keeps the absence policy visible without repeated null conditionals.

```java
import java.util.*;

public class Main {

  static Optional<Integer> lookup(Map<String, Integer> data, String id) {
    if (id == null || id.isBlank()) throw new IllegalArgumentException("nonblank id required");
    return Optional.ofNullable(data.get(id));
  }

  static Optional<Integer> tryParse(String text) {
    try {
      return Optional.of(Integer.parseInt(text));
    } catch (NumberFormatException error) {
      return Optional.empty();
    }
  }

  public static void main(String[] args) throws Exception {
    Map<String, Integer> data = Map.of("a", 7);
    Optional<Integer> known = Optional.ofNullable(data.get("a"));
    Optional<Integer> missing = Optional.ofNullable(data.get("b"));
    assert known.orElseThrow() == 7 && missing.isEmpty();

    assert known.map(value -> value * 2).orElseThrow() == 14;
    assert missing.map(value -> value * 2).isEmpty();
  }
}
```

**Expected:** 14 and empty.

## Prediction before your attempt

Before running Example A, decide what `Optional.ofNullable(data.get("b"))` returns when the key is missing, and why returning 0 instead would be ambiguous. For Example B, predict the result of mapping the present 7 with `value -> value * 2` and of applying the same mapping to an empty `Optional`. Before Exercise 3, predict how many times the fallback supplier runs for `orElse` and for `orElseGet` when the value is present.

## Exercises

1. **Represent a missing lookup: change one input.** Change `Map<String, Integer> data = Map.of("a", 7);` to `Map<String, Integer> data = Map.of("a", 8);` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `known.orElseThrow() == 7 && missing.isEmpty()`.
   **Verify:** Name the value that makes `known.orElseThrow() == 7 && missing.isEmpty()` false, then restore the line.

2. **Transform only present values: diagnose an edited check.** Example B's new assertion was edited to `assert known.map(value -> value + 2).orElseThrow() == 14;`. Explain why it fails for unchanged state and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `known.map(value -> value * 2).orElseThrow() == 14`; the restored assertion passes.
   **Verify:** Explain why the edited assertion rejects the state that `known.map(value -> value * 2).orElseThrow() == 14` accepts.

3. **Compare eager and lazy fallback.** Use a counter-producing fallback with orElse and orElseGet on a present value.
   **Expected:** orElse increments; orElseGet does not.
   **Verify:** Control: changing `assert lazy == 7 && calls.get() == 1;` to `assert lazy != 7 && calls.get() == 1;` inside the assertion must make it fail.

4. **Reject malformed lookup input.** Validate an empty identifier before consulting the map.
   **Expected:** IllegalArgumentException rather than empty.
   **Verify:** Control: changing `invalid = true;` to `invalid = false;` must fail the assertion on `invalid && lookup(data, "b").isEmpty()`.

5. **Flatten a nullable transformation.** Parse an optional numeric string through a helper returning Optional<Integer>.
   **Expected:** valid 12 present; bad text empty under this declared parser policy.
   **Verify:** Control: changing `assert Optional.of("12").flatMap(Main::tryParse).orElseThrow() == 12;` to `assert Optional.of("13").flatMap(Main::tryParse).orElseThrow() == 12;` inside the assertion must make it fail.

6. **Expose unsafe get.** Call get on empty and catchNoSuchElementException.
   **Expected:** specific absence failure.
   **Verify:** Control: changing `absent = true;` to `absent = false;` must fail the assertion on `absent`.

## Common pitfalls and diagnosis

`orElse(expensive())` always evaluates its argument, even when the value is present, because Java evaluates arguments before the call; use `orElseGet` for costly or side-effecting fallbacks. Calling `get()` without a check simply moves the absence failure to `NoSuchElementException` on a later line. A method that returns `Optional` must never return null. Finally, an empty `Optional` should mean "no result", not "bad request": validate malformed input separately and throw.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the edit stores 8 under the key "a". Then read `known.orElseThrow()` and compare it with the 7 the assertion expects. Finally, confirm that the missing key "b" still yields an empty `Optional`, so only the first conjunct fails.
- **Exercise 2:** First apply the edited lambda `value -> value + 2` to the present 7. Then compare the result with the 14 in the assertion. Finally, explain why the empty case would not reveal this mistake: `map` never calls the function on an empty value.
- **Exercise 3:** First let an `AtomicInteger` named `calls` produce the fallback through `incrementAndGet`. Then pass `calls.incrementAndGet()` to `orElse` and the reference `calls::incrementAndGet` to `orElseGet`, both on the present 7. Finally, assert that the counter is 1 after both calls, so only the eager argument ran.
- **Exercise 4:** First reject a blank identifier in `lookup` with `IllegalArgumentException` before touching the map. Then call it with a single space inside a `try` block. Finally, assert that a well-formed missing key such as "b" still returns an empty `Optional`.
- **Exercise 5:** First write `tryParse` so that it returns `Optional.of(value)` on success and `Optional.empty()` on `NumberFormatException`. Then call it through `flatMap` on `Optional.of("12")` and on bad text. Finally, explain why `map` would have produced a nested `Optional<Optional<Integer>>`.
- **Exercise 6:** First call `get()` on `Optional.empty()` inside a `try` block. Then catch `NoSuchElementException` and record it. Finally, name the safer call you would use instead and the context it lets you add.

## Self-check and retrieval

Without the guide, state when `Optional` is the right return type and when an exception is better, using the lookup and the empty identifier as examples. Explain the difference between `map` and `flatMap`, why `orElse` runs its argument eagerly, and what `orElseThrow` adds over `get`.

## Next step

Continue with `java-018`: Tests that detect broken behavior. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Optional.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-017: Optional values and validation boundaries.
Read courses/java/guides/java-017.md and courses/java/lessons/java-017.java. Direct prerequisites: `java-016`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
