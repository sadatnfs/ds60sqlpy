import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.spark.storage.StorageLevel

object Main {

  def transform(source: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete transform")

  def schemaContract(frame: DataFrame): Seq[(String, String)] =
    throw new UnsupportedOperationException("Complete schemaContract")

  def assertSameBag(actual: DataFrame, expected: DataFrame): Unit =
    throw new UnsupportedOperationException("Complete assertSameBag")

  def cachedSummary(frame: DataFrame): (Long, Long, String) =
    throw new UnsupportedOperationException("Complete cachedSummary")

  def failingReuse(frame: DataFrame): Unit =
    throw new UnsupportedOperationException("Complete failingReuse")

  def differenceCounts(actual: DataFrame, expected: DataFrame): (Long, Long) =
    throw new UnsupportedOperationException("Complete differenceCounts")

  def main(args: Array[String]): Unit = {

    val spark = SparkSession
      .builder()
      .appName("ds60-spark-027")
      .master("local[2]")
      .config("spark.ui.enabled", "false")
      .config("spark.driver.host", "127.0.0.1")
      .config("spark.driver.bindAddress", "127.0.0.1")
      .config("spark.sql.shuffle.partitions", "2")
      .config("spark.sql.adaptive.enabled", "false")
      .config("spark.sql.ansi.enabled", "true")
      .config("spark.sql.session.timeZone", "UTC")
      .getOrCreate()
    try {
      require(spark.sparkContext.master == "local[2]", "local-only course session")
      spark.sparkContext.setLogLevel("ERROR")
      val schema = StructType(
        Seq(
          StructField("entity_id", LongType, false),
          StructField("segment", StringType, true),
          StructField("amount", LongType, true)
        )
      )
      val source = spark.createDataFrame(
        spark.sparkContext.parallelize(
          Seq(
            Row(1L, "a", 10L),
            Row(1L, "a", 10L),
            Row(2L, "a", null),
            Row(3L, "b", 0L),
            Row(4L, "b", 20L),
            Row(4L, "b", 20L),
            Row(5L, null, 5L),
            Row(6L, "c", -5L)
          ),
          2
        ),
        schema
      )
      val goldenSchema = StructType(
        Seq(
          StructField("entity_id", LongType, false),
          StructField("segment", StringType, true),
          StructField("doubled", LongType, true)
        )
      )
      val golden = spark.createDataFrame(
        spark.sparkContext.parallelize(
          Seq(
            Row(1L, "a", 20L),
            Row(1L, "a", 20L),
            Row(2L, "a", null),
            Row(3L, "b", 0L),
            Row(4L, "b", 40L),
            Row(4L, "b", 40L),
            Row(5L, null, 10L)
          ),
          2
        ),
        goldenSchema
      )
      locally {
        assert(
          source.count() == 8L && source
            .select("entity_id", "segment", "amount")
            .distinct()
            .count() == 6L
        )
        assert(golden.count() == 7L && golden.agg(sum("doubled")).first().getLong(0) == 130L)
        println("Golden bag contains duplicates and unknown values deliberately")
      }
      locally {
        val numeric = spark.sql("SELECT CAST(1 AS BIGINT) AS entity_id")
        val textual = spark.sql("SELECT CAST('1' AS STRING) AS entity_id")
        assert(numeric.schema("entity_id").dataType != textual.schema("entity_id").dataType)
        println("Identical displayed digits can have different field types")
      }
      println("spark-027: worked examples passed; six task implementations remain")
    } finally {
      try { () }
      finally { spark.stop() }
    }
  }
}

// Exercise 1: Transform without collapsing occurrences or unknowns. Inputs/task: Keep rows whose amount is nonnegative orNULL, then return entity_id, segment, doubled=amount*2. Preserve duplicate occurrences and unknown values. Expected: Seven rows, known total 130 and oneNULL doubled value. The negative entity 6 row is excluded. Verify: Assert population, total and unknown count, then compare with the literal golden relation in later tasks.
// Exercise 2: Define an ordered field/type contract. Inputs/task: Return ordered(name, simple_type) pairs from the result schema. Compare with entity_id bigint, segment string, doubled bigint. Expected: Exactly those three fields in that order. Casting entity_id to string changes the contract even when printed values look alike. Verify: Assert the correct type list and a different list after the deliberate cast.
// Exercise 3: Compare schemas before duplicate-sensitive values. Inputs/task: Reject a schema mismatch first, then require both exceptAll differences to be empty. Accept a repartitioned correct result and reject the deliberate string-ID result. Expected: Correct result passes in different physical layouts;string-ID candidate fails with a named schema contract error. Verify: Assert acceptance for golden/repartitioned values and explicit schema rejection before a coercing bag comparison.
// Exercise 4: Register, materialize, reuse and release one cached relation. Inputs/task: Persist the supplied transformed relation with MEMORY_AND_DISK, materialize via count, reuse for a total and inspect a filtered consumer plan. Unpersist with blocking cleanup in finally. Expected: Count 7, total 130, an InMemoryTableScan reuse marker, and no registered storage level after return. Verify: Assert result values, cache-scan evidence and post-returnStorageLevel.NONE. Do not use a timing threshold.
// Exercise 5: Release persistence when a consumer fails. Inputs/task: Persist and materialize the relation, then raise an injected failure before a later consumer. Unpersist in finally and verify the original error reaches the caller. Expected: The injected_after_materialize error is observed and storage level isNONE afterward. Correct uncached output still passes the golden oracle. Verify: Assert the named failure, post-failure release and full golden equality on a subsequent computation.
// Exercise 6: Demonstrate why set equality misses duplicate loss. Inputs/task: Return directional exceptAll row counts after schema validation. Compare transformed.distinct with golden and require the golden validator to reject it. Expected: Distinct has 5 rows;unexpected occurrences 0 and missing expected occurrences 2. The bag validator raises a named bag contract mismatch. Verify: Assert(0,2), count 5 and the explicit negative-control rejection.
