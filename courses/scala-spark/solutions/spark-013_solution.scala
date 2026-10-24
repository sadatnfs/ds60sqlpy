import org.apache.spark.sql.{DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

object Main {
  type Summary = Seq[(Option[String], Long, Long, Option[Long])]

  def ids(df: DataFrame): Seq[Long] =
    df.select("event_id").orderBy("event_id").collect()
      .map(_.getLong(0)).toSeq

  def metrics(df: DataFrame): (Long, Long, Option[Long]) = {
    val row = df.agg(
      count(lit(1)).as("rows"),
      count(col("amount_cents")).as("valued"),
      sum(col("amount_cents")).as("total_cents")
    ).first()
    (row.getLong(0), row.getLong(1),
      if (row.isNullAt(2)) None else Some(row.getLong(2)))
  }

  def summarize(df: DataFrame): DataFrame =
    df.groupBy("team").agg(
      count(lit(1)).as("rows"),
      count(col("amount_cents")).as("valued"),
      sum(col("amount_cents")).as("total_cents")
    )

  def canonical(df: DataFrame): Summary = {
    val expectedSchema: Seq[(String, DataType)] = Seq(
      ("team", StringType), ("rows", LongType),
      ("valued", LongType), ("total_cents", LongType)
    )
    assert(df.schema.fields.map(f => (f.name, f.dataType)).toSeq == expectedSchema)
    df.orderBy(col("team").asc_nulls_last).collect().toSeq.map { row =>
      (if (row.isNullAt(0)) None else Some(row.getString(0)),
        row.getLong(1), row.getLong(2),
        if (row.isNullAt(3)) None else Some(row.getLong(3)))
    }
  }

  def paidEvents(raw: DataFrame): DataFrame =
    raw.filter(col("status") === lit("paid"))

  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder().appName("ds60-spark-013-solution")
      .master("local[2]")
      .config("spark.ui.enabled", "false")
      .config("spark.driver.host", "127.0.0.1")
      .config("spark.driver.bindAddress", "127.0.0.1")
      .config("spark.sql.shuffle.partitions", "2")
      .config("spark.sql.session.timeZone", "UTC").getOrCreate()
    try {
      require(spark.sparkContext.master == "local[2]")
      val schema = StructType(Seq(
        StructField("event_id", LongType, false),
        StructField("team", StringType, true),
        StructField("amount_cents", LongType, true),
        StructField("status", StringType, false)
      ))
      val rows = Seq(
        Row(1L, "A", 100L, "paid"), Row(2L, "A", null, "paid"),
        Row(3L, "B", 0L, "paid"), Row(4L, null, 50L, "paid"),
        Row(5L, "B", 150L, "void"), Row(6L, "A", 100L, "paid"),
        Row(7L, "C", null, "paid")
      )
      val raw = spark.createDataFrame(
        spark.sparkContext.parallelize(rows, 2), schema
      )
      val paid = paidEvents(raw)
      val golden: Summary = Seq(
        (Some("A"), 3L, 2L, Some(200L)),
        (Some("B"), 1L, 1L, Some(0L)),
        (Some("C"), 1L, 0L, None),
        (None, 1L, 1L, Some(50L))
      )

      // Exercise 1: assert grain and retained/excluded identities.
      assert(ids(raw) == Seq(1L, 2L, 3L, 4L, 5L, 6L, 7L))
      assert(raw.filter(col("event_id").isNull).count() == 0L)
      assert(raw.count() == 7L)
      assert(raw.select("event_id").distinct().count() == 7L)
      assert(ids(paid) == Seq(1L, 2L, 3L, 4L, 6L, 7L))
      assert(ids(raw.filter(col("status") =!= lit("paid"))) == Seq(5L))
      assert(paid.count() == 6L)
      assert(paid.columns.contains("event_id"))

      // Exercise 2: counts and exact integer cents are different contracts.
      assert(metrics(raw) == (7L, 5L, Some(400L)))
      assert(metrics(paid) == (6L, 4L, Some(250L)))

      // Exercise 3: preserve NULL, observed zero and the NULL-key group.
      assert(canonical(summarize(paid)) == golden)

      // Exercise 4: use explicit missingness or NULL-safe equality.
      assert(ids(paid.filter(col("amount_cents").isNull)) == Seq(2L, 7L))
      assert(ids(paid.filter(col("amount_cents") === lit(0L))) == Seq(3L))
      assert(ids(paid.filter(col("team").isNull)) == Seq(4L))
      assert(ids(paid.filter(col("team") === lit(null))).isEmpty)
      assert(ids(paid.filter(col("team") <=> lit(null))) == Seq(4L))

      // Exercise 5: show the incorrect shortcut, then preserve the real bag.
      val wrong = paid.select("team", "amount_cents").distinct()
      assert(metrics(wrong) == (5L, 3L, Some(150L)))
      assert(metrics(paid) == (6L, 4L, Some(250L)))
      assert(canonical(summarize(paid.repartition(3))) == golden)

      // Exercise 6: SQL and DataFrames each compare to independent literals.
      paid.createOrReplaceTempView("ds60_spark_013_paid")
      val sqlResult = spark.sql("""
        SELECT team, COUNT(*) AS rows,
               COUNT(amount_cents) AS valued,
               SUM(amount_cents) AS total_cents
        FROM ds60_spark_013_paid
        GROUP BY team
        ORDER BY team ASC NULLS LAST
      """)
      assert(canonical(sqlResult) == golden)
      assert(raw.count() == paid.count() + 1L)
      assert(metrics(paid)._3.contains(250L))
      println("Scala checks passed: 7 raw, 6 paid, 4 observed, 250 cents.")
    } finally {
      spark.stop()
    }
  }
}
