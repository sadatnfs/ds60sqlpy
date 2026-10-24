import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._


object Main {


  def schemaFields(frame: DataFrame): Seq[(String,String,Boolean)] = {
    frame.schema.fields.map(field => (field.name,field.dataType.simpleString,field.nullable)).toSeq
  }

  def teamA(frame: DataFrame): DataFrame = {
    frame.filter(col("team") === lit("A"))
  }

  def boundedIds(frame: DataFrame, limit: Int): Seq[Long] = {
    require(limit >= 0 && limit <= 20, "driver ID budget outside 0..20")
    val rows = frame.select("event_id").orderBy("event_id").limit(limit + 1).collect().map(_.getLong(0)).toSeq
    require(rows.size <= limit, "driver ID result exceeds budget")
    rows
  }

  def observedRows(frame: DataFrame): DataFrame = {
    frame.filter(col("amount_cents").isNotNull)
  }

  def canonical(frame: DataFrame): Seq[(Long,Option[String],Option[Long])] = {
    frame.select("event_id","team","amount_cents").orderBy("event_id").collect().toSeq.map { row =>
      (row.getLong(0),if (row.isNullAt(1)) None else Some(row.getString(1)),if (row.isNullAt(2)) None else Some(row.getLong(2)))
    }
  }

  def settings(spark: SparkSession): Map[String,String] = {
    Map("master" -> spark.sparkContext.master,
     "timezone" -> spark.conf.get("spark.sql.session.timeZone"),
     "shuffle" -> spark.conf.get("spark.sql.shuffle.partitions"),
     "ansi" -> spark.conf.get("spark.sql.ansi.enabled"),
     "adaptive" -> spark.conf.get("spark.sql.adaptive.enabled"),
     "ui" -> spark.sparkContext.getConf.get("spark.ui.enabled"),
     "driver_host" -> spark.sparkContext.getConf.get("spark.driver.host"),
     "driver_bind" -> spark.sparkContext.getConf.get("spark.driver.bindAddress"),
     "spark_version" -> spark.version)
  }

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
      // Exercise 1: Inspect the complete schema contract
      assert(schemaFields(raw) == Seq(("event_id","bigint",false),("team","string",true),("amount_cents","bigint",true)))
      // Exercise 2: Keep a transformation separate from its action
      val a = teamA(raw)
      assert(a.count() == 2L && raw.count() == 4L)
      assert(a.select("event_id").orderBy("event_id").collect().map(_.getLong(0)).toSeq == Seq(1L,3L))
      // Exercise 3: Bound the driver result and detect overflow of the budget
      assert(boundedIds(raw,4) == Seq(1L,2L,3L,4L))
      var oversize = false
      try boundedIds(raw,3) catch { case _: IllegalArgumentException => oversize = true }
      assert(oversize)
      assert(boundedIds(raw.filter(lit(false)),0).isEmpty)
      var invalidBudget = false
      try boundedIds(raw,21) catch { case _: IllegalArgumentException => invalidBudget = true }
      assert(invalidBudget)
      // Exercise 4: Retain observed zero while isolating unknown amounts
      val observed = observedRows(raw)
      assert(boundedIds(observed,4) == Seq(1L,3L,4L))
      assert(observed.agg(sum("amount_cents")).first().getLong(0) == 65L)
      assert(raw.filter(col("amount_cents").isNull).count() == 1L)
      // Exercise 5: Canonicalize content across physical repartitioning
      val golden = Seq((1L,Some("A"),Some(0L)),(2L,Some("B"),None),(3L,Some("A"),Some(25L)),(4L,Some("B"),Some(40L)))
      assert(canonical(raw) == golden && canonical(raw.repartition(1)) == golden && canonical(raw.repartition(3)) == golden)
      // Exercise 6: Read back the actual local session contract
      assert(settings(spark) == Map("master" -> "local[2]","timezone" -> "UTC","shuffle" -> "2","ansi" -> "true","adaptive" -> "false","ui" -> "false","driver_host" -> "127.0.0.1","driver_bind" -> "127.0.0.1","spark_version" -> "4.0.1"))
      println("spark-012: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString)
    } finally { spark.stop() }
  }
}

// Exercise 1: Inspect the complete schema contract. Inputs/task: Return ordered field triples(name, simpleString, nullable) for a DataFrame. Check the fixture rather than inferring correctness from a printed schema alone. Expected: The triples are(event_id, bigint, false),(team, string, true),(amount_cents, bigint, true). Verify: Compare the complete triples with literals in both languages, including all nullability flags.
// Exercise 2: Keep a transformation separate from its action. Inputs/task: Return a DataFrame plan selecting team A without collecting or counting inside the function. At the call site, request a count and verify IDs 1 and 3. Preserve raw. Expected: The returned frame contains two rows when evaluated;raw still has four. The function body contains only a filter transformation. Verify: Assert returned count 2, ordered IDs[1,3] and raw count 4 at explicit action sites.
// Exercise 3: Bound the driver result and detect overflow of the budget. Inputs/task: Return ordered event IDs while collecting at most limit+1 rows, with 0<=limit<=20. Reject a result larger than limit and invalid limits. Empty data with limit 0 is valid. Do not collect the full frame before checking length. Expected: The four-row fixture passes limit 4 and rejects limit 3. An empty filter with limit 0 returns empty;limit 21 is rejected before collection. Verify: Assert exact IDs, catch the oversize and invalid-budget errors, and inspect the bounded limit before the action.
// Exercise 4: Retain observed zero while isolating unknown amounts. Inputs/task: Return rows with nonnull amount_cents, keeping all columns and identities. Do not replace NULL with zero or filter out observed zero. Expected: IDs 1,3,4 remain with amounts 0,25,40, total 65. Raw still has one NULL amount at ID 2. Verify: Assert exact IDs and sum 65, and independently count the unchanged raw NULL row.
// Exercise 5: Canonicalize content across physical repartitioning. Inputs/task: Return ordered triples(event_id, optional team, optional amount) for this bounded fixture. Compare raw, repartition(1) and repartition(3) against the same literal content, not raw collect order. Expected: Every version yields (1, A,0),(2, B, NULL),(3, A,25),(4, B,40). Physical placement does not change identity, NULL state or value. Verify: Assert all three canonical outputs and keep the final event_id ordering explicit.
// Exercise 6: Read back the actual local session contract. Inputs/task: Return master, timezone, shuffle-partition, ANSI, AQE, UI, driver-binding and Spark-version settings from the active session. Compare them with this prepared profile and rely on finally for owned stop. Do not substitute a hardcoded target string for version readback. Expected: Master local[2], UTC, two shuffle partitions, ANSI true, AQE false, UI false, both driver addresses 127.0.0.1, and Spark version 4.0.1. Verify: Assert the complete settings map;record actual version output and distinguish it from worker cleanup evidence.
