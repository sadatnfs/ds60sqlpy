import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._


object Main {
  val payloadSchema = StructType(Seq(StructField("parent_id",LongType,true),StructField("items",ArrayType(StructType(Seq(StructField("sku",StringType,true),StructField("qty",LongType,true))),true),true),StructField("_corrupt_record",StringType,true)))
  def rows(frame: DataFrame): Seq[String] = frame.toJSON.collect().toSeq

  def parseRecords(raw: DataFrame): DataFrame = {
    raw.withColumn("doc",from_json(col("raw"),payloadSchema,Map("mode"->"PERMISSIVE","columnNameOfCorruptRecord"->"_corrupt_record")))
    .withColumn("reason",when(col("raw").isNull,lit("missing_payload")).when(col("doc._corrupt_record").isNotNull,lit("malformed_json")).when(col("doc.parent_id").isNull,lit("missing_parent")).otherwise(lit("accepted")))
  }

  def parentLedger(parsed: DataFrame): DataFrame = {
    parsed.filter(col("reason") === "accepted").select(col("source_id"),col("doc.parent_id").as("parent_id"),col("doc.items").as("items")).withColumn("array_state",when(col("items").isNull,"unknown").when(size(col("items")) === 0,"empty").otherwise("populated"))
  }

  def children(parents: DataFrame): DataFrame = {
    parents.select(col("parent_id"),posexplode(col("items")).as(Seq("position","item"))).select(col("parent_id"),col("position"),col("item.sku").as("sku"),col("item.qty").as("qty"))
  }

  def outerChildren(parents: DataFrame): DataFrame = {
    parents.select(col("parent_id"),col("array_state"),posexplode_outer(col("items")).as(Seq("position","item"))).select(col("parent_id"),col("array_state"),col("position"),col("item.sku").as("sku"),col("item.qty").as("qty"))
  }

  def summarizeChildren(outer: DataFrame): DataFrame = {
    outer.groupBy("parent_id","array_state").agg(count("position").as("child_count"),count("qty").as("known_qty_count"),sum("qty").as("total_qty"))
  }

  def arrayRelationships(spark: SparkSession): (DataFrame,DataFrame) = {
    val source = spark.sql("SELECT array('a','b') AS skus, array('web','shop','api') AS channels")
    val cross = source.select(explode(col("skus")).as("sku"),col("channels")).select(col("sku"),explode(col("channels")).as("channel"))
    val zipped = source.select(posexplode(arrays_zip(col("skus"),col("channels"))).as(Seq("position","pair"))).select(col("position"),col("pair.skus").as("sku"),col("pair.channels").as("channel"))
    (cross,zipped)
  }

  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder().appName("ds60-spark-017").master("local[2]")
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
      val inputSchema = StructType(Seq(StructField("source_id",LongType,false),StructField("raw",StringType,true)))
      val raw = spark.createDataFrame(spark.sparkContext.parallelize(Seq(
       Row(1L,"""{"parent_id":10,"items":[{"sku":"a","qty":2},{"sku":"a","qty":3}]}"""),
       Row(2L,"""{"parent_id":20,"items":[]}"""),Row(3L,"""{"parent_id":30,"items":null}"""),
       Row(4L,"""{"parent_id":40,"items":[{"sku":"b","qty":null}]}"""),
       Row(5L,"{bad"),Row(6L,"""{"items":[]}"""),Row(7L,null)),2),inputSchema)
      // Exercise 1: Parse once and retain rejection evidence
      val parsed = parseRecords(raw)
      assert(parsed.select("source_id","reason").orderBy("source_id").collect().toSeq.map(r => (r.getLong(0),r.getString(1))) == Seq((1L,"accepted"),(2L,"accepted"),(3L,"accepted"),(4L,"accepted"),(5L,"malformed_json"),(6L,"missing_parent"),(7L,"missing_payload")))
      assert(parsed.count() == 7L)
      // Exercise 2: Record collection state before changing grain
      val parents = parentLedger(parsed)
      assert(parents.select("parent_id","array_state").orderBy("parent_id").collect().toSeq.map(r => (r.getLong(0),r.getString(1))) == Seq((10L,"populated"),(20L,"empty"),(30L,"unknown"),(40L,"populated")))
      assert(parents.filter(col("parent_id") === 10L).select(size(col("items"))).first().getInt(0) == 2)
      // Exercise 3: Flatten observed child occurrences
      val child = children(parents)
      assert(child.orderBy("parent_id","position").collect().toSeq.map(r => (r.getLong(0),r.getInt(1),r.getString(2),if(r.isNullAt(3)) None else Some(r.getLong(3)))) == Seq((10L,0,"a",Some(2L)),(10L,1,"a",Some(3L)),(40L,0,"b",None)))
      assert(child.select("parent_id","position").distinct().count() == 3L)
      // Exercise 4: Preserve parents without inventing observed children
      val outer = outerChildren(parents)
      val metrics = outer.agg(count(lit(1)),countDistinct("parent_id"),count("position")).first()
      assert((metrics.getLong(0),metrics.getLong(1),metrics.getLong(2)) == (5L,4L,3L))
      assert(outer.filter(col("position").isNull).select("parent_id","array_state").orderBy("parent_id").collect().toSeq.map(r => (r.getLong(0),r.getString(1))) == Seq((20L,"empty"),(30L,"unknown")))
      // Exercise 5: Reconcile child counts and nullable measures
      val summary = summarizeChildren(outer).orderBy("parent_id")
      assert(summary.select("parent_id","child_count","known_qty_count","total_qty").collect().toSeq.map(r => (r.getLong(0),r.getLong(1),r.getLong(2),if(r.isNullAt(3)) None else Some(r.getLong(3)))) == Seq((10L,2L,2L,Some(5L)),(20L,0L,0L,None),(30L,0L,0L,None),(40L,1L,0L,None)))
      // Exercise 6: Choose Cartesian or positional array semantics
      val relations = arrayRelationships(spark)
      assert(relations._1.collect().toSeq.map(r => (r.getString(0),r.getString(1))).toSet == (for(s <- Set("a","b"); c <- Set("web","shop","api")) yield (s,c)))
      assert(relations._2.orderBy("position").collect().toSeq.map(r => (r.getInt(0),if(r.isNullAt(1)) None else Some(r.getString(1)),r.getString(2))) == Seq((0,Some("a"),"web"),(1,Some("b"),"shop"),(2,None,"api")))
      println("spark-017: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString)
    } finally { spark.stop() }
  }
}

// Exercise 1: Parse once and retain rejection evidence. Inputs/task: Parse raw with the explicit payload schema and PERMISSIVE mode, then add reason using precedence missing_payload, malformed_json, missing_parent, accepted. Preserve source_id and raw. Expected: Sources 1-4 accepted;5 malformed_json;6 missing_parent;7 missing_payload. No source disappears and accepted count is 4. Verify: Assert all seven ordered source/reason rows and reconcile accepted 4 plus rejected 3 with input 7.
// Exercise 2: Record collection state before changing grain. Inputs/task: For accepted records return source_id, parent_id, items, array_state, with array_state unknown, empty or populated. Keep arrays typed and preserve the two repeated SKU occurrences. Expected: Parent 10 populated,20 empty,30 unknown,40 populated. Parent 10 has size 2;parent 40 size 1. Verify: Assert the four parent/state rows and item lengths independently of any later explode output.
// Exercise 3: Flatten observed child occurrences. Inputs/task: Use posexplode to return parent_id, position, sku, qty for actual items. Order by parent_id and position, and retain repeated SKU a. Expected: Rows(10,0, a,2),(10,1, a,3),(40,0, b, NULL). Exactly 3 children;parents 20 and 30 produce none. Verify: Assert the entire three-row occurrence list and unique(parent_id, position) count 3.
// Exercise 4: Preserve parents without inventing observed children. Inputs/task: Use posexplode_outer, preserving parent_id and array_state along with position, sku, qty. Keep null placeholders for empty and unknown arrays. Expected: Five rows:the three observed children plus(20, empty, NULL, NULL, NULL) and (30, unknown, NULL, NULL, NULL). Verify: Assert five rows, four distinct parents and exactly three nonnull generated positions.
// Exercise 5: Reconcile child counts and nullable measures. Inputs/task: Aggregate the outer relation to parent_id, array_state, child_count, known_qty_count, total_qty. Count positions for children and preserve SUM NULL when there are no known quantities. Expected: Parent 10:(2,2,5);20:(0,0, NULL);30:(0,0, NULL);40:(1,0, NULL). Empty and unknown collection states remain visible. Verify: Assert each parent count tuple and that summed child_count is 3 while known_qty_count is 2.
// Exercise 6: Choose Cartesian or positional array semantics. Inputs/task: For one parent with SKUs[a, b] and channels[web, shop, api], return both independent exploded pairs and arrays_zip positional rows. Explain the relationship required for each interpretation. Expected: Independent generators produce 6 pairs;zip produces(a, web),(b, shop),(NULL, api), three rows. Verify: Assert the complete Cartesian pair set and all three ordered zipped rows including the paddedNULL.
