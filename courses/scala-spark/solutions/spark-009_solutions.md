# spark-009: Explained reference solutions

Read the [guide](../guides/spark-009.md) and attempt the [learner source](../lessons/spark-009.scala) first. The [complete reference](spark-009_solution.scala) contains each implementation and its assertions. Values, identity, missingness and failure behavior are separate checks; compilation alone does not establish any of them.

## Exercises and reasoning

### Shared domain definitions

```scala
final class Owner(val factor: Long) {
  val resource: Object = new Object()
  def bad: Long => Long = value => factor * value
}
```

### Exercise 1: Validate the prepared dependency family

Construct an org.apache.spark coordinate for a lowercase hyphenated artifact base, requiring Scala binary 2.13 and Spark target 4.0.1. Reject other binary/version tuples and malformed base names. Do not download anything.

**Expected:** spark-sql,2.13,4.0.1 yields org.apache.spark: spark-sql_2.13:4.0.1. Binary 3 or 2.12 and version 4.2.0 are outside this prepared target contract.

```scala
def artifactCoordinate(base: String, scalaBinary: String, sparkVersion: String): String = {
  require(base != null && base.matches("[a-z][a-z0-9-]*"), "invalid artifact base")
  require(scalaBinary == "2.13" && sparkVersion == "4.0.1", "unsupported prepared target tuple")
  s"org.apache.spark:${base}_${scalaBinary}:${sparkVersion}"
}
```

The function is a validator for the declared prepared target, not a general statement that other versions are invalid software. Binary suffix and Spark version both participate in artifact identity. Rejecting path-like base names prevents confusing an artifact name with a filesystem or URL selection. Returning a string proves only configuration construction; it does not prove that the artifact was resolved, compiled or run.

```scala
assert(artifactCoordinate("spark-sql","2.13","4.0.1") == "org.apache.spark:spark-sql_2.13:4.0.1")
expectIllegalArgument(artifactCoordinate("spark-sql","3","4.0.1"))
expectIllegalArgument(artifactCoordinate("spark-sql","2.12","4.0.1"))
expectIllegalArgument(artifactCoordinate("spark-sql","2.13","4.2.0"))
expectIllegalArgument(artifactCoordinate("bad/name","2.13","4.0.1"))
```

### Exercise 2: Keep execution local and bounded

Accept exactly local[2] as the course master and reject remote addresses, local[*] and null. Return the accepted value without starting a session.

**Expected:** local[2] passes; local[*], spark://example:7077 and null raise IllegalArgumentException.

```scala
def localMaster(value: String): String = {
  require(value == "local[2]", "only the prepared local[2] master is allowed")
  value
}
```

The execution target is an explicit course policy. Equality to the single allowed literal avoids silently inheriting a remote or unbounded environment. The function performs no connection and does not grant a runtime capability by itself. The later SparkSession lesson will still inspect the actual session master and its lifecycle after the prepared worker creates it.

```scala
assert(localMaster("local[2]") == "local[2]")
Seq("local[*]","spark://example:7077",null).foreach(value => expectIllegalArgument(localMaster(value)))
```

### Exercise 3: Capture data instead of a resource owner

Return a multiplier closure that copies only owner.factor into a local immutable value. Require factor and input magnitude at most 1000000 so multiplication is within Long range. Do not retain owner or its nonserializable resource.

**Expected:** Owner factor 3 produces 7->21 and-2->-6. An input outside the bounded domain is rejected. The function is suitable for the later serialization check.

```scala
def captureValue(owner: Owner): Long => Long = {
  val factor = owner.factor
  require(factor >= 0L && factor <= 1000000L, "factor outside domain")
  (value: Long) => {
    require(value >= -1000000L && value <= 1000000L, "input outside domain")
    factor * value
  }
}
```

The local val contains only the numeric factor, so the closure does not need the owner object to read a field later. The owner deliberately contains a resource that Java serialization cannot carry. Bounding both factors makes the arithmetic claim precise rather than ignoring Long overflow. The next test verifies the actual captured-state consequence instead of assuming that a visually small lambda is serializable.

```scala
val owner = new Owner(3L)
val safe = captureValue(owner)
assert(safe(7L) == 21L && safe(-2L) == -6L)
expectIllegalArgument(safe(1000001L))
```

### Exercise 4: Observe the captured object graph

Serialize a locally constructed object into an in-memory byte array and return its byte size, closing the stream. Demonstrate that the safe closure serializes and owner.bad fails with NotSerializableException.

**Expected:** The safe closure produces a positive byte count; the bad closure retaining Owner raises NotSerializableException. No file or external service is used.

```scala
def serializedSize(value: AnyRef): Int = {
  val bytes = new ByteArrayOutputStream()
  val output = new ObjectOutputStream(bytes)
  try { output.writeObject(value); output.flush(); bytes.size() }
  finally output.close()
}
```

Serialization traverses the object graph reachable from the closure. A simple arithmetic body can still fail if it retains an unsuitable owner. The positive byte-size check establishes that serialization actually occurred, while the exact exception challenges the common mistake. Stream closure is guaranteed even on failure. This is local Java serialization evidence, not proof of remote dependency availability or a safe format for untrusted input.

```scala
assert(serializedSize(safe.asInstanceOf[AnyRef]) > 0)
var rejected = false
try serializedSize(owner.bad.asInstanceOf[AnyRef]) catch { case _: NotSerializableException => rejected = true }
assert(rejected, "capturing the nonserializable owner must fail")
```

### Exercise 5: Verify behavior after a local serialization round trip

Serialize the supplied local function to memory, deserialize only those self-produced bytes and return the recovered function. Close both streams. Compare original and recovered outputs on a bounded fixture.

**Expected:** The safe factor 3 closure returns identical results after round trip for-2,0,7. The check proves more than a nonempty byte array.

```scala
def roundTrip(function: Long => Long): Long => Long = {
  val bytes = new ByteArrayOutputStream()
  val output = new ObjectOutputStream(bytes)
  try { output.writeObject(function); output.flush() } finally output.close()
  val input = new ObjectInputStream(new ByteArrayInputStream(bytes.toByteArray))
  try input.readObject().asInstanceOf[Long => Long] finally input.close()
}
```

A byte stream can be produced successfully yet fail to restore under incompatible classes or serialization behavior. Comparing function outputs after restoration checks the bounded behavior directly. The cast is justified only by the fact that this function serialized its own known function object. Loading arbitrary external serialized bytes would have a different trust and compatibility boundary and is outside this lesson.

```scala
val restored = roundTrip(safe)
assert(Seq(-2L,0L,7L).forall(value => restored(value) == safe(value)))
assert(restored(7L) == 21L)
```

### Exercise 6: Separate runtime readback from a target declaration

Return actual Scala version and Java specification version plus the declared spark_target4.0.1. Do not label the target string as an observed Spark runtime version. The prepared foundation profile should report Scala 2.13 and Java 17.

**Expected:** Keys are scala_actual, java_actual, spark_target. Scala starts with 2.13., Java is 17, and target is 4.0.1. Exact Scala patch comes from the run.

```scala
def versionReport(): Map[String, String] = {
  Map("scala_actual" -> scala.util.Properties.versionNumberString,
      "java_actual" -> System.getProperty("java.specification.version"),
      "spark_target" -> "4.0.1")
}
```

The map deliberately distinguishes observations from intentions. Scala and Java are read from the executing process, while the Spark target is the version this authored profile expects to use later. A configured target does not prove a SparkSession was created or a cluster job ran. This distinction prevents an old design tuple or a dependency string from being presented as runtime acceptance.

```scala
val report = versionReport()
assert(report.keySet == Set("scala_actual","java_actual","spark_target"))
assert(report("scala_actual").startsWith("2.13.") && report("java_actual") == "17")
assert(report("spark_target") == "4.0.1")
```

## Evidence and scope

Run the complete reference using the same prepared profile as the learner source. Its assertions check normal values, malformed or boundary inputs and conservation where relevant. The final version line records the actual compiler/runtime family used. The reference is an executable explanation, not a hidden grading service or proof that a distributed Spark job would have the same performance characteristics.
