import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

object Main {
  type Summary = Seq[(Option[String], Long, Long, Option[Long])]
  def ids(frame: DataFrame): Seq[Long] =
    frame.select("event_id").orderBy("event_id").collect().map(_.getLong(0)).toSeq
  def metrics(frame: DataFrame): (Long, Long, Option[Long]) = {
    val row = frame.agg(count(lit(1)), count(col("amount_cents")), sum(col("amount_cents"))).first()
    (row.getLong(0), row.getLong(1), if (row.isNullAt(2)) None else Some(row.getLong(2)))
  }
  def canonical(frame: DataFrame): Summary = {
    assert(
      frame.schema.fields.map(field => (field.name, field.dataType)).toSeq == Seq(
        ("team", StringType),
        ("rows", LongType),
        ("valued", LongType),
        ("total_cents", LongType)
      )
    )
    frame.orderBy(col("team").asc_nulls_last).collect().toSeq.map { row =>
      (
        if (row.isNullAt(0)) None else Some(row.getString(0)),
        row.getLong(1),
        row.getLong(2),
        if (row.isNullAt(3)) None else Some(row.getLong(3))
      )
    }
  }

  def classified(frame: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete classified")

  def accepted(frame: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete accepted")

  def quarantine(frame: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete quarantine")

  def summarizePaid(frame: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete summarizePaid")

  def paidProjection(frame: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete paidProjection")

  def auditedSqlReport(spark: SparkSession, frame: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete auditedSqlReport")

  def main(args: Array[String]): Unit = {
    val spark = SparkSession
      .builder()
      .appName("ds60-spark-014")
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
          StructField("source_row", LongType, false),
          StructField("event_id", LongType, true),
          StructField("team", StringType, true),
          StructField("amount_cents", LongType, true),
          StructField("status", StringType, true)
        )
      )
      val rows = Seq(
        Row(1L, 1L, "A", 100L, "paid"),
        Row(2L, 2L, "A", null, "paid"),
        Row(3L, 3L, "B", 0L, "paid"),
        Row(4L, 4L, null, 50L, "paid"),
        Row(5L, 5L, "B", 150L, "void"),
        Row(6L, 6L, "A", 100L, "paid"),
        Row(7L, 7L, "C", null, "paid"),
        Row(8L, 8L, "B", 25L, "paid"),
        Row(9L, 9L, "E", 0L, "paid"),
        Row(10L, 10L, "D", 200L, "paid"),
        Row(11L, 11L, "A", 10L, "mystery"),
        Row(12L, null, "A", 5L, "paid")
      )
      val raw = spark.createDataFrame(spark.sparkContext.parallelize(rows, 2), schema)
      locally {
        assert(raw.count() == 12L)
        assert(raw.select("source_row").distinct().count() == 12L)
        assert(raw.filter(col("event_id").isNull).select("source_row").first().getLong(0) == 12L)
        println("Source occurrence identity survives a missing business ID")
      }
      locally {
        val unknown = raw
          .filter(col("amount_cents").isNull)
          .select("event_id")
          .orderBy("event_id")
          .collect()
          .map(_.getLong(0))
          .toSeq
        val zero = raw
          .filter(col("amount_cents") === lit(0L))
          .select("event_id")
          .orderBy("event_id")
          .collect()
          .map(_.getLong(0))
          .toSeq
        assert(unknown == Seq(2L, 7L) && zero == Seq(3L, 9L))
        println("Unknown amounts and observed zeros have different identities")
      }
      println("spark-014: worked examples passed; six task implementations remain")
    } finally { spark.stop() }
  }
}

// Exercise 1: Classify defects without dropping source occurrences. Inputs/task: Add a nullable rejection_reason Column using the declared precedence:missing_id, invalid_id, unknown_status, negative_amount. Keep every source field and row. Unknown amounts are allowed;unknown statuses are not. Expected: Source row 11 has unknown_status, row 12 has missing_id, and the other 10 reasons are NULL. All 12 source_row identities remain. Verify: Assert the exact two(source_row, reason) pairs and the unchanged source count 12.
// Exercise 2: Create the accepted event relation. Inputs/task: Return source_row, event_id, team, amount_cents, status only for rows with no rejection reason. Preserve the valid void event and all accepted zero/NULL amounts. Expected: Accepted event IDs are 1 through 10, with 10 rows. Event 5 remains accepted as void;IDs 2 and 7 remain accepted with unknown amounts. Verify: Assert the complete accepted ID list, count 10, one void row and two NULL-amount rows.
// Exercise 3: Retain a complete quarantine row. Inputs/task: Return source_row, event_id, team, amount_cents, status, rejection_reason for rejected records, ordered by source_row when inspected. Keep the original values, including the missing event ID. Expected: Rows are(11,11, A,10, mystery, unknown_status) and (12, NULL, A,5, paid, missing_id). Accepted and quarantined counts sum to 12. Verify: Compare every quarantined field with literal expected rows and check count conservation independently.
// Exercise 4: Publish a NULL-aware paid summary. Inputs/task: From accepted records, filter paid and group by team into team, rows, valued, total_cents. Count every event, only nonnull amounts, and the exact Long sum. Preserve a NULL team group and a NULL-only amount group. Expected: Groups are A:(3,2,200), B:(2,2,25), C:(1,0, NULL), D:(1,1,200), E:(1,1,0), NULL:(1,1,50). Paid metrics are 9 rows,7 valued,475 cents. Verify: Assert the full typed canonical group list and the global paid metrics against independent literals.
// Exercise 5: Expose projection-plus-distinct loss. Inputs/task: Return a paid row-level projection retaining event_id, team, amount_cents. Compare it with the deliberately wrong team/amount distinct projection and explain the lost 100-cent event. Expected: The correct projection has metrics(9,7,475);the wrong projection has(8,6,375). IDs 1 and 6 must both remain despite equal team/amount values. Verify: Assert both metric tuples and verify that correct event IDs include 1 and 6 separately.
// Exercise 6: Gate the SQL report on identity and conservation. Inputs/task: Validate at most 100 unique nonmissing source_row occurrences, unique positive accepted event IDs, and accepted-plus-quarantine conservation before returning a SQL paid summary. Reject a duplicate accepted event ID. Compare SQL output to the same literal groups. Expected: The base 12-row batch passes and matches all six golden groups. Appending source_row13 with a second event_id1 rejects publication instead of choosing a winner. Verify: Assert base SQL parity and a real failure for the duplicate-ID extension;retain the validation failure rather than publishing a partial report.
