# java-034: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Application design separates domain decisions from the mechanisms that supply data, time or side effects. A pure pricing calculation can be tested without a database, network or system clock. A service composes that calculation with repository and clock ports. Adapters implement those ports for a particular environment. Dependency inversion means the domain-facing code depends on the behavior it needs rather than on a concrete infrastructure class.

This lesson builds a small quote service. A catalog port supplies integer-cent prices, a fixed clock supplies the timestamp, and an audit sink records successful operations in memory. The service validates quantity and catalog lookup before producing a result or recording an event. A failing repository propagates its failure rather than returning a fabricated zero price. Thefake-backed tests establish service logic and call boundaries, not live database or network acceptance.

**Port:** A behavior interface required by application logic.

**Adapter:** An implementation connecting a port to a concrete mechanism.

**Pure core:** Domain calculations independent of infrastructure side effects.

**Dependency inversion:** Depending on required behavior rather than concrete external machinery.

## Reading the reference

Define a Catalog interface returning OptionalLong and declaring IOException for an operational read failure. Inject a Supplier<Instant> and Consumer<String> through the constructor. Keep the pure total calculation separate and use Math.multiplyExact for overflow. The Quote record carries item, quantity, total and time. Audit only after all required validation and calculation succeed.

## Exercise 1: Test the pure calculation: change one input

Task: Copy Example A into a scratch `Main.java` and change `total(0, 125);` to `total(1, 125);`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.

The core arithmetic needs no repository or clock. Isolating it makes domain boundaries and overflow behavior easy to check.

The unchanged code is the part that Example A adds:

```java
assert total(3, 125) == 375;
boolean invalid = false;
try {
  total(0, 125);
} catch (IllegalArgumentException expected) {
  invalid = true;
}
assert invalid;
```

**Expected:** The changed run fails with an `AssertionError` from the assertion on `invalid`. Restoring the original line brings back the worked observation: 375 cents; nonpositive quantity rejected.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `invalid` false. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Compose a deterministic service: debug a regression

Task: A regression changed one token in the code that Example B adds after Example A, so one line now reads `id.equals("item-a") ? java.util.OptionalLong.of(126) : java.util.OptionalLong.empty();`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.

A fixed clock removes timing nondeterminism. The audit event is a local test double, not a message sent to another person or service.

The unchanged code is the part that Example B adds:

```java
List<String> audit = new ArrayList<>();
var instant = java.time.Instant.parse("2026-01-01T00:00:00Z");
Catalog catalog = id ->
  id.equals("item-a") ? java.util.OptionalLong.of(125) : java.util.OptionalLong.empty();
Service service = new Service(catalog, () -> instant, audit::add);
Quote quote = service.quote("item-a", 2);
assert quote.totalCents() == 250 &&
quote.created().equals(instant) &&
audit.equals(List.of("quoted:item-a"));
```

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `quote.totalCents() == 250 && quote.created().equals(instant) && audit.equals(List.of("quoted:item-a"))`; after it the line reads `id.equals("item-a") ? java.util.OptionalLong.of(125) : java.util.OptionalLong.empty();` again and total 250, time 2026-01-01T00:00:00Z, one audit event.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `quote.totalCents() == 250 && quote.created().equals(instant) && audit.equals(List.of("quoted:item-a"))` for this input.

## Exercise 3: Reject an unknown catalog item

Task: Request missing and inspect the audit list.

A missing item is a domain outcome. It should not silently become a zero-priced quote or produce a misleading success event.

```java
boolean missing = false;
try {
  service.quote("missing", 2);
} catch (NoSuchElementException expected) {
  missing = true;
}
assert missing && audit.size() == 1;
```

**Expected:** NoSuchElementException; no additional audit.

**Verify:** Keep an assertion equivalent to `missing && audit.size() == 1`. As a control, change `missing = true;` to `missing = false;`: the run must fail with an `AssertionError` from the assertion on `missing && audit.size() == 1`. Restore the line before continuing.

## Exercise 4: Propagate an infrastructure failure

Task: Inject a Catalog thatthrowsIOException.

An operational failure differs from a valid missing lookup. The service preserves that distinction so a caller can choose retry or error behavior appropriately.

```java
List<String> failures = new ArrayList<>();
Service unavailable = new Service(
  id -> {
    throw new java.io.IOException("catalog unavailable");
  },
  () -> instant,
  failures::add
);
boolean propagated = false;
try {
  unavailable.quote("item-a", 1);
} catch (java.io.IOException expected) {
  propagated = expected.getMessage().equals("catalog unavailable");
}
assert propagated && failures.isEmpty();
```

**Expected:** same failure type; no success audit.

**Verify:** Keep an assertion equivalent to `propagated && failures.isEmpty()`. As a control, change `throw new java.io.IOException("catalog unavailable");` to `throw new java.io.IOException("catalog unavailable!");`: the run must fail with an `AssertionError` from the assertion on `propagated && failures.isEmpty()`. Restore the line before continuing.

## Exercise 5: Prove invalid quantity fails before a repository call

Task: Use a counting catalog and request negative quantity.

Validation ordering is part of the boundary contract. It avoids unnecessary external work and prevents a malformed request from being mistaken for an infrastructure failure.

```java
var calls = new java.util.concurrent.atomic.AtomicInteger();
Service checked = new Service(
  id -> {
    calls.incrementAndGet();
    return java.util.OptionalLong.of(1);
  },
  () -> instant,
  value -> {}
);
boolean rejected = false;
try {
  checked.quote("item-a", -1);
} catch (IllegalArgumentException expected) {
  rejected = true;
}
assert rejected && calls.get() == 0;
```

**Expected:** repository call count 0.

**Verify:** Keep an assertion equivalent to `rejected && calls.get() == 0`. As a control, change `rejected = true;` to `rejected = false;`: the run must fail with an `AssertionError` from the assertion on `rejected && calls.get() == 0`. Restore the line before continuing.

## Exercise 6: Detect arithmetic overflow without an event

Task: Use a Long.MAX_VALUE unit price and quantity 2.

A validly typed integer can still exceed the domain representation. Calculating before emitting a success event keeps side effects aligned with the actual outcome.

```java
List<String> overflowAudit = new ArrayList<>();
Service expensive = new Service(
  id -> java.util.OptionalLong.of(Long.MAX_VALUE),
  () -> instant,
  overflowAudit::add
);
boolean overflow = false;
try {
  expensive.quote("x", 2);
} catch (ArithmeticException expected) {
  overflow = true;
}
assert overflow && overflowAudit.isEmpty();
```

**Expected:** ArithmeticException; audit sink unused.

**Verify:** Keep an assertion equivalent to `overflow && overflowAudit.isEmpty()`. As a control, change `overflow = true;` to `overflow = false;`: the run must fail with an `AssertionError` from the assertion on `overflow && overflowAudit.isEmpty()`. Restore the line before continuing.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
