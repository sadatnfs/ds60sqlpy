# java-032: Profiling and benchmark reasoning

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-031`

## Learning objectives

Explain warmup, measurement bias, jfr event, observable result using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Sum 1..1000 with a loop and compare with n*(n+1)/2. The final exercise transfers the mechanism to keep instrumented anduninstrumented claims separate.

## Purpose and mental model

Performance measurement starts with a correct,representative workload. JVM execution can change during warmup as classes load and JIT compilation occurs. A first-call timing and a warmed repeated timing answer different questions. Dead-code elimination can remove unused work,while logging orprofiling can add work that dominates a small calculation. A benchmark must retain observable results and record its measurement conditions.

Java Flight Recorder,JFR,records runtime events with relatively low overhead in suitable configurations,but any instrumentation can affect the workload. This lesson creates one owned recording containing a custom calculation event,then reads that event back. It does not start a persistent system recording or claim a production performance diagnosis. Simple elapsed-time samples are reported without hardcoded speed thresholds or universal conclusions.

## Vocabulary and concepts

**Warmup:** Initial execution used to separate setup/JIT effects from repeated work.

**Measurement bias:** A distortion introduced by workload choice,ordering or instrumentation.

**JFR event:** A structured runtime observation recorded under an explicit configuration.

**Observable result:** A value retained so measured work cannot be discarded as unused.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-032/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

System.nanoTime measures elapsed intervals,not wall-clock dates. Keep a checksum or volatile sink so the calculation result remains observable. Separate warmup iterations from measured iterations. A customjdk.jfr.Event records declared fields;enable its event name,start the Recording,commit the event,stop and dump to an owned file. RecordingFile reads structured events for verification.

## Worked example / walkthrough

### Example A: Establish a numerical oracle

Correctness is checked independently before timing. A faster wrong computation is not a useful optimization.

```java
import java.util.*;

public class Main {
    static volatile long sink;
    static long sum(int n){if(n<0||n>100000)throw new IllegalArgumentException("bounded nonnegative n required");long result=0;for(int i=1;i<=n;i++)result+=i;return result;}
    @jdk.jfr.Name("course.Calculation") @jdk.jfr.Label("Course calculation")
    static class Calculation extends jdk.jfr.Event {long input;long output;}
    public static void main(String[] args) throws Exception {
        assert sum(1000)==500_500L && sum(1000)==1000L*1001/2;
    }
}

```

**Expected:** 500500.

### Example B: Warm up without hiding results

The sink makes the result observable. This is a teaching safeguard,not a replacement for a dedicated benchmark harness such asJMH.

```java
import java.util.*;

public class Main {
    static volatile long sink;
    static long sum(int n){if(n<0||n>100000)throw new IllegalArgumentException("bounded nonnegative n required");long result=0;for(int i=1;i<=n;i++)result+=i;return result;}
    @jdk.jfr.Name("course.Calculation") @jdk.jfr.Label("Course calculation")
    static class Calculation extends jdk.jfr.Event {long input;long output;}
    public static void main(String[] args) throws Exception {
        assert sum(1000)==500_500L && sum(1000)==1000L*1001/2;

        for(int i=0;i<100;i++)sink=sum(1000);assert sink==500_500L;
    }
}

```

**Expected:** sink500500 after warmup.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Establish a numerical oracle.** Sum 1..1000 with a loop and compare with n*(n+1)/2.
   **Expected:** 500500.
   **Verify:** Compare your assertion values or captured diagnostic with 500500.

2. **Warm up without hiding results.** Run the calculation100times and store each result in a volatile sink.
   **Expected:** sink500500 after warmup.
   **Verify:** Compare your assertion values or captured diagnostic with sink500500 after warmup.

3. **Measure repeated work with a checksum.** Time20calculations and sum their outputs.
   **Expected:** checksum10010000;elapsednanosecondsnonnegative.
   **Verify:** Compare your assertion values or captured diagnostic with checksum10010000;elapsednanosecondsnonnegative.

4. **Record and read an actualJFR event.** Create a bounded recording withoneCalculation event containinginput100 andoutput5050.
   **Expected:** one matching event with the declared fields.
   **Verify:** Compare your assertion values or captured diagnostic with one matching event with the declared fields.

5. **Collect a small timing distribution.** Measure the same bounded work five times and inspect sorted samples.
   **Expected:** five nonnegative samples;minimum<=maximum;checksums preserved.
   **Verify:** Compare your assertion values or captured diagnostic with five nonnegative samples;minimum<=maximum;checksums preserved.

6. **Keep instrumented anduninstrumented claims separate.** Record warmup,workload andprofiling state beside a measurement;refuse a universal speedup claim.
   **Expected:** metadata names 100 warmups and profiling false; universal claim false.
   **Verify:** Compare your assertion values or captured diagnostic with metadata names 100 warmups and profiling false; universal claim false.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Warmup, Measurement bias, JFR event in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.jfr/jdk/jfr/Recording.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Consult `docs/implementation/java-content-status.md` for the actual compile/run receipts. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-032: Profiling and benchmark reasoning.
Read courses/java/guides/java-032.md and courses/java/lessons/java-032.java. Direct prerequisites: `java-031`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
