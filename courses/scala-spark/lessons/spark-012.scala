import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._


object Main {


  def schemaFields(frame: DataFrame): Seq[(String,String,Boolean)] =
    throw new UnsupportedOperationException("Complete schemaFields")

  def teamA(frame: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete teamA")

  def boundedIds(frame: DataFrame, limit: Int): Seq[Long] =
    throw new UnsupportedOperationException("Complete boundedIds")

  def observedRows(frame: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete observedRows")

  def canonical(frame: DataFrame): Seq[(Long,Option[String],Option[Long])] =
    throw new UnsupportedOperationException("Complete canonical")

  def settings(spark: SparkSession): Map[String,String] =
    throw new UnsupportedOperationException("Complete settings")

  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder().appName("ds60-spark-012").master("local[2]")
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
        StructField("event_id",LongType,false),
        StructField("team",StringType,true),
        StructField("amount_cents",LongType,true)))
      val rows = Seq(Row(1L,"A",0L),Row(2L,"B",null),Row(3L,"A",25L),Row(4L,"B",40L))
      val raw = spark.createDataFrame(spark.sparkContext.parallelize(rows,2),schema)
      locally {
        val names = raw.schema.fields.map(_.name).toSeq
        assert(names == Seq("event_id","team","amount_cents"))
        assert(raw.schema("event_id").dataType == LongType)
        assert(!raw.schema("event_id").nullable && raw.schema("amount_cents").nullable)
        println(raw.schema.simpleString)
      }
      locally {
        val planned = raw.filter(col("team") === lit("A"))
        val observedCount = planned.count()
        assert(observedCount == 2L)
        assert(planned.select("event_id").orderBy("event_id").collect().map(_.getLong(0)).toSeq == Seq(1L,3L))
        println(s"team A rows=$observedCount")
      }
      println("spark-012: worked examples passed; six task implementations remain")
    } finally { spark.stop() }
  }
}

// Exercise 1: Inspect the complete schema contract. Inputs/task: Return ordered field triples(name, simpleString, nullable) for a DataFrame. Check the fixture rather than inferring correctness from a printed schema alone. Expected: The triples are(event_id, bigint, false),(team, string, true),(amount_cents, bigint, true). Verify: Compare the complete triples with literals in both languages, including all nullability flags.
// Exercise 2: Keep a transformation separate from its action. Inputs/task: Return a DataFrame plan selecting team A without collecting or counting inside the function. At the call site, request a count and verify IDs 1 and 3. Preserve raw. Expected: The returned frame contains two rows when evaluated;raw still has four. The function body contains only a filter transformation. Verify: Assert returned count 2, ordered IDs[1,3] and raw count 4 at explicit action sites.
// Exercise 3: Bound the driver result and detect overflow of the budget. Inputs/task: Return ordered event IDs while collecting at most limit+1 rows, with 0<=limit<=20. Reject a result larger than limit and invalid limits. Empty data with limit 0 is valid. Do not collect the full frame before checking length. Expected: The four-row fixture passes limit 4 and rejects limit 3. An empty filter with limit 0 returns empty;limit 21 is rejected before collection. Verify: Assert exact IDs, catch the oversize and invalid-budget errors, and inspect the bounded limit before the action.
// Exercise 4: Retain observed zero while isolating unknown amounts. Inputs/task: Return rows with nonnull amount_cents, keeping all columns and identities. Do not replace NULL with zero or filter out observed zero. Expected: IDs 1,3,4 remain with amounts 0,25,40, total 65. Raw still has one NULL amount at ID 2. Verify: Assert exact IDs and sum 65, and independently count the unchanged raw NULL row.
// Exercise 5: Canonicalize content across physical repartitioning. Inputs/task: Return ordered triples(event_id, optional team, optional amount) for this bounded fixture. Compare raw, repartition(1) and repartition(3) against the same literal content, not raw collect order. Expected: Every version yields (1, A,0),(2, B, NULL),(3, A,25),(4, B,40). Physical placement does not change identity, NULL state or value. Verify: Assert all three canonical outputs and keep the final event_id ordering explicit.
// Exercise 6: Read back the actual local session contract. Inputs/task: Return master, timezone, shuffle-partition, ANSI, AQE, UI, driver-binding and Spark-version settings from the active session. Compare them with this prepared profile and rely on finally for owned stop. Do not substitute a hardcoded target string for version readback. Expected: Master local[2], UTC, two shuffle partitions, ANSI true, AQE false, UI false, both driver addresses 127.0.0.1, and Spark version 4.0.1. Verify: Assert the complete settings map;record actual version output and distinguish it from worker cleanup evidence.
