# spark-009: Packages, build inputs, and closure serialization

Authored tutorial and practice content. The prepared Scala/JVM worker executes a bounded program; process success and understanding remain distinct. No source file installs a tool or downloads a dependency.

## Level and prerequisites

Beginner; approximately 105 minutes. Direct design prerequisites: `spark-008`. The lesson uses Scala 2.13 syntax and the prepared JDK 17 worker. The older design document proposed a different Spark/JDK tuple; use the current [execution baseline](../execution-baseline.md) for this authored material.

## How to run this lesson

Open `spark-009` in the classroom, select the Scala source, prepare the `scala-jvm` profile and run the saved pad. The worker stages the single source as `Main.scala` and invokes `object Main`. Read the terminal output and exact assertions. The [learner source](../lessons/spark-009.scala) runs two complete demonstrations; its six task functions remain explicit stubs until you implement them. Preserve your saved attempt. The [reference program](../solutions/spark-009_solution.scala) and [explained solutions](../solutions/spark-009_solutions.md) are separate and should be opened after an attempt or an explicit worked-comparison request. If the profile is unavailable, reading and saving remain available; opening this guide does not prepare a runtime.

## Learning objectives

- Separate source code, compiled artifacts and dependency coordinates before distributing functions.
- Explain the result of both worked examples before running them.
- Implement the six contracts, inspect normal and boundary evidence, and explain a counterexample in your own words.

## Vocabulary and concepts

- **Dependency coordinate:** A structured artifact identity containing organization, name and version, including the Scala binary suffix when required.

- **Binary compatibility:** The ability of compiled classes to link against the runtime/library interface they expect; source similarity alone does not establish it.

- **Closure capture:** Values or object references retained by a function for use after its enclosing scope returns.

- **Serialization boundary:** The conversion of an object graph to bytes, which can fail when a captured object cannot be represented by the chosen format.

A source file, a compiled class and a dependency artifact are different objects. The classroom compiles the single Scala source as Main.scala and runs object Main. A real project can organize source into packages and build modules, but this fixed single-file pad does not implicitly run sbt, download artifacts or resolve arbitrary dependencies. A build specification should record the actual Scala binary family, JDK and Spark version separately from the source text.

Spark's Scala artifacts use a binary suffix such as spark-sql_2.13. A Scala 3 artifact or a2.12 artifact is not interchangeable merely because the package name looks similar. The authored worker target is Spark 4.0.1 with Scala binary 2.13 and JDK 17. The earlier expansion plan's4.2.0/JDK 21 tuple is a proposal, not evidence that this runtime has those versions. Each reference prints actual Scala and Java readback.

A closure retains the values it needs from an outer scope. If a class method returns value => factor*value and factor is a field, the closure may retain the owner object to access that field. If the owner also contains a nonserializable resource, the function can fail when sent through Java serialization. The failure concerns the captured object graph, not whether the arithmetic expression itself is simple.

Copying the needed immutable numeric value into a local val can produce a closure that captures only that value. This is not a universal cure for every distributed closure problem: the function's code and its referenced classes still need to be available where it runs, and external resources should not be hidden in captured state. The lesson uses a deliberately nonserializable owner and bounded pure arithmetic so the mechanism is observable.

The reference serializes only objects constructed inside its own process into an in-memory byte array. Deserialization is used only to round-trip those self-produced bytes; it is not a recipe for loading arbitrary untrusted serialized objects. A successful local round trip demonstrates that this function's captured state can be serialized under the current classes and runtime. It does not prove deployment to another JVM or executor has all compatible code and configuration.

A master URL is also an execution boundary. The fixed teaching profile accepts only local[2], not a remote cluster address or unconstrained local[*]. The version report distinguishes an actual runtime readback from the intended Spark target. This keeps source/configuration evidence separate from a future cluster deployment or performance claim.

## Worked example / walkthrough

### Worked example 1

```scala
val binary = "2.13"
val artifact = s"org.apache.spark:spark-sql_$binary:4.0.1"
assert(artifact == "org.apache.spark:spark-sql_2.13:4.0.1")
assert(!artifact.contains("_3:"))
println(artifact)
```

The suffix is part of artifact identity, not a decorative language label. This example constructs a coordinate string but performs no dependency lookup or download. Actual availability must be established by the prepared worker and its version receipt.

### Worked example 2

```scala
val offset = 7L
val addOffset: Long => Long = value => value + offset
assert(addOffset(3L) == 10L)
assert(addOffset(3L) == addOffset(3L))
println("The closure needs the immutable numeric offset")
```

The function's result depends on its argument and one captured immutable value. No external counter, file or connection is consulted. Later tests distinguish this simple captured value from an entire nonserializable owner object.

## Exercises

### Exercise 1: Validate the prepared dependency family

Construct an org.apache.spark coordinate for a lowercase hyphenated artifact base, requiring Scala binary 2.13 and Spark target 4.0.1. Reject other binary/version tuples and malformed base names. Do not download anything.

**Expected result/shape:** spark-sql,2.13,4.0.1 yields org.apache.spark: spark-sql_2.13:4.0.1. Binary 3 or 2.12 and version 4.2.0 are outside this prepared target contract.

**Verify:** Assert the exact coordinate and catch each unsupported tuple or malformed artifact base.

**Progressive hint:** Validate the tuple before interpolating the suffix and version.

### Exercise 2: Keep execution local and bounded

Accept exactly local[2] as the course master and reject remote addresses, local[*] and null. Return the accepted value without starting a session.

**Expected result/shape:** local[2] passes; local[*], spark://example:7077 and null raise IllegalArgumentException.

**Verify:** Assert the accepted literal and all three rejected values with no network action.

**Progressive hint:** This is an allowlist equality check, not a URL parser that accepts arbitrary destinations.

### Exercise 3: Capture data instead of a resource owner

Return a multiplier closure that copies only owner.factor into a local immutable value. Require factor and input magnitude at most 1000000 so multiplication is within Long range. Do not retain owner or its nonserializable resource.

**Expected result/shape:** Owner factor 3 produces 7->21 and-2->-6. An input outside the bounded domain is rejected. The function is suitable for the later serialization check.

**Verify:** Assert both signed results and the domain rejection, then compare serializability with owner.bad in Exercise 4.

**Progressive hint:** Read owner.factor before defining the returned lambda and use only that local val inside it.

### Exercise 4: Observe the captured object graph

Serialize a locally constructed object into an in-memory byte array and return its byte size, closing the stream. Demonstrate that the safe closure serializes and owner.bad fails with NotSerializableException.

**Expected result/shape:** The safe closure produces a positive byte count; the bad closure retaining Owner raises NotSerializableException. No file or external service is used.

**Verify:** Assert positive size for safe and catch the exact serialization exception for owner.bad.

**Progressive hint:** Use ByteArrayOutputStream and ObjectOutputStream with finally-based close.

### Exercise 5: Verify behavior after a local serialization round trip

Serialize the supplied local function to memory, deserialize only those self-produced bytes and return the recovered function. Close both streams. Compare original and recovered outputs on a bounded fixture.

**Expected result/shape:** The safe factor 3 closure returns identical results after round trip for-2,0,7. The check proves more than a nonempty byte array.

**Verify:** Assert exact output equality for all three inputs and an expected 21 result for 7.

**Progressive hint:** Use a new ObjectInputStream over the byte array produced in the same call.

### Exercise 6: Separate runtime readback from a target declaration

Return actual Scala version and Java specification version plus the declared spark_target4.0.1. Do not label the target string as an observed Spark runtime version. The prepared foundation profile should report Scala 2.13 and Java 17.

**Expected result/shape:** Keys are scala_actual, java_actual, spark_target. Scala starts with 2.13., Java is 17, and target is 4.0.1. Exact Scala patch comes from the run.

**Verify:** Assert the keys and version families, then retain the printed runtime line as platform-specific evidence.

**Progressive hint:** Use scala.util.Properties and System.getProperty for actual readback; keep the target key explicitly named.

## Common pitfalls

If a closure fails serialization, inspect the owner object it captures rather than only the arithmetic line. If a local round trip succeeds but executor loading fails, check code distribution and binary compatibility. If a coordinate ends in_3 or_2.12, do not substitute it for the declared_2.13 artifact. If a version report prints a hardcoded value, rename it as a target and add actual readback. If a source suggests downloading dependencies on Run, return to explicit preparation instead; the fixed lesson does not resolve arbitrary artifacts.

## Self-check

Without opening the reference, trace the listed boundary case through `artifactCoordinate`. Then explain why `versionReport` needs its declared invariant or input restriction. Name the exact assertion that would reject one tempting wrong implementation. Retain the observed values and explain how they support the lesson outcome: Separate source code, compiled artifacts and dependency coordinates before distributing functions.

## Next step

Continue to the next lesson only after you can explain the boundary behavior. The [course route](../README.md) shows authored material and runtime evidence separately.

## Primary sources and official APIs

- [Scala binary compatibility](https://docs.scala-lang.org/overviews/core/binary-compatibility-for-library-authors.html).

- [Spark 4.0.1 deployment overview](https://spark.apache.org/docs/4.0.1/cluster-overview.html).

- [Java17 ObjectOutputStream](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/io/ObjectOutputStream.html).

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-009: Packages, build inputs, and closure serialization.
Read courses/scala-spark/guides/spark-009.md and courses/scala-spark/lessons/spark-009.scala. Direct prerequisites: spark-008.
Explain the Scala 2.13 syntax and data contract, ask me to predict a concrete result, then inspect my attempt. Give one hint at a time, review exact assertion evidence and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt. Use only the prepared scala-jvm profile and preserve my saved work; do not install or download dependencies.
Done when all six contracts and their boundary cases have inspected evidence and I can explain why an incorrect implementation fails.
```
