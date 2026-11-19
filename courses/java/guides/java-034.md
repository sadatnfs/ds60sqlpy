# java-034: Application design and dependency boundaries

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-033`

## Learning objectives

Separate pure domain logic from infrastructure so validation and failures are testable before any repository call. Along the way, explain port, adapter, pure core, dependency inversion using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Request missing and inspect the audit list. The final exercise transfers the mechanism to detect arithmetic overflow without an event.

## Purpose and mental model

Application design separates domain decisions from the mechanisms that supply data, time or side effects. A pure pricing calculation can be tested without a database, network or system clock. A service composes that calculation with repository and clock ports. Adapters implement those ports for a particular environment. Dependency inversion means the domain-facing code depends on the behavior it needs rather than on a concrete infrastructure class.

This lesson builds a small quote service. A catalog port supplies integer-cent prices, a fixed clock supplies the timestamp, and an audit sink records successful operations in memory. The service validates quantity and catalog lookup before producing a result or recording an event. A failing repository propagates its failure rather than returning a fabricated zero price. Thefake-backed tests establish service logic and call boundaries, not live database or network acceptance.

## Vocabulary and concepts

**Port:** A behavior interface required by application logic.

**Adapter:** An implementation connecting a port to a concrete mechanism.

**Pure core:** Domain calculations independent of infrastructure side effects.

**Dependency inversion:** Depending on required behavior rather than concrete external machinery.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-034/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



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

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Test the pure calculation: change one input.** Copy Example A into a scratch `Main.java` and change `total(0, 125);` to `total(1, 125);`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `invalid`. Restoring the original line brings back the worked observation: 375 cents; nonpositive quantity rejected.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `invalid` false. After restoring the line, the program completes without an `AssertionError` again.

2. **Compose a deterministic service: debug a regression.** A regression changed one token in the code that Example B adds after Example A, so one line now reads `id.equals("item-a") ? java.util.OptionalLong.of(126) : java.util.OptionalLong.empty();`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `quote.totalCents() == 250 && quote.created().equals(instant) && audit.equals(List.of("quoted:item-a"))`; after it the line reads `id.equals("item-a") ? java.util.OptionalLong.of(125) : java.util.OptionalLong.empty();` again and total 250, time 2026-01-01T00:00:00Z, one audit event.
   **Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `quote.totalCents() == 250 && quote.created().equals(instant) && audit.equals(List.of("quoted:item-a"))` for this input.

3. **Reject an unknown catalog item.** Request missing and inspect the audit list.
   **Expected:** NoSuchElementException; no additional audit.
   **Verify:** Keep an assertion equivalent to `missing && audit.size() == 1`. As a control, change `missing = true;` to `missing = false;`: the run must fail with an `AssertionError` from the assertion on `missing && audit.size() == 1`. Restore the line before continuing.

4. **Propagate an infrastructure failure.** Inject a Catalog thatthrowsIOException.
   **Expected:** same failure type; no success audit.
   **Verify:** Keep an assertion equivalent to `propagated && failures.isEmpty()`. As a control, change `throw new java.io.IOException("catalog unavailable");` to `throw new java.io.IOException("catalog unavailable!");`: the run must fail with an `AssertionError` from the assertion on `propagated && failures.isEmpty()`. Restore the line before continuing.

5. **Prove invalid quantity fails before a repository call.** Use a counting catalog and request negative quantity.
   **Expected:** repository call count 0.
   **Verify:** Keep an assertion equivalent to `rejected && calls.get() == 0`. As a control, change `rejected = true;` to `rejected = false;`: the run must fail with an `AssertionError` from the assertion on `rejected && calls.get() == 0`. Restore the line before continuing.

6. **Detect arithmetic overflow without an event.** Use a Long.MAX_VALUE unit price and quantity 2.
   **Expected:** ArithmeticException; audit sink unused.
   **Verify:** Keep an assertion equivalent to `overflow && overflowAudit.isEmpty()`. As a control, change `overflow = true;` to `overflow = false;`: the run must fail with an `AssertionError` from the assertion on `overflow && overflowAudit.isEmpty()`. Restore the line before continuing.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: 375 cents; nonpositive quantity rejected. Then list the values read by `invalid` and trace each one from its declaration. Finally, compute the asserted value with `total(1, 125);` in place before running.
- **Exercise 2:** First restate the expected observation: total 250, time 2026-01-01T00:00:00Z, one audit event. Then list the values read by `quote.totalCents() == 250 && quote.created().equals(instant) && audit.equals(List.of("quoted:item-a"))` and trace each one from its declaration. Finally, compare `id.equals("item-a") ? java.util.OptionalLong.of(126) : java.util.OptionalLong.empty();` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: noSuchElementException; no additional audit. Then list the values read by `missing && audit.size() == 1` and trace each one from its declaration. Finally, predict the effect of changing `missing = true;` to `missing = false;` before running anything.
- **Exercise 4:** First restate the expected observation: same failure type; no success audit. Then list the values read by `propagated && failures.isEmpty()` and trace each one from its declaration. Finally, predict the effect of changing `throw new java.io.IOException("catalog unavailable");` to `throw new java.io.IOException("catalog unavailable!");` before running anything.
- **Exercise 5:** First restate the expected observation: repository call count 0. Then list the values read by `rejected && calls.get() == 0` and trace each one from its declaration. Finally, predict the effect of changing `rejected = true;` to `rejected = false;` before running anything.
- **Exercise 6:** First restate the expected observation: arithmeticException; audit sink unused. Then list the values read by `overflow && overflowAudit.isEmpty()` and trace each one from its declaration. Finally, predict the effect of changing `overflow = true;` to `overflow = false;` before running anything.

## Self-check and retrieval

Close the solution and explain Port, Adapter, Pure core in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

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
