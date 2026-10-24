import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._


object Main {
  type Summary = Seq[(Option[String],Long,Long,Option[Long])]
  def ids(frame: DataFrame): Seq[Long] = frame.select("event_id").orderBy("event_id").collect().map(_.getLong(0)).toSeq
  def metrics(frame: DataFrame): (Long,Long,Option[Long]) = {
    val row = frame.agg(count(lit(1)),count(col("amount_cents")),sum(col("amount_cents"))).first()
    (row.getLong(0),row.getLong(1),if (row.isNullAt(2)) None else Some(row.getLong(2)))
  }
  def canonical(frame: DataFrame): Summary = {
    assert(frame.schema.fields.map(field => (field.name,field.dataType)).toSeq == Seq(
      ("team",StringType),("rows",LongType),("valued",LongType),("total_cents",LongType)))
    frame.orderBy(col("team").asc_nulls_last).collect().toSeq.map { row =>
      (if (row.isNullAt(0)) None else Some(row.getString(0)),row.getLong(1),row.getLong(2),if (row.isNullAt(3)) None else Some(row.getLong(3)))
    }
  }

  def classified(frame: DataFrame): DataFrame = {
    val reason = when(col("event_id").isNull,lit("missing_id"))
      .when(col("event_id") <= lit(0L),lit("invalid_id"))
      .when(col("status").isNull || !col("status").isin("paid","void"),lit("unknown_status"))
      .when(col("amount_cents") < lit(0L),lit("negative_amount"))
      .otherwise(lit(null).cast(StringType))
    frame.withColumn("rejection_reason",reason)
  }

  def accepted(frame: DataFrame): DataFrame = {
    classified(frame).filter(col("rejection_reason").isNull).select("source_row","event_id","team","amount_cents","status")
  }

  def quarantine(frame: DataFrame): DataFrame = {
    classified(frame).filter(col("rejection_reason").isNotNull).select("source_row","event_id","team","amount_cents","status","rejection_reason")
  }

  def summarizePaid(frame: DataFrame): DataFrame = {
    frame.filter(col("status") === lit("paid")).groupBy("team").agg(count(lit(1)).as("rows"),count(col("amount_cents")).as("valued"),sum(col("amount_cents")).as("total_cents"))
  }

  def paidProjection(frame: DataFrame): DataFrame = {
    frame.filter(col("status") === lit("paid")).select("event_id","team","amount_cents")
  }

  def auditedSqlReport(spark: SparkSession, frame: DataFrame): DataFrame = {
    val source = frame.agg(count(lit(1)),countDistinct(col("source_row")),count(col("source_row"))).first()
    require(source.getLong(0) <= 100L && source.getLong(0) == source.getLong(1) && source.getLong(0) == source.getLong(2), "invalid or oversized source identity")
    val valid = accepted(frame)
    val keys = valid.agg(count(lit(1)),countDistinct(col("event_id")),min(col("event_id"))).first()
    require(keys.getLong(0) == keys.getLong(1) && (keys.getLong(0) == 0L || keys.getLong(2) > 0L), "accepted event IDs must be positive and unique")
    require(valid.count() + quarantine(frame).count() == source.getLong(0), "source count does not reconcile")
    valid.filter(col("status") === lit("paid")).createOrReplaceTempView("ds60_spark_014_paid")
    spark.sql("SELECT team,COUNT(*) AS rows,COUNT(amount_cents) AS valued,SUM(amount_cents) AS total_cents FROM ds60_spark_014_paid GROUP BY team")
  }

  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder().appName("ds60-spark-014").master("local[2]")
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
      val schema = StructType(Seq(
        StructField("source_row",LongType,false),StructField("event_id",LongType,true),
        StructField("team",StringType,true),StructField("amount_cents",LongType,true),
        StructField("status",StringType,true)))
      val rows = Seq(
       Row(1L,1L,"A",100L,"paid"),Row(2L,2L,"A",null,"paid"),
       Row(3L,3L,"B",0L,"paid"),Row(4L,4L,null,50L,"paid"),
       Row(5L,5L,"B",150L,"void"),Row(6L,6L,"A",100L,"paid"),
       Row(7L,7L,"C",null,"paid"),Row(8L,8L,"B",25L,"paid"),
       Row(9L,9L,"E",0L,"paid"),Row(10L,10L,"D",200L,"paid"),
       Row(11L,11L,"A",10L,"mystery"),Row(12L,null,"A",5L,"paid"))
      val raw = spark.createDataFrame(spark.sparkContext.parallelize(rows,2),schema)
      // Exercise 1: Classify defects without dropping source occurrences
      val classification = classified(raw)
      assert(classification.count() == 12L)
      assert(classification.filter(col("rejection_reason").isNotNull).select("source_row","rejection_reason").orderBy("source_row").collect().toSeq.map(row => (row.getLong(0),row.getString(1))) == Seq((11L,"unknown_status"),(12L,"missing_id")))
      // Exercise 2: Create the accepted event relation
      val valid = accepted(raw)
      assert(ids(valid) == (1L to 10L) && valid.count() == 10L)
      assert(valid.filter(col("status") === lit("void")).count() == 1L)
      assert(valid.filter(col("amount_cents").isNull).count() == 2L)
      // Exercise 3: Retain a complete quarantine row
      val rejected = quarantine(raw)
      val rejectedRows = rejected.orderBy("source_row").collect().toSeq.map(row => (row.getLong(0),if (row.isNullAt(1)) None else Some(row.getLong(1)),row.getString(2),row.getLong(3),row.getString(4),row.getString(5)))
      assert(rejectedRows == Seq((11L,Some(11L),"A",10L,"mystery","unknown_status"),(12L,None,"A",5L,"paid","missing_id")))
      assert(valid.count() + rejected.count() == raw.count())
      // Exercise 4: Publish a NULL-aware paid summary
      val golden: Summary = Seq((Some("A"),3L,2L,Some(200L)),(Some("B"),2L,2L,Some(25L)),(Some("C"),1L,0L,None),(Some("D"),1L,1L,Some(200L)),(Some("E"),1L,1L,Some(0L)),(None,1L,1L,Some(50L)))
      assert(canonical(summarizePaid(valid)) == golden)
      assert(metrics(valid.filter(col("status") === lit("paid"))) == (9L,7L,Some(475L)))
      // Exercise 5: Expose projection-plus-distinct loss
      val paid = paidProjection(valid)
      assert(metrics(paid) == (9L,7L,Some(475L)))
      assert(metrics(paid.select("team","amount_cents").distinct()) == (8L,6L,Some(375L)))
      assert(ids(paid).contains(1L) && ids(paid).contains(6L))
      // Exercise 6: Gate the SQL report on identity and conservation
      assert(canonical(auditedSqlReport(spark,raw)) == golden)
      val duplicate = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row(13L,1L,"A",100L,"paid")),1),schema)
      var rejectedDuplicate = false
      try auditedSqlReport(spark,raw.unionByName(duplicate)) catch { case _: IllegalArgumentException => rejectedDuplicate = true }
      assert(rejectedDuplicate)
      println("spark-014: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString)
    } finally { spark.stop() }
  }
}

// Exercise 1: Classify defects without dropping source occurrences. Inputs/task: Add a nullable rejection_reason Column using the declared precedence:missing_id, invalid_id, unknown_status, negative_amount. Keep every source field and row. Unknown amounts are allowed;unknown statuses are not. Expected: Source row 11 has unknown_status, row 12 has missing_id, and the other 10 reasons are NULL. All 12 source_row identities remain. Verify: Assert the exact two(source_row, reason) pairs and the unchanged source count 12.
// Exercise 2: Create the accepted event relation. Inputs/task: Return source_row, event_id, team, amount_cents, status only for rows with no rejection reason. Preserve the valid void event and all accepted zero/NULL amounts. Expected: Accepted event IDs are 1 through 10, with 10 rows. Event 5 remains accepted as void;IDs 2 and 7 remain accepted with unknown amounts. Verify: Assert the complete accepted ID list, count 10, one void row and two NULL-amount rows.
// Exercise 3: Retain a complete quarantine row. Inputs/task: Return source_row, event_id, team, amount_cents, status, rejection_reason for rejected records, ordered by source_row when inspected. Keep the original values, including the missing event ID. Expected: Rows are(11,11, A,10, mystery, unknown_status) and (12, NULL, A,5, paid, missing_id). Accepted and quarantined counts sum to 12. Verify: Compare every quarantined field with literal expected rows and check count conservation independently.
// Exercise 4: Publish a NULL-aware paid summary. Inputs/task: From accepted records, filter paid and group by team into team, rows, valued, total_cents. Count every event, only nonnull amounts, and the exact Long sum. Preserve a NULL team group and a NULL-only amount group. Expected: Groups are A:(3,2,200), B:(2,2,25), C:(1,0, NULL), D:(1,1,200), E:(1,1,0), NULL:(1,1,50). Paid metrics are 9 rows,7 valued,475 cents. Verify: Assert the full typed canonical group list and the global paid metrics against independent literals.
// Exercise 5: Expose projection-plus-distinct loss. Inputs/task: Return a paid row-level projection retaining event_id, team, amount_cents. Compare it with the deliberately wrong team/amount distinct projection and explain the lost 100-cent event. Expected: The correct projection has metrics(9,7,475);the wrong projection has(8,6,375). IDs 1 and 6 must both remain despite equal team/amount values. Verify: Assert both metric tuples and verify that correct event IDs include 1 and 6 separately.
// Exercise 6: Gate the SQL report on identity and conservation. Inputs/task: Validate at most 100 unique nonmissing source_row occurrences, unique positive accepted event IDs, and accepted-plus-quarantine conservation before returning a SQL paid summary. Reject a duplicate accepted event ID. Compare SQL output to the same literal groups. Expected: The base 12-row batch passes and matches all six golden groups. Appending source_row13 with a second event_id1 rejects publication instead of choosing a winner. Verify: Assert base SQL parity and a real failure for the duplicate-ID extension;retain the validation failure rather than publishing a partial report.
