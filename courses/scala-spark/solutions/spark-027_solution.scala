import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.spark.storage.StorageLevel

object Main {


  def transform(source: DataFrame): DataFrame = {
    source.filter(col("amount") >= 0L || col("amount").isNull).select(col("entity_id"),col("segment"),(col("amount") * 2L).as("doubled"))
  }

  def schemaContract(frame: DataFrame): Seq[(String,String)] = {
    frame.schema.fields.toSeq.map(field => (field.name,field.dataType.simpleString))
  }

  def assertSameBag(actual: DataFrame, expected: DataFrame): Unit = {
    require(schemaContract(actual) == schemaContract(expected),"schema contract mismatch")
    require(actual.exceptAll(expected).count() == 0L && expected.exceptAll(actual).count() == 0L,"bag contract mismatch")
  }

  def cachedSummary(frame: DataFrame): (Long,Long,String) = {
    frame.persist(StorageLevel.MEMORY_AND_DISK)
    try {
     require(frame.storageLevel != StorageLevel.NONE,"cache not registered")
     val rows = frame.count()
     val total = frame.agg(sum("doubled")).first().getLong(0)
     val plan = frame.filter(col("doubled") >= 0L).queryExecution.executedPlan.toString
     (rows,total,plan)
    } finally frame.unpersist(blocking=true)
  }

  def failingReuse(frame: DataFrame): Unit = {
    frame.persist(StorageLevel.MEMORY_AND_DISK)
    try {
     frame.count()
     throw new IllegalStateException("injected_after_materialize")
    } finally frame.unpersist(blocking=true)
  }

  def differenceCounts(actual: DataFrame, expected: DataFrame): (Long,Long) = {
    require(schemaContract(actual) == schemaContract(expected),"schema contract mismatch")
    (actual.exceptAll(expected).count(),expected.exceptAll(actual).count())
  }

  def main(args: Array[String]): Unit = {

    val spark = SparkSession.builder().appName("ds60-spark-027").master("local[2]")
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
      val schema = StructType(Seq(StructField("entity_id",LongType,false),StructField("segment",StringType,true),StructField("amount",LongType,true)))
      val source = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row(1L,"a",10L),Row(1L,"a",10L),Row(2L,"a",null),Row(3L,"b",0L),Row(4L,"b",20L),Row(4L,"b",20L),Row(5L,null,5L),Row(6L,"c",-5L)),2),schema)
      val goldenSchema = StructType(Seq(StructField("entity_id",LongType,false),StructField("segment",StringType,true),StructField("doubled",LongType,true)))
      val golden = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row(1L,"a",20L),Row(1L,"a",20L),Row(2L,"a",null),Row(3L,"b",0L),Row(4L,"b",40L),Row(4L,"b",40L),Row(5L,null,10L)),2),goldenSchema)
      // Exercise 1: Transform without collapsing occurrences or unknowns
      val transformed = transform(source)
      val summary = transformed.agg(count(lit(1)),sum("doubled"),count("doubled")).first()
      assert((summary.getLong(0),summary.getLong(1),summary.getLong(2)) == (7L,130L,6L))
      // Exercise 2: Define an ordered field/type contract
      assert(schemaContract(transformed) == Seq(("entity_id","bigint"),("segment","string"),("doubled","bigint")))
      val wrongType = transformed.withColumn("entity_id",col("entity_id").cast("string"))
      assert(schemaContract(wrongType) != schemaContract(golden))
      // Exercise 3: Compare schemas before duplicate-sensitive values
      assertSameBag(transformed,golden);assertSameBag(transformed.repartition(3),golden)
      var rejectedType = false
      try assertSameBag(wrongType,golden) catch { case e: IllegalArgumentException if e.getMessage.contains("schema contract") => rejectedType = true }
      assert(rejectedType)
      // Exercise 4: Register, materialize, reuse and release one cached relation
      val cached = cachedSummary(transformed)
      assert(cached._1 == 7L && cached._2 == 130L && cached._3.contains("InMemoryTableScan"))
      assert(transformed.storageLevel == StorageLevel.NONE)
      println("registered_then_materialized_rows=" + cached._1 + ";reuse_total=" + cached._2 + ";reuse_plan=" + cached._3 + ";released=true")
      // Exercise 5: Release persistence when a consumer fails
      var injected = false
      try failingReuse(transformed) catch { case e: IllegalStateException if e.getMessage == "injected_after_materialize" => injected = true }
      assert(injected && transformed.storageLevel == StorageLevel.NONE)
      assertSameBag(transform(source),golden)
      // Exercise 6: Demonstrate why set equality misses duplicate loss
      val dropped = transformed.distinct()
      assert(dropped.count() == 5L && differenceCounts(dropped,golden) == (0L,2L))
      var rejectedBag = false
      try assertSameBag(dropped,golden) catch { case e: IllegalArgumentException if e.getMessage.contains("bag contract") => rejectedBag = true }
      assert(rejectedBag)
      println("spark-027: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString)
    } finally { try { () } finally { spark.stop() } }
  }
}

// Exercise 1: Transform without collapsing occurrences or unknowns. Inputs/task: Keep rows whose amount is nonnegative orNULL, then return entity_id, segment, doubled=amount*2. Preserve duplicate occurrences and unknown values. Expected: Seven rows, known total 130 and oneNULL doubled value. The negative entity 6 row is excluded. Verify: Assert population, total and unknown count, then compare with the literal golden relation in later tasks.
// Exercise 2: Define an ordered field/type contract. Inputs/task: Return ordered(name, simple_type) pairs from the result schema. Compare with entity_id bigint, segment string, doubled bigint. Expected: Exactly those three fields in that order. Casting entity_id to string changes the contract even when printed values look alike. Verify: Assert the correct type list and a different list after the deliberate cast.
// Exercise 3: Compare schemas before duplicate-sensitive values. Inputs/task: Reject a schema mismatch first, then require both exceptAll differences to be empty. Accept a repartitioned correct result and reject the deliberate string-ID result. Expected: Correct result passes in different physical layouts;string-ID candidate fails with a named schema contract error. Verify: Assert acceptance for golden/repartitioned values and explicit schema rejection before a coercing bag comparison.
// Exercise 4: Register, materialize, reuse and release one cached relation. Inputs/task: Persist the supplied transformed relation with MEMORY_AND_DISK, materialize via count, reuse for a total and inspect a filtered consumer plan. Unpersist with blocking cleanup in finally. Expected: Count 7, total 130, an InMemoryTableScan reuse marker, and no registered storage level after return. Verify: Assert result values, cache-scan evidence and post-returnStorageLevel.NONE. Do not use a timing threshold.
// Exercise 5: Release persistence when a consumer fails. Inputs/task: Persist and materialize the relation, then raise an injected failure before a later consumer. Unpersist in finally and verify the original error reaches the caller. Expected: The injected_after_materialize error is observed and storage level isNONE afterward. Correct uncached output still passes the golden oracle. Verify: Assert the named failure, post-failure release and full golden equality on a subsequent computation.
// Exercise 6: Demonstrate why set equality misses duplicate loss. Inputs/task: Return directional exceptAll row counts after schema validation. Compare transformed.distinct with golden and require the golden validator to reject it. Expected: Distinct has 5 rows;unexpected occurrences 0 and missing expected occurrences 2. The bag validator raises a named bag contract mismatch. Verify: Assert(0,2), count 5 and the explicit negative-control rejection.
