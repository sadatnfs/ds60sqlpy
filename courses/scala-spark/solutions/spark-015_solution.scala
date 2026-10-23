import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._


object Main {
  def amountRows(frame: DataFrame): Seq[(Long,Option[Long])] =
    frame.select("event_id","amount_cents").orderBy("event_id").collect().toSeq.map(row => (row.getLong(0),if(row.isNullAt(1)) None else Some(row.getLong(1))))

  def withParsed(frame: DataFrame): DataFrame = {
    frame.withColumn("parsed_amount",expr("try_cast(trim(amount_text) AS BIGINT)"))
  }

  def parseLedger(frame: DataFrame): DataFrame = {
    withParsed(frame).withColumn("parse_status",when(col("amount_text").isNull,lit("missing")).when(col("parsed_amount").isNull,lit("rejected")).otherwise(lit("valid")))
  }

  def acceptedProjection(frame: DataFrame): DataFrame = {
    parseLedger(frame).filter(col("parse_status") =!= lit("rejected")).select(col("event_id"),col("parsed_amount").as("amount_cents"))
  }

  def sqlProjection(spark: SparkSession, frame: DataFrame): DataFrame = {
    frame.createOrReplaceTempView("ds60_spark_015_raw")
    spark.sql("WITH parsed AS (SELECT event_id,amount_text,try_cast(trim(amount_text) AS BIGINT) AS amount_cents FROM ds60_spark_015_raw) SELECT event_id,amount_cents FROM parsed WHERE amount_text IS NULL OR amount_cents IS NOT NULL")
  }

  def strictProjection(frame: DataFrame): DataFrame = {
    frame.select(col("event_id"),trim(col("amount_text")).cast(LongType).as("amount_cents"))
  }

  def nonnegativeAmounts(frame: DataFrame): DataFrame = {
    acceptedProjection(frame).filter(col("amount_cents").isNull || (col("amount_cents") >= lit(0L)))
  }

  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder().appName("ds60-spark-015").master("local[2]")
      .config("spark.ui.enabled","false")
      .config("spark.driver.host","127.0.0.1")
      .config("spark.driver.bindAddress","127.0.0.1")
      .config("spark.sql.shuffle.partitions","2")
      .config("spark.sql.adaptive.enabled","false")
      .config("spark.sql.ansi.enabled","true")
      .config("spark.sql.session.timeZone","UTC").getOrCreate()
    try {
      require(spark.sparkContext.master == "local[2]", "local-only course session")
      spark.sparkContext.setLogLevel("ERROR")
      val schema = StructType(Seq(StructField("event_id",LongType,false),StructField("amount_text",StringType,true)))
      val rows = Seq(Row(1L,"100"),Row(2L,"0"),Row(3L," 25 "),Row(4L,null),Row(5L,"bad"),Row(6L,"9223372036854775808"),Row(7L,"-5"),Row(8L,"50"))
      val raw = spark.createDataFrame(spark.sparkContext.parallelize(rows,2),schema)
      // Exercise 1: Add an explicit tolerant parse column
      val parsed = withParsed(raw)
      assert(parsed.schema("parsed_amount").dataType == LongType)
      assert(parsed.orderBy("event_id").select("event_id","parsed_amount").collect().toSeq.map(row => (row.getLong(0),if(row.isNullAt(1)) None else Some(row.getLong(1)))) == Seq((1L,Some(100L)),(2L,Some(0L)),(3L,Some(25L)),(4L,None),(5L,None),(6L,None),(7L,Some(-5L)),(8L,Some(50L))))
      // Exercise 2: Classify missing versus rejected tokens
      val ledger = parseLedger(raw)
      assert(ledger.orderBy("event_id").select("parse_status").collect().map(_.getString(0)).toSeq == Seq("valid","valid","valid","missing","rejected","rejected","valid","valid"))
      assert(ledger.filter(col("parse_status") === lit("rejected")).select("event_id").orderBy("event_id").collect().map(_.getLong(0)).toSeq == Seq(5L,6L))
      // Exercise 3: Project the six parse-accepted events
      val accepted = acceptedProjection(raw)
      assert(amountRows(accepted) == Seq((1L,Some(100L)),(2L,Some(0L)),(3L,Some(25L)),(4L,None),(7L,Some(-5L)),(8L,Some(50L))))
      val metric = accepted.agg(count(lit(1)),count("amount_cents"),sum("amount_cents")).first()
      assert((metric.getLong(0),metric.getLong(1),metric.getLong(2)) == (6L,5L,170L))
      // Exercise 4: Express the same parse contract in SQL
      val expected = Seq((1L,Some(100L)),(2L,Some(0L)),(3L,Some(25L)),(4L,None),(7L,Some(-5L)),(8L,Some(50L)))
      assert(amountRows(sqlProjection(spark,raw)) == expected && amountRows(acceptedProjection(raw)) == expected)
      // Exercise 5: Observe strict ANSI failure at evaluation
      assert(spark.conf.get("spark.sql.ansi.enabled") == "true")
      assert(amountRows(strictProjection(raw.filter(!col("event_id").isin(5L,6L)))) == expected)
      var expectedCastFailure = false
      try strictProjection(raw.filter(col("event_id") === lit(5L))).collect() catch { case error: Exception =>
        expectedCastFailure = Iterator.iterate[Throwable](error)(_.getCause).take(8).takeWhile(_ != null).exists(cause => Option(cause.getMessage).exists(_.contains("CAST_INVALID_INPUT")))
      }
      assert(expectedCastFailure, "strict invalid text must produce CAST_INVALID_INPUT")
      println("Expected strict-cast diagnostic observed: CAST_INVALID_INPUT")
      // Exercise 6: Apply a separate nonnegative domain policy
      val domain = nonnegativeAmounts(raw)
      assert(amountRows(domain) == Seq((1L,Some(100L)),(2L,Some(0L)),(3L,Some(25L)),(4L,None),(8L,Some(50L))))
      val dm = domain.agg(count(lit(1)),count("amount_cents"),sum("amount_cents")).first()
      assert((dm.getLong(0),dm.getLong(1),dm.getLong(2)) == (5L,4L,175L))
      assert(accepted.filter(col("amount_cents") < lit(0L)).select("event_id").first().getLong(0) == 7L)
      assert(domain.count() + ledger.filter(col("parse_status") === lit("rejected")).count() + accepted.filter(col("amount_cents") < lit(0L)).count() == 8L)
      println("spark-015: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString)
    } finally { spark.stop() }
  }
}

// Exercise 1: Add an explicit tolerant parse column. Inputs/task: Return all source columns plus parsed_amount from try_cast(trim(amount_text) AS BIGINT). Preserve eight rows and distinguish this nullable parse result from a final validity decision. Expected: Ordered parsed values are 100,0,25, NULL, NULL, NULL,-5,50. The output parsed type is bigint. Verify: Compare all eight(event_id, parsed_amount) pairs and the field type with literals.
// Exercise 2: Classify missing versus rejected tokens. Inputs/task: Add parse_status with missing for source NULL, rejected for a nonnull source that parsed to NULL, and valid otherwise. Keep all original rows and parsed values. Expected: IDs 1,2,3,7,8 are valid, ID 4 missing, and IDs 5,6 rejected. Counts are 5,1,2 and sum to 8. Verify: Assert the ordered status list and the exact two rejected IDs.
// Exercise 3: Project the six parse-accepted events. Inputs/task: Retain valid and missing statuses, then return event_id and parsed_amount aliased as amount_cents. Reject only malformed/overflowing nonnull tokens at this stage. Expected: IDs[1,2,3,4,7,8] remain with amounts[100,0,25, NULL,-5,50]. There are 6 rows,5 known values and total 170. Verify: Assert the exact rows and independent count/known/sum metrics.
// Exercise 4: Express the same parse contract in SQL. Inputs/task: Register the raw frame as a session-local view and produce the same six event_id, amount_cents rows using a SQL parse CTE and explicit missing-or-success filter. Compare with literals rather than only with the DataFrame result. Expected: The SQL ordered rows are exactly the six rows from Exercise 3, including the NULL amount and signed-5. Verify: Assert the SQL result against the full literal row list and separately compare the DataFrame path to that list.
// Exercise 5: Observe strict ANSI failure at evaluation. Inputs/task: Return a strict trimmed BIGINT cast projection. Evaluate a valid subset successfully, then intentionally evaluate the bad token at ID 5 under ANSI mode and require a CAST_INVALID_INPUT diagnostic. Do not count an unrelated exception as success. Expected: The valid subset has the same six rows. ID 5 fails when collected, and the reference records the expected failure code before continuing. Verify: Assert ANSI readback true, valid-row results, and a caught diagnostic containing CAST_INVALID_INPUT.
// Exercise 6: Apply a separate nonnegative domain policy. Inputs/task: From parse-accepted rows, retain unknown amounts and known nonnegative amounts. Return event_id, amount_cents and report the separate negative-domain rejection at ID 7 in the checks. Expected: Final IDs[1,2,3,4,8] have 5 rows,4 known values, total 175. The full source reconciles as 5 final accepted+2 parse rejected+1 negative-domain rejected. Verify: Assert final rows/metrics, negative ID 7 and the 8-row conservation equation.
