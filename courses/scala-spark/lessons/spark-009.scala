import java.io.{ByteArrayInputStream, ByteArrayOutputStream, ObjectInputStream, ObjectOutputStream, NotSerializableException}

object Main {
  final class Owner(val factor: Long) {
    val resource: Object = new Object()
    def bad: Long => Long = value => factor * value
  }

  def artifactCoordinate(base: String, scalaBinary: String, sparkVersion: String): String =
    throw new UnsupportedOperationException("Complete artifactCoordinate")

  def localMaster(value: String): String =
    throw new UnsupportedOperationException("Complete localMaster")

  def captureValue(owner: Owner): Long => Long =
    throw new UnsupportedOperationException("Complete captureValue")

  def serializedSize(value: AnyRef): Int =
    throw new UnsupportedOperationException("Complete serializedSize")

  def roundTrip(function: Long => Long): Long => Long =
    throw new UnsupportedOperationException("Complete roundTrip")

  def versionReport(): Map[String, String] =
    throw new UnsupportedOperationException("Complete versionReport")

  def main(args: Array[String]): Unit = {
    locally {
      val binary = "2.13"
      val artifact = s"org.apache.spark:spark-sql_$binary:4.0.1"
      assert(artifact == "org.apache.spark:spark-sql_2.13:4.0.1")
      assert(!artifact.contains("_3:"))
      println(artifact)
    }
    locally {
      val offset = 7L
      val addOffset: Long => Long = value => value + offset
      assert(addOffset(3L) == 10L)
      assert(addOffset(3L) == addOffset(3L))
      println("The closure needs the immutable numeric offset")
    }
    println("spark-009: worked examples passed; six task implementations remain")
  }
}

// Exercise 1: Validate the prepared dependency family. Inputs/task: Construct an org.apache.spark coordinate for a lowercase hyphenated artifact base, requiring Scala binary 2.13 and Spark target 4.0.1. Reject other binary/version tuples and malformed base names. Do not download anything. Expected: spark-sql,2.13,4.0.1 yields org.apache.spark:spark-sql_2.13:4.0.1. Binary 3 or 2.12 and version 4.2.0 are outside this prepared target contract. Verify: Assert the exact coordinate and catch each unsupported tuple or malformed artifact base.
// Exercise 2: Keep execution local and bounded. Inputs/task: Accept exactly local[2] as the course master and reject remote addresses, local[*] and null. Return the accepted value without starting a session. Expected: local[2] passes;local[*], spark://example:7077 and null raise IllegalArgumentException. Verify: Assert the accepted literal and all three rejected values with no network action.
// Exercise 3: Capture data instead of a resource owner. Inputs/task: Return a multiplier closure that copies only owner.factor into a local immutable value. Require factor and input magnitude at most 1000000 so multiplication is within Long range. Do not retain owner or its nonserializable resource. Expected: Owner factor 3 produces 7->21 and-2->-6. An input outside the bounded domain is rejected. The function is suitable for the later serialization check. Verify: Assert both signed results and the domain rejection, then compare serializability with owner.bad in Exercise 4.
// Exercise 4: Observe the captured object graph. Inputs/task: Serialize a locally constructed object into an in-memory byte array and return its byte size, closing the stream. Demonstrate that the safe closure serializes and owner.bad fails with NotSerializableException. Expected: The safe closure produces a positive byte count; the bad closure retaining Owner raises NotSerializableException. No file or external service is used. Verify: Assert positive size for safe and catch the exact serialization exception for owner.bad.
// Exercise 5: Verify behavior after a local serialization round trip. Inputs/task: Serialize the supplied local function to memory, deserialize only those self-produced bytes and return the recovered function. Close both streams. Compare original and recovered outputs on a bounded fixture. Expected: The safe factor 3 closure returns identical results after round trip for-2,0,7. The check proves more than a nonempty byte array. Verify: Assert exact output equality for all three inputs and an expected 21 result for 7.
// Exercise 6: Separate runtime readback from a target declaration. Inputs/task: Return actual Scala version and Java specification version plus the declared spark_target4.0.1. Do not label the target string as an observed Spark runtime version. The prepared foundation profile should report Scala 2.13 and Java 17. Expected: Keys are scala_actual, java_actual, spark_target. Scala starts with 2.13., Java is 17, and target is 4.0.1. Exact Scala patch comes from the run. Verify: Assert the keys and version families, then retain the printed runtime line as platform-specific evidence.
