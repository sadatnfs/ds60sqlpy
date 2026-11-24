# java-032: Profiling and benchmark reasoning

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-031`

## Learning objectives

Measure performance with warm-up, checksums and JFR events and report the result without overclaiming. Along the way, explain warmup, measurement bias, jfr event, observable result using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Time 20 calculations and sum their outputs. The final exercise transfers the mechanism to keep instrumented and uninstrumented claims separate.

## Purpose and mental model

Performance measurement starts with a correct, representative workload. JVM execution can change during warmup as classes load and JIT compilation occurs. A first-call timing and a warmed repeated timing answer different questions. Dead-code elimination can remove unused work, while logging or profiling can add work that dominates a small calculation. A benchmark must retain observable results and record its measurement conditions.

Java Flight Recorder, JFR, records runtime events with relatively low overhead in suitable configurations, but any instrumentation can affect the workload. This lesson creates one owned recording containing a custom calculation event, then reads that event back. It does not start a persistent system recording or claim a production performance diagnosis. Simple elapsed-time samples are reported without hardcoded speed thresholds or universal conclusions.

## Vocabulary and concepts

**Warmup:** Initial execution used to separate setup/JIT effects from repeated work.

**Measurement bias:** A distortion introduced by workload choice, ordering or instrumentation.

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

System.nanoTime measures elapsed intervals, not wall-clock dates. Keep a checksum or volatile sink so the calculation result remains observable. Separate warmup iterations from measured iterations. A custom jdk.jfr.Event records declared fields; enable its event name, start the Recording, commit the event, stop and dump to an owned file. RecordingFile reads structured events for verification.

## Worked example / walkthrough

### Example A: Establish a numerical oracle

Correctness is checked independently before timing. A faster wrong computation is not a useful optimization.

```java
import java.util.*;

public class Main {

  static volatile long sink;

  static long sum(int n) {
    if (n < 0 || n > 100000) throw new IllegalArgumentException("bounded nonnegative n required");
    long result = 0;
    for (int i = 1; i <= n; i++) result += i;
    return result;
  }

  @jdk.jfr.Name("course.Calculation")
  @jdk.jfr.Label("Course calculation")
  static class Calculation extends jdk.jfr.Event {

    long input;
    long output;
  }

  public static void main(String[] args) throws Exception {
    assert sum(1000) == 500_500L && sum(1000) == (1000L * 1001) / 2;
  }
}
```

**Expected:** 500500.

### Example B: Warm up without hiding results

The sink makes the result observable. This is a teaching safeguard, not a replacement for a dedicated benchmark harness such as JMH.

```java
import java.util.*;

public class Main {

  static volatile long sink;

  static long sum(int n) {
    if (n < 0 || n > 100000) throw new IllegalArgumentException("bounded nonnegative n required");
    long result = 0;
    for (int i = 1; i <= n; i++) result += i;
    return result;
  }

  @jdk.jfr.Name("course.Calculation")
  @jdk.jfr.Label("Course calculation")
  static class Calculation extends jdk.jfr.Event {

    long input;
    long output;
  }

  public static void main(String[] args) throws Exception {
    assert sum(1000) == 500_500L && sum(1000) == (1000L * 1001) / 2;

    for (int i = 0; i < 100; i++) sink = sum(1000);
    assert sink == 500_500L;
  }
}
```

**Expected:** sink 500500 after warmup.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Establish a numerical oracle: predict an edited check.** Copy Example A into a scratch `Main.java` and change `assert sum(1000) == 500_500L && sum(1000) == (1000L * 1001) / 2;` to `assert sum(1001) == 500_500L && sum(1000) == (1000L * 1001) / 2;` inside its assertion. Before running it with `java -ea Main`, predict whether the assertion still holds and explain why; then restore it.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `sum(1000) == 500_500L && sum(1000) == (1000L * 1001) / 2`. Restoring the original line brings back the worked observation: 500500.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and explain why the edited condition is false for the values that satisfy `sum(1000) == 500_500L && sum(1000) == (1000L * 1001) / 2`. After restoring the line, the program completes without an `AssertionError` again.

2. **Warm up without hiding results: debug a regression.** A regression changed one token in the code that Example B adds after Example A, so one line now reads `for (int i = 0; i < 100; i++) sink = sum(1001);`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `sink == 500_500L`; after it the line reads `for (int i = 0; i < 100; i++) sink = sum(1000);` again and sink 500500 after warmup.
   **Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `sink == 500_500L` for this input.

3. **Measure repeated work with a checksum.** Time 20 calculations and sum their outputs.
   **Expected:** checksum 10010000; elapsed nanoseconds nonnegative.
   **Verify:** Keep an assertion equivalent to `checksum == 10_010_000L && elapsed >= 0`. As a control, change `for (int i = 0; i < 20; i++) checksum += sum(1000);` to `for (int i = 0; i <= 20; i++) checksum += sum(1000);`: the run must fail with an `AssertionError` from the assertion on `checksum == 10_010_000L && elapsed >= 0`. Restore the line before continuing.

4. **Record and read an actual JFR event.** Create a bounded recording with one Calculation event containing input 100 and output 5050.
   **Expected:** one matching event with the declared fields.
   **Verify:** Keep an assertion equivalent to `events.size() == 1 && events.get(0).getLong("input") == 100 && events.get(0).getLong("output") == 5050`. As a control, change `event.input = 100;` to `event.input = 101;`: the run must fail with an `AssertionError` from the assertion on `events.size() == 1 && events.get(0).getLong("input") == 100 && events.get(0).getLong("output") == 5050`. Restore the line before continuing.

5. **Collect a small timing distribution.** Measure the same bounded work five times and inspect sorted samples.
   **Expected:** five nonnegative samples; minimum<=maximum; checksums preserved.
   **Verify:** Keep an assertion equivalent to `samples.length == 5 && samples[0] >= 0 && samples[0] <= samples[4]`. As a control, change `long[] samples = new long[5];` to `long[] samples = new long[6];`: the run must fail with an `AssertionError` from the assertion on `samples.length == 5 && samples[0] >= 0 && samples[0] <= samples[4]`. Restore the line before continuing.

6. **Keep instrumented and uninstrumented claims separate.** Record warmup, workload and profiling state beside a measurement; refuse a universal speedup claim.
   **Expected:** metadata names 100 warmups and profiling false; universal claim false.
   **Verify:** Keep an assertion equivalent to `receipt.get("warmup_iterations").equals(100) && receipt.get("universal_speedup_claim").equals(false)`. As a control, change `100,` to `101,`: the run must fail with an `AssertionError` from the assertion on `receipt.get("warmup_iterations").equals(100) && receipt.get("universal_speedup_claim").equals(false)`. Restore the line before continuing.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: 500500. Then list the values read by `sum(1000) == 500_500L && sum(1000) == (1000L * 1001) / 2` and trace each one from its declaration. Finally, compute the asserted value with `assert sum(1001) == 500_500L && sum(1000) == (1000L * 1001) / 2;` in place before running.
- **Exercise 2:** First restate the expected observation: sink 500500 after warmup. Then list the values read by `sink == 500_500L` and trace each one from its declaration. Finally, compare `for (int i = 0; i < 100; i++) sink = sum(1001);` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: checksum 10010000; elapsed nanoseconds nonnegative. Then list the values read by `checksum == 10_010_000L && elapsed >= 0` and trace each one from its declaration. Finally, predict the effect of changing `for (int i = 0; i < 20; i++) checksum += sum(1000);` to `for (int i = 0; i <= 20; i++) checksum += sum(1000);` before running anything.
- **Exercise 4:** First restate the expected observation: one matching event with the declared fields. Then list the values read by `events.size() == 1 && events.get(0).getLong("input") == 100 && events.get(0).getLong("output") == 5050` and trace each one from its declaration. Finally, predict the effect of changing `event.input = 100;` to `event.input = 101;` before running anything.
- **Exercise 5:** First restate the expected observation: five nonnegative samples; minimum<=maximum; checksums preserved. Then list the values read by `samples.length == 5 && samples[0] >= 0 && samples[0] <= samples[4]` and trace each one from its declaration. Finally, predict the effect of changing `long[] samples = new long[5];` to `long[] samples = new long[6];` before running anything.
- **Exercise 6:** First restate the expected observation: metadata names 100 warmups and profiling false; universal claim false. Then list the values read by `receipt.get("warmup_iterations").equals(100) && receipt.get("universal_speedup_claim").equals(false)` and trace each one from its declaration. Finally, predict the effect of changing `100,` to `101,` before running anything.

## Self-check and retrieval

Close the solution and explain Warmup, Measurement bias, JFR event in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.jfr/jdk/jfr/Recording.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-032: Profiling and benchmark reasoning.
Read courses/java/guides/java-032.md and courses/java/lessons/java-032.java. Direct prerequisites: `java-031`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
