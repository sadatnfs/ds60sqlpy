import java.nio.charset.StandardCharsets
import java.nio.file.{Files, Paths}
import scala.collection.mutable.ArrayBuffer
import scala.util.control.NonFatal
import org.apache.spark.sql.{DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

// Immutable trusted verifier. It calls the learner API with independent data.
object Ds60Verify {
  def main(args: Array[String]): Unit = {
    val checks = ArrayBuffer.empty[(String, Boolean, String)]
    def check(name: String, ok: Boolean, detail: String): Unit = checks += ((name, ok, detail))
    val spark = SparkSession
      .builder()
      .appName("ds60-spark-rows-v1")
      .master("local[2]")
      .config("spark.ui.enabled", "false")
      .config("spark.driver.host", "127.0.0.1")
      .config("spark.driver.bindAddress", "127.0.0.1")
      .config("spark.sql.shuffle.partitions", "2")
      .config("spark.sql.session.timeZone", "UTC")
      .getOrCreate()
    try {
      val schema = StructType(
        Seq(
          StructField("event_id", LongType, false),
          StructField("team", StringType, true),
          StructField("amount_cents", LongType, true),
          StructField("status", StringType, false)
        )
      )
      val rows = Seq(
        Row(1L, "A", 100L, "paid"),
        Row(2L, "A", null, "paid"),
        Row(3L, "B", 0L, "paid"),
        Row(4L, null, 50L, "paid"),
        Row(5L, "B", 150L, "void"),
        Row(6L, "A", 100L, "paid"),
        Row(7L, "C", null, "paid")
      )
      def frame(values: Seq[Row]): DataFrame =
        spark.createDataFrame(spark.sparkContext.parallelize(values, 2), schema)
      def ids(df: DataFrame): Seq[Long] =
        df.select("event_id").orderBy("event_id").collect().toSeq.map(_.getLong(0))
      def canonical(df: DataFrame): Seq[(Option[String], Long, Long, Option[Long])] =
        df.orderBy(col("team").asc_nulls_last)
          .collect()
          .toSeq
          .map(r =>
            (
              if (r.isNullAt(0)) None else Some(r.getString(0)),
              r.getLong(1),
              r.getLong(2),
              if (r.isNullAt(3)) None else Some(r.getLong(3))
            )
          )
      val expected: Seq[(Option[String], Long, Long, Option[Long])] = Seq(
        (Some("A"), 3L, 2L, Some(200L)),
        (Some("B"), 1L, 1L, Some(0L)),
        (Some("C"), 1L, 0L, None),
        (None, 1L, 1L, Some(50L))
      )
      val paid = Main.paidEvents(frame(rows))
      check(
        "paid-identities",
        ids(paid) == Seq(1L, 2L, 3L, 4L, 6L, 7L),
        "Exact paid event IDs; preserve both equal-valued events"
      )
      val summary = Main.summarize(paid)
      val expectedSchema: Seq[(String, DataType)] = Seq(
        ("team", StringType),
        ("rows", LongType),
        ("valued", LongType),
        ("total_cents", LongType)
      )
      check(
        "summary-schema",
        summary.schema.fields.map(f => (f.name, f.dataType)).toSeq == expectedSchema,
        "Four named typed output fields"
      )
      check("summary-values", canonical(summary) == expected, "NULL-aware ordered golden groups")
      check(
        "partition-invariance",
        canonical(Main.summarize(paid.repartition(3))) == expected,
        "Physical redistribution preserves the logical bag"
      )
      val transfer = Main.paidEvents(frame(rows :+ Row(8L, "D", 25L, "paid")))
      check(
        "transfer-identities",
        ids(transfer) == Seq(1L, 2L, 3L, 4L, 6L, 7L, 8L),
        "Changed input remains visible"
      )
      val transferExpected =
        expected.take(3) ++ Seq((Some("D"), 1L, 1L, Some(25L))) ++ expected.drop(3)
      check(
        "transfer-summary",
        canonical(Main.summarize(transfer)) == transferExpected,
        "Changed team and cents are computed rather than hardcoded"
      )
    } catch {
      case NonFatal(error) =>
        error.printStackTrace()
        check(
          "execution-exception",
          false,
          "Learner API raised before its typed contract completed"
        )
    } finally { spark.stop() }
    val encoded = checks
      .map { case (name, passed, detail) =>
        s"""{"name":"$name","passed":$passed,"detail":"$detail"}"""
      }
      .mkString(",")
    Files.write(
      Paths.get("checks.json"),
      (s"""{"checks":[$encoded]}""" + "\n").getBytes(StandardCharsets.UTF_8)
    )
    if (checks.isEmpty || checks.exists(!_._2)) sys.exit(1)
  }
}
