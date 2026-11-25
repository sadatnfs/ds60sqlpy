# java-009: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

Exceptions separate normal return values from failure. A checked exception is declared or handled by callers; an unchecked exception often signals an invalid argument or programming error. Resource lifetime is a different concern: a resource must close whether the body succeeds or fails. try-with-resources closes resources in reverse declaration order. If the body throws and closing also throws, the body exception remains primary and close failures are attached as suppressed exceptions. Catching everything and returning a default would erase that information. This lesson uses tiny in-memory AutoCloseable probes to make lifetime order and suppression observable without opening external files.

**Checked exception:** A failure type that callers must declare or handle.

**Resource lifetime:** The interval during which an owned resource is usable.

**Suppressed exception:** A secondary close failure retained beside a primary exception.

## Reading the reference

A try(resource declarations) block owns the declared resources until control exits. AutoCloseable.close may throw Exception. getSuppressed exposes secondary close failures. Use a specific catch when a failure is expected, and preserve the original cause when translating to a domain exception. A finally block is useful for cleanup patterns not covered by resources, but throwing from finally can replace an important earlier failure.

## Exercise 1: Close on normal completion: change one input

Task: Change `try (Probe resource = new Probe("A", events, false)) {` to `try (Probe resource = new Probe("A!", events, false)) {` in Example A and predict which assertion fails and why.

Leaving the block triggers close even without an explicit call in the body. Ownership is visible in the block structure.

The unchanged code is the part that Example A adds:

```java
List<String> events = new ArrayList<>();
try (Probe resource = new Probe("A", events, false)) {
  events.add("body");
}
assert events.equals(List.of("body", "closeA"));
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `events.equals(List.of("body", "closeA"))`.

**Verify:** Name the value that makes `events.equals(List.of("body", "closeA"))` false, then restore the line.

## Exercise 2: Close in reverse order: debug a regression

Task: A regression in Example B's new code makes one line read `try (Probe a = new Probe("A!", events, false); Probe b = new Probe("B", events, false)) {`. Repair it using the failing assertion.

Later resources often depend on earlier ones, so reverse closure is deliberate. The event trace proves the actual order for this fixture.

The unchanged code is the part that Example B adds:

```java
events.clear();
try (Probe a = new Probe("A", events, false); Probe b = new Probe("B", events, false)) {
  events.add("body");
}
assert events.equals(List.of("body", "closeB", "closeA"));
```

**Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `events.equals(List.of("body", "closeB", "closeA"))`; the repaired line reads `try (Probe a = new Probe("A", events, false); Probe b = new Probe("B", events, false)) {`.

**Verify:** Explain how the changed token alters the value that `events.equals(List.of("body", "closeB", "closeA"))` tests.

## Exercise 3: Close after body failure

Task: Throw IllegalStateException in the body and inspect events after catching it.

Exceptional control flow does not skip resource closure. A manually placed close after the body statement would never execute in this case.

```java
events.clear();
boolean bodyFailed = false;
try (Probe a = new Probe("A", events, false)) {
  throw new IllegalStateException("body");
} catch (IllegalStateException expected) {
  bodyFailed = true;
}
assert bodyFailed && events.equals(List.of("closeA"));
```

**Expected:** `closeA` is still recorded.

**Verify:** Control: changing `bodyFailed = true;` to `bodyFailed = false;` must fail the assertion on `bodyFailed && events.equals(List.of("closeA"))`.

## Exercise 4: Preserve suppressed close failure

Task: Make the body throw and the resource close throw too.

The primary failure is not lost. Suppressed exceptions retain cleanup diagnostics without pretending they were the original cause.

```java
events.clear();
try (Probe a = new Probe("A", events, true)) {
  throw new IllegalStateException("body");
} catch (IllegalStateException expected) {
  assert expected.getMessage().equals("body");
  assert expected.getSuppressed().length == 1;
  assert expected.getSuppressed()[0].getMessage().equals("closeA");
}
```

**Expected:** primary message `body`; one suppressed exception `closeA`.

**Verify:** Control: changing `try (Probe a = new Probe("A", events, true)) {` to `try (Probe a = new Probe("A!", events, true)) {` must fail the assertion on `expected.getSuppressed()[0].getMessage().equals("closeA")`.

## Exercise 5: Observe close-only failure

Task: Let the body succeed but close throw IOException.

When there is no body exception, a close failure becomes the primary failure. Resource cleanup is part of the operation outcome.

```java
boolean closeFailed = false;
try (Probe a = new Probe("A", events, true)) {} catch (java.io.IOException expected) {
  closeFailed = expected.getMessage().equals("closeA");
}
assert closeFailed;
```

**Expected:** IOException `closeA` is primary.

**Verify:** Control: changing `try (Probe a = new Probe("A", events, true)) {} catch (java.io.IOException expected) {` to `try (Probe a = new Probe("A", events, false)) {} catch (java.io.IOException expected) {` must fail the assertion on `closeFailed`.

## Exercise 6: Retain a translated cause

Task: Wrap an IOException in IllegalStateException with a domain message and inspect cause.

A useful translation adds context while preserving diagnostic ancestry. Creating a new exception with only the old message would discard type and stack information.

```java
var original = new java.io.IOException("read failed");
var translated = new IllegalStateException("Cannot load lesson fixture", original);
assert translated.getCause() == original && translated.getMessage().contains("fixture");
```

**Expected:** cause remains the original IOException.

**Verify:** Control: changing `assert translated.getCause() == original && translated.getMessage().contains("fixture");` to `assert translated.getCause() == original && translated.getMessage().contains("fixture!");` inside the assertion must make it fail.

## After comparing the answer

Add a third resource to your copy whose `close` also throws, predict the order of the suppressed exceptions on the primary failure, and test that prediction with `getSuppressed()`.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
