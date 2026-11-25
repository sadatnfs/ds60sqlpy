# java-034: Application design and dependency boundaries

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-033`

## Learning objectives

Separate pure domain logic from infrastructure so validation and failures are testable before any repository call.

The six exercises practice these steps:

- Test the pure calculation.
- Compose a deterministic service.
- Reject an unknown catalog item.
- Propagate an infrastructure failure.
- Prove invalid quantity fails before a repository call.
- Detect arithmetic overflow without an event.

## Purpose and mental model

Application design separates domain decisions from the mechanisms that supply data, time or side effects. A pure pricing calculation can be tested without a database, network or system clock. A service composes that calculation with repository and clock ports. Adapters implement those ports for a particular environment. Dependency inversion means the domain-facing code depends on the behavior it needs rather than on a concrete infrastructure class.

This lesson builds a small quote service. A catalog port supplies integer-cent prices, a fixed clock supplies the timestamp, and an audit sink records successful operations in memory. The service validates quantity and catalog lookup before producing a result or recording an event. A failing repository propagates its failure rather than returning a fabricated zero price. Thefake-backed tests establish service logic and call boundaries, not live database or network acceptance.

## Vocabulary and concepts

**Port:** A behavior interface required by application logic.

**Adapter:** An implementation connecting a port to a concrete mechanism.

**Pure core:** Domain calculations independent of infrastructure side effects.

**Dependency inversion:** Depending on required behavior rather than concrete external machinery.

## How to run this lesson

The quote service takes three plain Java ports, a `Catalog` lambda, a clock `Supplier` and an audit `Consumer`, so every check runs in memory with a fixed instant and no database, network or system clock.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

Define a Catalog interface returning OptionalLong and declaring IOException for an operational read failure. Inject a Supplier<Instant> and Consumer<String> through the constructor. Keep the pure total calculation separate and use Math.multiplyExact for overflow. The Quote record carries item, quantity, total and time. Audit only after all required validation and calculation succeed.

## Worked example / walkthrough

### Example A: Test the pure calculation

The core arithmetic needs no repository or clock. Isolating it makes domain boundaries and overflow behavior easy to check.

```java
import java.util.*;

public class Main {

  interface Catalog {
    java.util.OptionalLong unitPrice(String id) throws java.io.IOException;
  }

  record Quote(String item, int quantity, long totalCents, java.time.Instant created) {}

  static long total(int quantity, long unitPrice) {
    if (quantity <= 0 || unitPrice < 0) throw new IllegalArgumentException(
      "positive quantity and nonnegative price required"
    );
    return Math.multiplyExact((long) quantity, unitPrice);
  }

  record Service(
    Catalog catalog,
    java.util.function.Supplier<java.time.Instant> clock,
    java.util.function.Consumer<String> audit
  ) {
    Service {
      Objects.requireNonNull(catalog);
      Objects.requireNonNull(clock);
      Objects.requireNonNull(audit);
    }

    Quote quote(String id, int quantity) throws java.io.IOException {
      if (id == null || id.isBlank() || quantity <= 0) throw new IllegalArgumentException(
        "valid item and quantity required"
      );
      long price = catalog
        .unitPrice(id)
        .orElseThrow(() -> new NoSuchElementException("unknown item"));
      long amount = total(quantity, price);
      Quote result = new Quote(id, quantity, amount, clock.get());
      audit.accept("quoted:" + id);
      return result;
    }
  }

  public static void main(String[] args) throws Exception {
    assert total(3, 125) == 375;
    boolean invalid = false;
    try {
      total(0, 125);
    } catch (IllegalArgumentException expected) {
      invalid = true;
    }
    assert invalid;
  }
}
```

**Expected:** 375 cents; nonpositive quantity rejected.

### Example B: Compose a deterministic service

A fixed clock removes timing nondeterminism. The audit event is a local test double, not a message sent to another person or service.

```java
import java.util.*;

public class Main {

  interface Catalog {
    java.util.OptionalLong unitPrice(String id) throws java.io.IOException;
  }

  record Quote(String item, int quantity, long totalCents, java.time.Instant created) {}

  static long total(int quantity, long unitPrice) {
    if (quantity <= 0 || unitPrice < 0) throw new IllegalArgumentException(
      "positive quantity and nonnegative price required"
    );
    return Math.multiplyExact((long) quantity, unitPrice);
  }

  record Service(
    Catalog catalog,
    java.util.function.Supplier<java.time.Instant> clock,
    java.util.function.Consumer<String> audit
  ) {
    Service {
      Objects.requireNonNull(catalog);
      Objects.requireNonNull(clock);
      Objects.requireNonNull(audit);
    }

    Quote quote(String id, int quantity) throws java.io.IOException {
      if (id == null || id.isBlank() || quantity <= 0) throw new IllegalArgumentException(
        "valid item and quantity required"
      );
      long price = catalog
        .unitPrice(id)
        .orElseThrow(() -> new NoSuchElementException("unknown item"));
      long amount = total(quantity, price);
      Quote result = new Quote(id, quantity, amount, clock.get());
      audit.accept("quoted:" + id);
      return result;
    }
  }

  public static void main(String[] args) throws Exception {
    assert total(3, 125) == 375;
    boolean invalid = false;
    try {
      total(0, 125);
    } catch (IllegalArgumentException expected) {
      invalid = true;
    }
    assert invalid;

    List<String> audit = new ArrayList<>();
    var instant = java.time.Instant.parse("2026-01-01T00:00:00Z");
    Catalog catalog = id ->
      id.equals("item-a") ? java.util.OptionalLong.of(125) : java.util.OptionalLong.empty();
    Service service = new Service(catalog, () -> instant, audit::add);
    Quote quote = service.quote("item-a", 2);
    assert quote.totalCents() == 250 &&
    quote.created().equals(instant) &&
    audit.equals(List.of("quoted:item-a"));
  }
}
```

**Expected:** total 250, time 2026-01-01T00:00:00Z, one audit event.

## Prediction before your attempt

Before running Example A, compute `total(3, 125)` and decide what `total(0, 125)` does. For Example B, predict the total, the timestamp and the audit list after `quote("item-a", 2)` with a fixed clock. Before Exercise 5, decide how many times the catalog is called when the quantity is -1, given the order of checks inside `quote`.

## Exercises

1. **Test the pure calculation: change one input.** Change `total(0, 125);` to `total(1, 125);` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `invalid`.
   **Verify:** Name the value that makes `invalid` false, then restore the line.

2. **Compose a deterministic service: debug a regression.** A regression in Example B's new code makes one line read `id.equals("item-a") ? java.util.OptionalLong.of(126) : java.util.OptionalLong.empty();`. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `quote.totalCents() == 250 && quote.created().equals(instant) && audit.equals(List.of("quoted:item-a"))`; the repaired line reads `id.equals("item-a") ? java.util.OptionalLong.of(125) : java.util.OptionalLong.empty();`.
   **Verify:** Explain how the changed token alters the value that `quote.totalCents() == 250 && quote.created().equals(instant) && audit.equals(List.of("quoted:item-a"))` tests.

3. **Reject an unknown catalog item.** Request missing and inspect the audit list.
   **Expected:** NoSuchElementException; no additional audit.
   **Verify:** Control: changing `missing = true;` to `missing = false;` must fail the assertion on `missing && audit.size() == 1`.

4. **Propagate an infrastructure failure.** Inject a Catalog thatthrowsIOException.
   **Expected:** same failure type; no success audit.
   **Verify:** Control: changing `throw new java.io.IOException("catalog unavailable");` to `throw new java.io.IOException("catalog unavailable!");` must fail the assertion on `propagated && failures.isEmpty()`.

5. **Prove invalid quantity fails before a repository call.** Use a counting catalog and request negative quantity.
   **Expected:** repository call count 0.
   **Verify:** Control: changing `rejected = true;` to `rejected = false;` must fail the assertion on `rejected && calls.get() == 0`.

6. **Detect arithmetic overflow without an event.** Use a Long.MAX_VALUE unit price and quantity 2.
   **Expected:** ArithmeticException; audit sink unused.
   **Verify:** Control: changing `overflow = true;` to `overflow = false;` must fail the assertion on `overflow && overflowAudit.isEmpty()`.

## Common pitfalls and diagnosis

A service that calls `Instant.now()` or opens its own connection cannot be tested deterministically; inject the clock and the catalog instead. Turning a missing item into a zero price hides a real outcome, and catching an `IOException` to return a default hides an outage. Writing the audit event before the arithmetic finishes records success for a failed request. And plain `*` on `long` wraps silently on overflow, while `Math.multiplyExact` throws.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the edit calls `total(1, 125)` inside the `try` block. Then decide whether a quantity of 1 passes the positive quantity rule. Finally, explain why nothing is thrown, `invalid` stays false and the assertion fails.
- **Exercise 2:** First note that the edit makes the fake catalog return 126 cents for "item-a". Then compute two items at that price, 252. Finally, explain why the clock and audit parts still match and only the total comparison fails.
- **Exercise 3:** First call `service.quote("missing", 2)` and catch `NoSuchElementException`. Then inspect the audit list from Example B. Finally, assert that it still holds exactly one event, because the failed lookup never reached the audit call.
- **Exercise 4:** First build a `Service` whose catalog lambda throws `IOException("catalog unavailable")`. Then call `quote` and catch that exception, checking its message. Finally, assert that the separate audit list stayed empty and the failure was not converted into a price.
- **Exercise 5:** First wrap the catalog in a lambda that increments an `AtomicInteger` on every lookup. Then request a quantity of -1 and catch `IllegalArgumentException`. Finally, assert that the counter is still 0 and explain the order of checks in `quote`.
- **Exercise 6:** First inject a catalog that returns `Long.MAX_VALUE` for every item. Then request two items and catch `ArithmeticException` from `Math.multiplyExact`. Finally, assert that the overflow audit list is empty because the event comes after the calculation.

## Self-check and retrieval

From memory, explain what a port and an adapter are in this lesson, why `quote` validates input before calling the catalog, how a missing item differs from an unavailable catalog, and why the audit event is written only after the total and timestamp exist.

## Next step

Continue with `java-035`: Build a tested local data service. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-034: Application design and dependency boundaries.
Read courses/java/guides/java-034.md and courses/java/lessons/java-034.java. Direct prerequisites: `java-033`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
