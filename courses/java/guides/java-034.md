# java-034: Application design and dependency boundaries

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-033`

## Learning objectives

Explain port, adapter, pure core, dependency inversion using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Compute 3 items at 125 cents and check the zero/negative quantity policy. The final exercise transfers the mechanism to detect arithmetic overflow without an event.

## Purpose and mental model

Application design separates domain decisions from the mechanisms that supply data,time or side effects. A pure pricing calculation can be tested without a database,network or system clock. A service composes that calculation with repository and clock ports. Adapters implement those ports for a particular environment. Dependency inversion means the domain-facing code depends on the behavior it needs rather than on a concrete infrastructure class.

This lesson builds a small quote service. A catalog port supplies integer-cent prices,a fixed clock supplies the timestamp,and an audit sink records successful operations in memory. The service validates quantity andcatalog lookup before producing a result or recording an event. A failing repository propagates its failure rather than returning a fabricated zero price. Thefake-backed tests establish service logic and call boundaries,not live database or network acceptance.

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

Define a Catalog interface returning OptionalLong and declaring IOException for an operational read failure. Inject a Supplier<Instant> and Consumer<String> through the constructor. Keep the pure total calculation separate anduseMath.multiplyExact for overflow. TheQuote record carries item,quantity,total and time. Audit only after all required validation and calculation succeed.

## Worked example / walkthrough

### Example A: Test the pure calculation

The core arithmetic needsno repository or clock. Isolating it makes domain boundaries and overflow behavior easy to check.

```java
import java.util.*;

public class Main {
    interface Catalog {java.util.OptionalLong unitPrice(String id) throws java.io.IOException;}
    record Quote(String item,int quantity,long totalCents,java.time.Instant created){}
    static long total(int quantity,long unitPrice){if(quantity<=0||unitPrice<0)throw new IllegalArgumentException("positive quantity and nonnegative price required");return Math.multiplyExact((long)quantity,unitPrice);}
    record Service(Catalog catalog,java.util.function.Supplier<java.time.Instant> clock,java.util.function.Consumer<String> audit){
        Service{Objects.requireNonNull(catalog);Objects.requireNonNull(clock);Objects.requireNonNull(audit);}
        Quote quote(String id,int quantity) throws java.io.IOException {if(id==null||id.isBlank()||quantity<=0)throw new IllegalArgumentException("valid item and quantity required");long price=catalog.unitPrice(id).orElseThrow(() -> new NoSuchElementException("unknown item"));long amount=total(quantity,price);Quote result=new Quote(id,quantity,amount,clock.get());audit.accept("quoted:"+id);return result;}
    }
    public static void main(String[] args) throws Exception {
        assert total(3,125)==375;boolean invalid=false;try{total(0,125);}catch(IllegalArgumentException expected){invalid=true;}assert invalid;
    }
}

```

**Expected:** 375 cents; nonpositive quantity rejected.

### Example B: Compose a deterministic service

A fixed clock removes timing nondeterminism. The audit event is a local test double,not a message sent to another person or service.

```java
import java.util.*;

public class Main {
    interface Catalog {java.util.OptionalLong unitPrice(String id) throws java.io.IOException;}
    record Quote(String item,int quantity,long totalCents,java.time.Instant created){}
    static long total(int quantity,long unitPrice){if(quantity<=0||unitPrice<0)throw new IllegalArgumentException("positive quantity and nonnegative price required");return Math.multiplyExact((long)quantity,unitPrice);}
    record Service(Catalog catalog,java.util.function.Supplier<java.time.Instant> clock,java.util.function.Consumer<String> audit){
        Service{Objects.requireNonNull(catalog);Objects.requireNonNull(clock);Objects.requireNonNull(audit);}
        Quote quote(String id,int quantity) throws java.io.IOException {if(id==null||id.isBlank()||quantity<=0)throw new IllegalArgumentException("valid item and quantity required");long price=catalog.unitPrice(id).orElseThrow(() -> new NoSuchElementException("unknown item"));long amount=total(quantity,price);Quote result=new Quote(id,quantity,amount,clock.get());audit.accept("quoted:"+id);return result;}
    }
    public static void main(String[] args) throws Exception {
        assert total(3,125)==375;boolean invalid=false;try{total(0,125);}catch(IllegalArgumentException expected){invalid=true;}assert invalid;

        List<String> audit=new ArrayList<>();var instant=java.time.Instant.parse("2026-01-01T00:00:00Z");
        Catalog catalog=id -> id.equals("item-a")?java.util.OptionalLong.of(125):java.util.OptionalLong.empty();
        Service service=new Service(catalog,() -> instant,audit::add);Quote quote=service.quote("item-a",2);
        assert quote.totalCents()==250 && quote.created().equals(instant) && audit.equals(List.of("quoted:item-a"));
    }
}

```

**Expected:** total250,time2026-01-01T00:00:00Z,oneauditevent.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Test the pure calculation.** Compute 3 items at 125 cents and check the zero/negative quantity policy.
   **Expected:** 375 cents; nonpositive quantity rejected.
   **Verify:** Compare your assertion values or captured diagnostic with 375 cents; nonpositive quantity rejected.

2. **Compose a deterministic service.** Inject a fixedcatalog,clock and audit list,and request twoitems.
   **Expected:** total250,time2026-01-01T00:00:00Z,oneauditevent.
   **Verify:** Compare your assertion values or captured diagnostic with total250,time2026-01-01T00:00:00Z,oneauditevent.

3. **Reject an unknown catalog item.** Requestmissing andinspecttheauditlist.
   **Expected:** NoSuchElementException;no additional audit.
   **Verify:** Compare your assertion values or captured diagnostic with NoSuchElementException;no additional audit.

4. **Propagate an infrastructure failure.** Inject a Catalog thatthrowsIOException.
   **Expected:** same failure type;no success audit.
   **Verify:** Compare your assertion values or captured diagnostic with same failure type;no success audit.

5. **Prove invalid quantity fails before a repository call.** Use a countingcatalog and request negative quantity.
   **Expected:** repositorycallcount0.
   **Verify:** Compare your assertion values or captured diagnostic with repositorycallcount0.

6. **Detect arithmetic overflow without an event.** UseLong.MAX_VALUEunitprice andquantity2.
   **Expected:** ArithmeticException;audit sink unused.
   **Verify:** Compare your assertion values or captured diagnostic with ArithmeticException;audit sink unused.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Port, Adapter, Pure core in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-034: Application design and dependency boundaries.
Read courses/java/guides/java-034.md and courses/java/lessons/java-034.java. Direct prerequisites: `java-033`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
