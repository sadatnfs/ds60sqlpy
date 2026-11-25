# java-032: Profiling and benchmark reasoning

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-031`

## Learning objectives

Measure performance with warm-up, checksums and JFR events and report the result without overclaiming.

The six exercises practice these steps:

- Establish a numerical oracle.
- Warm up without hiding results.
- Measure repeated work with a checksum.
- Record and read an actual JFR event.
- Collect a small timing distribution.
- Keep instrumented and uninstrumented claims separate.

## Purpose and mental model

Performance measurement starts with a correct, representative workload. JVM execution can change during warmup as classes load and JIT compilation occurs. A first-call timing and a warmed repeated timing answer different questions. Dead-code elimination can remove unused work, while logging or profiling can add work that dominates a small calculation. A benchmark must retain observable results and record its measurement conditions.

Java Flight Recorder, JFR, records runtime events with relatively low overhead in suitable configurations, but any instrumentation can affect the workload. This lesson creates one owned recording containing a custom calculation event, then reads that event back. It does not start a persistent system recording or claim a production performance diagnosis. Simple elapsed-time samples are reported without hardcoded speed thresholds or universal conclusions.

## Vocabulary and concepts

**Warmup:** Initial execution used to separate setup/JIT effects from repeated work.

**Measurement bias:** A distortion introduced by workload choice, ordering or instrumentation.

**JFR event:** A structured runtime observation recorded under an explicit configuration.

**Observable result:** A value retained so measured work cannot be discarded as unused.

## How to run this lesson

`sum` is a plain loop with a fixed bound, `sink` is a `volatile` field that keeps results observable, and Exercise 4 writes one JFR recording to an owned temporary file that is deleted in `finally`. No check asserts a duration.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



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

Before running Example A, compute `sum(1000)` with the formula `n * (n + 1) / 2` and decide why the loop must agree with it before any timing matters. For Example B, predict the value in `sink` after 100 warmup calls. Before Exercise 3, compute the checksum of 20 calls and decide whether an elapsed time of 0 nanoseconds would make the measurement invalid.

## Exercises

1. **Establish a numerical oracle: predict an edited check.** Change Example A's assertion to `assert sum(1001) == 500_500L && sum(1000) == (1000L * 1001) / 2;`, predict whether it holds, then run and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `sum(1000) == 500_500L && sum(1000) == (1000L * 1001) / 2`.
   **Verify:** Explain why the edited assertion is false for the values that satisfy `sum(1000) == 500_500L && sum(1000) == (1000L * 1001) / 2`.

2. **Warm up without hiding results: debug a regression.** A regression in Example B's new code makes one line read `for (int i = 0; i < 100; i++) sink = sum(1001);`. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `sink == 500_500L`; the repaired line reads `for (int i = 0; i < 100; i++) sink = sum(1000);`.
   **Verify:** Explain how the changed token alters the value that `sink == 500_500L` tests.

3. **Measure repeated work with a checksum.** Time 20 calculations and sum their outputs.
   **Expected:** checksum 10010000; elapsed nanoseconds nonnegative.
   **Verify:** Control: changing `for (int i = 0; i < 20; i++) checksum += sum(1000);` to `for (int i = 0; i <= 20; i++) checksum += sum(1000);` must fail the assertion on `checksum == 10_010_000L && elapsed >= 0`.

4. **Record and read an actual JFR event.** Create a bounded recording with one Calculation event containing input 100 and output 5050.
   **Expected:** one matching event with the declared fields.
   **Verify:** Control: changing `event.input = 100;` to `event.input = 101;` must fail the assertion on `events.size() == 1 && events.get(0).getLong("input") == 100 && events.get(0).getLong("output") == 5050`.

5. **Collect a small timing distribution.** Measure the same bounded work five times and inspect sorted samples.
   **Expected:** five nonnegative samples; minimum<=maximum; checksums preserved.
   **Verify:** Control: changing `long[] samples = new long[5];` to `long[] samples = new long[6];` must fail the assertion on `samples.length == 5 && samples[0] >= 0 && samples[0] <= samples[4]`.

6. **Keep instrumented and uninstrumented claims separate.** Record warmup, workload and profiling state beside a measurement; refuse a universal speedup claim.
   **Expected:** metadata names 100 warmups and profiling false; universal claim false.
   **Verify:** Control: changing `100,` to `101,` must fail the assertion on `receipt.get("warmup_iterations").equals(100) && receipt.get("universal_speedup_claim").equals(false)`.

## Common pitfalls and diagnosis

The first timed call includes class loading and interpretation, so a single cold timing says little about steady state. If a result is never used, the JIT may remove the work entirely and report an impossibly fast loop; storing results in a `volatile` sink prevents that. One sample is noise, and comparing two runs on a busy laptop measures the laptop. Profilers and logging change what they measure. For real decisions, use a harness such as JMH.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the in-check edit calls `sum(1001)`, which returns 501,501. Then compare that with 500,500. Finally, explain why the formula check on `sum(1000)` was fine and only the edited call fails.
- **Exercise 2:** First note that the edit stores `sum(1001)` in the sink on every iteration. Then compute the value left after the loop, 501,501. Finally, compare it with 500,500 and explain why the warmup itself was not the problem.
- **Exercise 3:** First record `System.nanoTime()`, add `sum(1000)` to a checksum 20 times, and record the time again. Then compute the elapsed nanoseconds. Finally, assert a checksum of 10,010,000 and a nonnegative elapsed time without any speed threshold.
- **Exercise 4:** First enable the `course.Calculation` event on a new `Recording` and start it. Then create, begin, fill, end and commit one event with input 100 and output `sum(100)`, and dump the recording to a file. Finally, read the file back and assert one event with 100 and 5,050.
- **Exercise 5:** First create an array of five samples and time one `sum(1000)` call into each slot. Then sort the array with `Arrays.sort`. Finally, assert five nonnegative samples with the minimum no larger than the maximum, and check the sink after every run.
- **Exercise 6:** First write a receipt map with the warmup count, input size, measured iterations and profiling flag. Then add a universal speedup claim set to false. Finally, assert 100 warmups and the false claim, and explain why conditions belong beside every number.

## Self-check and retrieval

From memory, explain why correctness is checked before timing, what JIT warmup changes, how dead-code elimination can fake a fast result, and why the timing exercises assert only checksums and ordering. Say what the JFR event proves and what it does not.

## Next step

Continue with `java-033`: Secure application boundaries. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.jfr/jdk/jfr/Recording.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

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
