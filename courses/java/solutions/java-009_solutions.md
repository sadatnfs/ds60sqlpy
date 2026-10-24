# java-009: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Exceptions separate normal return values from failure. A checked exception is declared or handled by callers; an unchecked exception often signals an invalid argument or programming error. Resource lifetime is a different concern: a resource must close whether the body succeeds or fails. try-with-resources closes resources in reverse declaration order. If the body throws and closing also throws, the body exception remains primary and close failures are attached as suppressed exceptions. Catching everything and returning a default would erase that information. This lesson uses tiny in-memory AutoCloseable probes to make lifetime order and suppression observable without opening external files.

**Checked exception:** A failure type that callers must declare or handle.

**Resource lifetime:** The interval during which an owned resource is usable.

**Suppressed exception:** A secondary close failure retained beside a primary exception.

## Reading the reference

A try(resource declarations) block owns the declared resources until control exits. AutoCloseable.close may throwException. getSuppressed exposes secondary close failures. Use a specific catch when a failure is expected, and preserve the original cause when translating to a domain exception. A finally block is useful for cleanup patterns not covered by resources, but throwing from finally can replace an important earlier failure.

## Exercise 1: Close on normal completion

Task: Open a Probe resource, record body, then inspect closure order.

Leaving the block triggers close even without an explicit call in the body. Ownership is visible in the block structure.

```java
List<String> events = new ArrayList<>();
try (Probe resource = new Probe("A", events, false)) { events.add("body"); }
assert events.equals(List.of("body", "closeA"));
```

**Expected:** events body, close A.

**Verify:** Compare the program values or named exception with events body, close A. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Close in reverse order

Task: Declare resourcesA thenB and leave the block.

Later resources often depend on earlier ones, so reverse closure is deliberate. The event trace proves the actual order for this fixture.

```java
events.clear();
try (Probe a = new Probe("A", events, false); Probe b = new Probe("B", events, false)) { events.add("body"); }
assert events.equals(List.of("body", "closeB", "closeA"));
```

**Expected:** closeB beforecloseA.

**Verify:** Compare the program values or named exception with closeB beforecloseA. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Close after body failure

Task: Throw IllegalStateException in the body and inspect events after catching it.

Exceptional control flow does not skip resource closure. A manually placed close after the body statement would never execute in this case.

```java
events.clear(); boolean bodyFailed = false;
try (Probe a = new Probe("A", events, false)) { throw new IllegalStateException("body"); }
catch (IllegalStateException expected) { bodyFailed = true; }
assert bodyFailed && events.equals(List.of("closeA"));
```

**Expected:** close A still recorded.

**Verify:** Compare the program values or named exception with close A still recorded. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Preserve suppressed close failure

Task: Make the body throw and the resource close throw too.

The primary failure is not lost. Suppressed exceptions retain cleanup diagnostics without pretending they were the original cause.

```java
events.clear();
try (Probe a = new Probe("A", events, true)) { throw new IllegalStateException("body"); }
catch (IllegalStateException expected) {
    assert expected.getMessage().equals("body");
    assert expected.getSuppressed().length == 1;
    assert expected.getSuppressed()[0].getMessage().equals("closeA");
}
```

**Expected:** primary message body;one suppressed exceptioncloseA.

**Verify:** Compare the program values or named exception with primary message body;one suppressed exceptioncloseA. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Observe close-only failure

Task: Let the body succeed but close throwIOException.

When there is no body exception, a close failure becomes the primary failure. Resource cleanup is part of the operation outcome.

```java
boolean closeFailed = false;
try (Probe a = new Probe("A", events, true)) { }
catch (java.io.IOException expected) { closeFailed = expected.getMessage().equals("closeA"); }
assert closeFailed;
```

**Expected:** IOExceptioncloseA is primary.

**Verify:** Compare the program values or named exception with IOExceptioncloseA is primary. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Retain a translated cause

Task: Wrap an IOException in IllegalStateException with a domain message and inspect cause.

A useful translation adds context while preserving diagnostic ancestry. Creating a new exception with only the old message would discard type and stack information.

```java
var original = new java.io.IOException("read failed");
var translated = new IllegalStateException("Cannot load lesson fixture", original);
assert translated.getCause() == original && translated.getMessage().contains("fixture");
```

**Expected:** cause remains the original IOException.

**Verify:** Compare the program values or named exception with cause remains the original IOException. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
