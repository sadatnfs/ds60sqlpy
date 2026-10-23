# java-032: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Performance measurement starts with a correct,representative workload. JVM execution can change during warmup as classes load andJIT compilation occurs. A first-call timing and a warmed repeated timing answer different questions. Dead-code elimination can remove unused work,while logging orprofiling can add work that dominates a small calculation. A benchmark must retain observable results andrecord its measurement conditions.

Java Flight Recorder,JFR,records runtime events with relatively low overhead in suitable configurations,but any instrumentation can affect the workload. This lesson creates one owned recording containing a custom calculation event,then reads that event back. It doesnot start a persistent system recording orclaim a production performance diagnosis. Simple elapsed-time samples are reported without hardcoded speed thresholds oruniversal conclusions.

**Warmup:** Initial execution used toseparate setup/JIT effects from repeated work.

**Measurement bias:** A distortion introduced by workload choice,ordering orinstrumentation.

**JFR event:** A structured runtime observation recorded under an explicit configuration.

**Observable result:** A value retained so measured work cannot be discarded as unused.

## Reading the reference

System.nanoTime measures elapsed intervals,not wall-clock dates. Keep a checksum orvolatile sink so the calculation result remains observable. Separate warmup iterations from measured iterations. A customjdk.jfr.Event records declared fields;enable its event name,start theRecording,commit theevent,stop anddump to anownedfile. RecordingFile reads structured events forverification.

## Exercise 1: Establish a numerical oracle

Task: Sum1..1000 with a loop andcompare withn*(n+1)/2.

Correctness is checked independently before timing. A faster wrong computation is not a useful optimization.

```java
assert sum(1000)==500_500L && sum(1000)==1000L*1001/2;
```

**Expected:** 500500.

**Verify:** Compare the program values or named exception with 500500. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Warm up without hiding results

Task: Run the calculation100times andstore eachresult in a volatile sink.

The sink makes the result observable. This is a teaching safeguard,not a replacement for a dedicated benchmark harness such asJMH.

```java
for(int i=0;i<100;i++)sink=sum(1000);assert sink==500_500L;
```

**Expected:** sink500500 afterwarmup.

**Verify:** Compare the program values or named exception with sink500500 afterwarmup. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Measure repeated work with a checksum

Task: Time20calculations andsum their outputs.

The test checks work identity andmeasurement validity without asserting a particular duration. Scheduling andhardware affect the observation.

```java
long start=System.nanoTime(),checksum=0;for(int i=0;i<20;i++)checksum+=sum(1000);long elapsed=System.nanoTime()-start;
assert checksum==10_010_000L && elapsed>=0;
```

**Expected:** checksum10010000;elapsednanosecondsnonnegative.

**Verify:** Compare the program values or named exception with checksum10010000;elapsednanosecondsnonnegative. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Record andread an actualJFR event

Task: Create a bounded recording withoneCalculation event containinginput100 andoutput5050.

This verifies real recording andreadback of anowned event. It doesnot inferCPU hotspots orallocation rates from a custommarker alone.

```java
var root=java.nio.file.Files.createTempDirectory("ds60-jfr-");var file=root.resolve("fixture.jfr");
try {
    assert jdk.jfr.FlightRecorder.isAvailable();
    try(var recording=new jdk.jfr.Recording()) {
        recording.enable("course.Calculation").withoutThreshold();recording.start();var event=new Calculation();event.input=100;event.begin();event.output=sum(100);event.end();event.commit();recording.stop();recording.dump(file);
    }
    var events=jdk.jfr.consumer.RecordingFile.readAllEvents(file).stream().filter(event -> event.getEventType().getName().equals("course.Calculation")).toList();
    assert events.size()==1 && events.get(0).getLong("input")==100 && events.get(0).getLong("output")==5050;
} finally {java.nio.file.Files.deleteIfExists(file);java.nio.file.Files.deleteIfExists(root);}
```

**Expected:** one matching event withthedeclared fields.

**Verify:** Compare the program values or named exception with one matching event withthedeclared fields. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Collect a small timing distribution

Task: Measure the same boundedworkfive times andinspect sorted samples.

A distribution is more informative than one lucky timing. Five samples remain a small teaching observation,not a statistical performance acceptance study.

```java
long[] samples=new long[5];for(int run=0;run<samples.length;run++){long begin=System.nanoTime();sink=sum(1000);samples[run]=System.nanoTime()-begin;assert sink==500_500L;}
Arrays.sort(samples);assert samples.length==5 && samples[0]>=0 && samples[0]<=samples[4];
```

**Expected:** five nonnegative samples;minimum<=maximum;checksums preserved.

**Verify:** Compare the program values or named exception with five nonnegative samples;minimum<=maximum;checksums preserved. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Keep instrumented anduninstrumented claims separate

Task: Record warmup,workload andprofiling state beside a measurement;refuse a universal speedup claim.

A useful result states its conditions. Profiling,timing andcorrectness are related evidence,but they shouldnot be collapsed into one unlabeled success message.

```java
Map<String,Object> receipt=Map.of("warmup_iterations",100,"n",1000,"measured_iterations",20,"profiling_during_timing",false,"universal_speedup_claim",false);
assert receipt.get("warmup_iterations").equals(100) && receipt.get("universal_speedup_claim").equals(false);
```

**Expected:** metadata names100warmups andprofilingfalse;universal claimfalse.

**Verify:** Compare the program values or named exception with metadata names100warmups andprofilingfalse;universal claimfalse. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
