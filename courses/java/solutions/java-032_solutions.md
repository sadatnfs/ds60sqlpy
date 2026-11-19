# java-032: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Performance measurement starts with a correct, representative workload. JVM execution can change during warmup as classes load and JIT compilation occurs. A first-call timing and a warmed repeated timing answer different questions. Dead-code elimination can remove unused work, while logging or profiling can add work that dominates a small calculation. A benchmark must retain observable results and record its measurement conditions.

Java Flight Recorder, JFR, records runtime events with relatively low overhead in suitable configurations, but any instrumentation can affect the workload. This lesson creates one owned recording containing a custom calculation event, then reads that event back. It does not start a persistent system recording or claim a production performance diagnosis. Simple elapsed-time samples are reported without hardcoded speed thresholds or universal conclusions.

**Warmup:** Initial execution used to separate setup/JIT effects from repeated work.

**Measurement bias:** A distortion introduced by workload choice, ordering or instrumentation.

**JFR event:** A structured runtime observation recorded under an explicit configuration.

**Observable result:** A value retained so measured work cannot be discarded as unused.

## Reading the reference

System.nanoTime measures elapsed intervals, not wall-clock dates. Keep a checksum or volatile sink so the calculation result remains observable. Separate warmup iterations from measured iterations. A custom jdk.jfr.Event records declared fields; enable its event name, start the Recording, commit the event, stop and dump to an owned file. RecordingFile reads structured events for verification.

## Exercise 1: Establish a numerical oracle: predict an edited check

Task: Copy Example A into a scratch `Main.java` and change `assert sum(1000) == 500_500L && sum(1000) == (1000L * 1001) / 2;` to `assert sum(1001) == 500_500L && sum(1000) == (1000L * 1001) / 2;` inside its assertion. Before running it with `java -ea Main`, predict whether the assertion still holds and explain why; then restore it.

Correctness is checked independently before timing. A faster wrong computation is not a useful optimization.

The unchanged code is the part that Example A adds:

```java
assert sum(1000) == 500_500L && sum(1000) == (1000L * 1001) / 2;
```

**Expected:** The changed run fails with an `AssertionError` from the assertion on `sum(1000) == 500_500L && sum(1000) == (1000L * 1001) / 2`. Restoring the original line brings back the worked observation: 500500.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and explain why the edited condition is false for the values that satisfy `sum(1000) == 500_500L && sum(1000) == (1000L * 1001) / 2`. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Warm up without hiding results: debug a regression

Task: A regression changed one token in the code that Example B adds after Example A, so one line now reads `for (int i = 0; i < 100; i++) sink = sum(1001);`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.

The sink makes the result observable. This is a teaching safeguard, not a replacement for a dedicated benchmark harness such as JMH.

The unchanged code is the part that Example B adds:

```java
for (int i = 0; i < 100; i++) sink = sum(1000);
assert sink == 500_500L;
```

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `sink == 500_500L`; after it the line reads `for (int i = 0; i < 100; i++) sink = sum(1000);` again and sink 500500 after warmup.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `sink == 500_500L` for this input.

## Exercise 3: Measure repeated work with a checksum

Task: Time 20 calculations and sum their outputs.

The test checks work identity and measurement validity without asserting a particular duration. Scheduling and hardware affect the observation.

```java
long start = System.nanoTime(),
  checksum = 0;
for (int i = 0; i < 20; i++) checksum += sum(1000);
long elapsed = System.nanoTime() - start;
assert checksum == 10_010_000L && elapsed >= 0;
```

**Expected:** checksum 10010000; elapsed nanoseconds nonnegative.

**Verify:** Keep an assertion equivalent to `checksum == 10_010_000L && elapsed >= 0`. As a control, change `for (int i = 0; i < 20; i++) checksum += sum(1000);` to `for (int i = 0; i <= 20; i++) checksum += sum(1000);`: the run must fail with an `AssertionError` from the assertion on `checksum == 10_010_000L && elapsed >= 0`. Restore the line before continuing.

## Exercise 4: Record and read an actual JFR event

Task: Create a bounded recording withoneCalculation event containing input 100 and output 5050.

This verifies real recording and readback of an owned event. It does not infer CPU hotspots or allocation rates from a custom marker alone.

```java
var root = java.nio.file.Files.createTempDirectory("ds60-jfr-");
var file = root.resolve("fixture.jfr");
try {
  assert jdk.jfr.FlightRecorder.isAvailable();
  try (var recording = new jdk.jfr.Recording()) {
    recording.enable("course.Calculation").withoutThreshold();
    recording.start();
    var event = new Calculation();
    event.input = 100;
    event.begin();
    event.output = sum(100);
    event.end();
    event.commit();
    recording.stop();
    recording.dump(file);
  }
  var events = jdk.jfr.consumer.RecordingFile.readAllEvents(file)
    .stream()
    .filter(event -> event.getEventType().getName().equals("course.Calculation"))
    .toList();
  assert events.size() == 1 &&
  events.get(0).getLong("input") == 100 &&
  events.get(0).getLong("output") == 5050;
} finally {
  java.nio.file.Files.deleteIfExists(file);
  java.nio.file.Files.deleteIfExists(root);
}
```

**Expected:** one matching event with the declared fields.

**Verify:** Keep an assertion equivalent to `events.size() == 1 && events.get(0).getLong("input") == 100 && events.get(0).getLong("output") == 5050`. As a control, change `event.input = 100;` to `event.input = 101;`: the run must fail with an `AssertionError` from the assertion on `events.size() == 1 && events.get(0).getLong("input") == 100 && events.get(0).getLong("output") == 5050`. Restore the line before continuing.

## Exercise 5: Collect a small timing distribution

Task: Measure the same bounded work five times and inspect sorted samples.

A distribution is more informative than one lucky timing. Five samples remain a small teaching observation, not a statistical performance acceptance study.

```java
long[] samples = new long[5];
for (int run = 0; run < samples.length; run++) {
  long begin = System.nanoTime();
  sink = sum(1000);
  samples[run] = System.nanoTime() - begin;
  assert sink == 500_500L;
}
Arrays.sort(samples);
assert samples.length == 5 && samples[0] >= 0 && samples[0] <= samples[4];
```

**Expected:** five nonnegative samples; minimum<=maximum; checksums preserved.

**Verify:** Keep an assertion equivalent to `samples.length == 5 && samples[0] >= 0 && samples[0] <= samples[4]`. As a control, change `long[] samples = new long[5];` to `long[] samples = new long[6];`: the run must fail with an `AssertionError` from the assertion on `samples.length == 5 && samples[0] >= 0 && samples[0] <= samples[4]`. Restore the line before continuing.

## Exercise 6: Keep instrumented and uninstrumented claims separate

Task: Record warmup, workload and profiling state beside a measurement; refuse a universal speedup claim.

A useful result states its conditions. Profiling, timing and correctness are related evidence, but they should not be collapsed into one unlabeled success message.

```java
Map<String, Object> receipt = Map.of(
  "warmup_iterations",
  100,
  "n",
  1000,
  "measured_iterations",
  20,
  "profiling_during_timing",
  false,
  "universal_speedup_claim",
  false
);
assert receipt.get("warmup_iterations").equals(100) &&
receipt.get("universal_speedup_claim").equals(false);
```

**Expected:** metadata names 100 warmups and profiling false; universal claim false.

**Verify:** Keep an assertion equivalent to `receipt.get("warmup_iterations").equals(100) && receipt.get("universal_speedup_claim").equals(false)`. As a control, change `100,` to `101,`: the run must fail with an `AssertionError` from the assertion on `receipt.get("warmup_iterations").equals(100) && receipt.get("universal_speedup_claim").equals(false)`. Restore the line before continuing.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
