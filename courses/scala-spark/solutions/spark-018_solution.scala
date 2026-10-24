import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._


object Main {


  def parseInstants(raw: DataFrame): DataFrame = {
    raw.withColumn("event_time",to_timestamp(col("text"),"yyyy-MM-dd'T'HH:mm:ssXXX"))
  }

  def renderClock(events: DataFrame, zone: String): Seq[(Long,String)] = {
    val spark = events.sparkSession
    val previous = spark.conf.get("spark.sql.session.timeZone")
    try {
      spark.conf.set("spark.sql.session.timeZone",zone)
      events.select(col("event_id"),date_format(col("event_time"),"yyyy-MM-dd HH:mm:ss").as("clock")).orderBy("event_id").collect().toSeq.map(r => (r.getLong(0),r.getString(1)))
    } finally { spark.conf.set("spark.sql.session.timeZone",previous) }
  }

  def localDay(events: DataFrame): DataFrame = {
    val lower = to_timestamp(lit("2024-11-03T07:00:00Z"))
    val upper = to_timestamp(lit("2024-11-04T08:00:00Z"))
    events.filter(col("event_time") >= lower && col("event_time") < upper)
  }

  def localFields(spark: SparkSession): Seq[String] = {
    val previous = spark.conf.get("spark.sql.session.timeZone")
    try {
      Seq("UTC","America/Los_Angeles").map { zone =>
        spark.conf.set("spark.sql.session.timeZone",zone)
        val frame = spark.sql("SELECT CAST('2024-11-03 01:30:00' AS TIMESTAMP_NTZ) AS local_time")
        assert(frame.schema("local_time").dataType.typeName == "timestamp_ntz")
        frame.select(col("local_time").cast("string")).first().getString(0)
      }
    } finally { spark.conf.set("spark.sql.session.timeZone",previous) }
  }

  def foldEvidence(events: DataFrame): (Int,Int) = {
    val fold = events.filter(col("event_id").isin(2L,3L))
    val labels = renderClock(fold,"America/Los_Angeles").map(_._2).distinct
    val instants = fold.select(unix_timestamp(col("event_time"))).collect().map(_.getLong(0)).distinct
    (labels.size,instants.length)
  }

  def parseLedger(spark: SparkSession): DataFrame = {
    val source = spark.sql("SELECT * FROM VALUES (1,'2024-01-01T00:00:00Z'),(2,'bad'),(3,CAST(NULL AS STRING)) AS v(id,text)")
    source.withColumn("parsed",try_to_timestamp(col("text"),lit("yyyy-MM-dd'T'HH:mm:ssXXX"))).withColumn("reason",when(col("text").isNull,"missing_timestamp").when(col("parsed").isNull,"malformed_timestamp").otherwise("accepted"))
  }

  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder().appName("ds60-spark-018").master("local[2]")
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
      spark.conf.set("spark.sql.timestampType","TIMESTAMP_LTZ")
      val schema = StructType(Seq(StructField("event_id",LongType,false),StructField("text",StringType,false)))
      val raw = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row(1L,"2024-11-03T07:00:00Z"),Row(2L,"2024-11-03T01:30:00-07:00"),Row(3L,"2024-11-03T01:30:00-08:00"),Row(4L,"2024-11-04T08:00:00Z"),Row(5L,"2024-11-03T08:30:00Z"),Row(6L,"2024-11-03T06:59:59Z")),2),schema)
      // Exercise 1: Parse offset evidence into comparable instants
      val events = parseInstants(raw)
      assert(events.schema("event_time").dataType == TimestampType && events.filter(col("event_time").isNull).count() == 0L)
      val epochs = events.select(col("event_id"),unix_timestamp(col("event_time")).as("epoch")).collect().map(r => r.getLong(0)->r.getLong(1)).toMap
      assert(epochs(2L) == epochs(5L) && epochs(3L)-epochs(2L) == 3600L)
      // Exercise 2: Render a zone without changing the underlying instant
      val utc = renderClock(events,"UTC").toMap;val local = renderClock(events,"America/Los_Angeles").toMap
      assert(utc(2L) == "2024-11-03 08:30:00" && utc(3L) == "2024-11-03 09:30:00")
      assert(local(2L) == "2024-11-03 01:30:00" && local(3L) == local(2L))
      assert(spark.conf.get("spark.sql.session.timeZone") == "UTC")
      // Exercise 3: Filter a complete local day with instant boundaries
      assert(localDay(events).select("event_id").orderBy("event_id").collect().toSeq.map(_.getLong(0)) == Seq(1L,2L,3L,5L))
      assert(epochs(4L)-epochs(1L) == 25L*3600L)
      // Exercise 4: Keep an unresolved local timestamp as local fields
      assert(localFields(spark) == Seq("2024-11-03 01:30:00","2024-11-03 01:30:00"))
      assert(spark.conf.get("spark.sql.session.timeZone") == "UTC")
      // Exercise 5: Expose the information lost by a local clock key
      assert(foldEvidence(events) == (1,2))
      // Exercise 6: Quarantine invalid timestamps without confusing missingness
      val ledger = parseLedger(spark)
      assert(ledger.select("id","reason").orderBy("id").collect().toSeq.map(r => (r.getInt(0),r.getString(1))) == Seq((1,"accepted"),(2,"malformed_timestamp"),(3,"missing_timestamp")))
      assert(ledger.agg(count("parsed")).first().getLong(0) == 1L && spark.conf.get("spark.sql.ansi.enabled") == "true")
      println("spark-018: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString)
    } finally { spark.stop() }
  }
}

// Exercise 1: Parse offset evidence into comparable instants. Inputs/task: Return event_id, text, event_time by parsing the declared offset pattern yyyy-MM-ddTHH:mm:ss with a literal T and XXX offset. The session timestamp type must be LTZ. Expected: All 6 rows parse. Epoch(event 2)=epoch(event 5), and epoch(event 3)-epoch(event 2)=3600 seconds. Verify: Assert TimestampType, zero null timestamps, exact same-instant equality and the 3600-second separation.
// Exercise 2: Render a zone without changing the underlying instant. Inputs/task: Return ordered(event_id, formatted_clock) pairs for a requested zone, formatting yyyy-MM-dd HH:mm:ss. Set the zone only during materialization and restore the previous setting in finally. Expected: Events 2 and 3 render 08:30 and 09:30 underUTC but both 01:30 underAmerica/Los_Angeles. Session zone is UTC afterward. Verify: Assert both full clock strings for IDs 2/3 and the restored session configuration.
// Exercise 3: Filter a complete local day with instant boundaries. Inputs/task: Select events in the half-open interval[2024-11-03T07:00:00Z,2024-11-04T08:00:00Z). Return all event columns. Expected: Ordered event IDs[1,2,3,5]. Lower-bound ID 1 included, upper-bound ID 4 excluded and prior-second ID 6 excluded. Verify: Assert the exact ID set and the 25-hour boundary duration; do not use an inclusive BETWEEN.
// Exercise 4: Keep an unresolved local timestamp as local fields. Inputs/task: Under bothUTC andAmerica/Los_Angeles, cast 2024-11-03 01:30:00 explicitly to TIMESTAMP_NTZ, inspect its schema and render it as a string. Restore the prior zone. Expected: Both outputs are 2024-11-03 01:30:00 and the type is timestamp_ntz. No epoch or unique instant is claimed. Verify: Assert identical local clock strings and explicit type under both zones, then confirm session restoration.
// Exercise 5: Expose the information lost by a local clock key. Inputs/task: For the two fold events 2 and 3, compare local formatted labels with their epoch values. Return(label_count, instant_count), retaining original event identity. Expected: One distinct local label but two distinct instants. They must not be deduplicated by the displayed clock. Verify: Assert(1,2) using separately materialized local labels and original epoch evidence.
// Exercise 6: Quarantine invalid timestamps without confusing missingness. Inputs/task: Build an inline source containing a valid offset timestamp, bad text andNULL. Use try_to_timestamp with the declared offset pattern and classify accepted, malformed_timestamp, missing_timestamp. Expected: IDs 1,2,3 have those reasons respectively;only 1 is accepted while ANSI remains true. Verify: Assert all reason rows, one known timestamp and unchanged ANSI setting.
