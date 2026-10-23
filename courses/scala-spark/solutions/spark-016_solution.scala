import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._


object Main {
  def factIds(frame: DataFrame): Seq[Long] = frame.select("fact_id").orderBy("fact_id").collect().map(_.getLong(0)).toSeq
  def pairIds(frame: DataFrame): Seq[(Long,Long)] = frame.select("fact_id","dimension_row").orderBy("fact_id","dimension_row").collect().toSeq.map(row => (row.getLong(0),row.getLong(1)))

  def multiplicity(facts: DataFrame, dimension: DataFrame): DataFrame = {
    val f = facts.groupBy("key").agg(count(lit(1)).as("fact_rows")).as("f")
    val d = dimension.groupBy("key").agg(count(lit(1)).as("dimension_rows")).as("d")
    val joined = f.join(d,col("f.key") <=> col("d.key"),"full")
      .select(coalesce(col("f.key"),col("d.key")).as("key"),coalesce(col("fact_rows"),lit(0L)).as("fact_rows"),coalesce(col("dimension_rows"),lit(0L)).as("dimension_rows"))
    joined.withColumn("predicted_inner",when(col("key").isNull,lit(0L)).otherwise(col("fact_rows") * col("dimension_rows")))
  }

  def equalityJoin(facts: DataFrame, dimension: DataFrame): DataFrame = {
    facts.as("f").join(dimension.as("d"),col("f.key") === col("d.key"),"inner").select(col("f.fact_id"),col("d.dimension_row"),col("f.amount_cents"))
  }

  def leftJoin(facts: DataFrame, dimension: DataFrame): DataFrame = {
    facts.as("f").join(dimension.as("d"),col("f.key") === col("d.key"),"left").select(col("f.fact_id"),col("d.dimension_row"))
  }

  def membership(facts: DataFrame, dimension: DataFrame): (DataFrame,DataFrame) = {
    (facts.join(dimension,Seq("key"),"left_semi"),facts.join(dimension,Seq("key"),"left_anti"))
  }

  def nullSafeJoin(facts: DataFrame, dimension: DataFrame): DataFrame = {
    facts.as("f").join(dimension.as("d"),col("f.key") <=> col("d.key"),"inner").select(col("f.fact_id"),col("d.dimension_row"))
  }

  def safeEnrichment(facts: DataFrame, dimension: DataFrame): DataFrame = {
    val keys = dimension.agg(count(lit(1)),countDistinct(col("key"))).first()
    require(keys.getLong(0) == keys.getLong(1), "dimension keys must be nonnull and unique")
    facts.join(dimension.select("key","label"),Seq("key"),"left").select("fact_id","amount_cents","label")
  }

  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder().appName("ds60-spark-016").master("local[2]")
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
      val factSchema = StructType(Seq(StructField("fact_id",LongType,false),StructField("key",StringType,true),StructField("amount_cents",LongType,false)))
      val dimensionSchema = StructType(Seq(StructField("dimension_row",LongType,false),StructField("key",StringType,true),StructField("label",StringType,false)))
      val facts = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row(1L,"A",10L),Row(2L,"A",20L),Row(3L,"B",30L),Row(4L,"C",40L),Row(5L,null,50L),Row(6L,"D",60L)),2),factSchema)
      val dimension = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row(101L,"A","alpha1"),Row(102L,"A","alpha2"),Row(103L,"A","alpha3"),Row(104L,"B","beta"),Row(105L,null,"unknown"),Row(106L,"E","epsilon")),2),dimensionSchema)
      // Exercise 1: Build a multiplicity ledger before joining facts
      val ledger = multiplicity(facts,dimension).orderBy(col("key").asc_nulls_last).collect().toSeq.map(row => (if(row.isNullAt(0)) None else Some(row.getString(0)),row.getLong(1),row.getLong(2),row.getLong(3)))
      assert(ledger == Seq((Some("A"),2L,3L,6L),(Some("B"),1L,1L,1L),(Some("C"),1L,0L,0L),(Some("D"),1L,0L,0L),(Some("E"),0L,1L,0L),(None,1L,1L,0L)))
      assert(ledger.map(_._4).sum == 7L)
      // Exercise 2: Verify equality pairs and quantify fanout
      val expectedPairs = Seq((1L,101L),(1L,102L),(1L,103L),(2L,101L),(2L,102L),(2L,103L),(3L,104L))
      val inner = equalityJoin(facts,dimension)
      assert(pairIds(inner) == expectedPairs && inner.count() == 7L)
      assert(inner.agg(sum("amount_cents")).first().getLong(0) == 120L)
      facts.createOrReplaceTempView("ds60_spark_016_facts");dimension.createOrReplaceTempView("ds60_spark_016_dimension")
      assert(pairIds(spark.sql("SELECT f.fact_id,d.dimension_row FROM ds60_spark_016_facts f JOIN ds60_spark_016_dimension d ON f.key=d.key")) == expectedPairs)
      // Exercise 3: Count actual matches in a left join
      val left = leftJoin(facts,dimension)
      val leftPairs = left.orderBy(col("fact_id"),col("dimension_row").asc_nulls_last).collect().toSeq.map(row => (row.getLong(0),if(row.isNullAt(1)) None else Some(row.getLong(1))))
      assert(leftPairs == expectedPairs.map { case (f,d) => (f,Some(d)) } ++ Seq((4L,None),(5L,None),(6L,None)))
      val leftMetrics = left.agg(count(lit(1)),count("dimension_row"),countDistinct("fact_id")).first()
      assert((leftMetrics.getLong(0),leftMetrics.getLong(1),leftMetrics.getLong(2)) == (10L,7L,6L))
      // Exercise 4: Use semi and anti joins for membership
      val membershipFrames = membership(facts,dimension)
      assert(factIds(membershipFrames._1) == Seq(1L,2L,3L) && factIds(membershipFrames._2) == Seq(4L,5L,6L))
      assert(membershipFrames._1.count() + membershipFrames._2.count() == 6L)
      // Exercise 5: Make NULL-safe matching an explicit alternative
      assert(pairIds(nullSafeJoin(facts,dimension)) == expectedPairs :+ (5L,105L))
      // Exercise 6: Gate enrichment on a reviewed unique dimension
      var rejectedDimension = false
      try safeEnrichment(facts,dimension) catch { case _: IllegalArgumentException => rejectedDimension = true }
      assert(rejectedDimension)
      val reviewed = dimension.filter(col("dimension_row").isin(103L,104L,106L))
      val enriched = safeEnrichment(facts,reviewed)
      assert(enriched.orderBy("fact_id").collect().toSeq.map(row => (row.getLong(0),row.getLong(1),if(row.isNullAt(2)) None else Some(row.getString(2)))) == Seq((1L,10L,Some("alpha3")),(2L,20L,Some("alpha3")),(3L,30L,Some("beta")),(4L,40L,None),(5L,50L,None),(6L,60L,None)))
      assert(enriched.count() == 6L && enriched.agg(sum("amount_cents")).first().getLong(0) == 210L)
      println("spark-016: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString)
    } finally { spark.stop() }
  }
}

// Exercise 1: Build a multiplicity ledger before joining facts. Inputs/task: Return key, fact_rows, dimension_rows, predicted_inner for the union of key buckets. Merge NULL diagnostic buckets explicitly, but predict zero ordinary-equality pairs for NULL. Order keys with NULL last. Expected: A:(2,3,6), B:(1,1,1), C:(1,0,0), D:(1,0,0), E:(0,1,0), NULL:(1,1,0). Predicted inner rows sum to 7. Verify: Assert the full ledger and its summed predicted count, including unmatched right-only E and the NULL bucket.
// Exercise 2: Verify equality pairs and quantify fanout. Inputs/task: Return fact_id, dimension_row, amount_cents from an ordinary inner equality join. Compare both DataFrame and SQL pair identities with the seven literal expected pairs. Expected: Facts 1 and 2 each match dimension rows 101,102,103;fact 3 matches 104. There are 7 pairs and the repeated joined amount totals 120, while matched fact amounts total 60. Verify: Assert every pair, count 7 and pair-grain sum 120;compare a SQL join to the same pair list.
// Exercise 3: Count actual matches in a left join. Inputs/task: Return fact_id, dimension_row from an ordinary left equality join. Preserve unmatched facts with a NULL right identity and inspect rows ordered by fact_id, dimension_row. Expected: There are 10 output rows but 7 nonnull dimension_row values. Facts 4,5,6 each have one NULL-extended row;all six fact IDs remain represented. Verify: Assert the complete ordered pair/NULL list and distinguish COUNT(*)10 from COUNT(dimension_row)7.
// Exercise 4: Use semi and anti joins for membership. Inputs/task: Return a pair of DataFrames containing matched and unmatched facts under ordinary equality, using left_semi and left_anti. Preserve fact rows without right-side fanout. Expected: Semi IDs are[1,2,3], anti IDs[4,5,6]. Key A contributes two semi rows despite three dimension matches. Their bags reconcile to all six facts. Verify: Assert both exact ID lists and their combined count 6;do not use distinct to repair an inner join.
// Exercise 5: Make NULL-safe matching an explicit alternative. Inputs/task: Return fact_id, dimension_row from an inner join using NULL-safe key equality. Compare with ordinary equality and explain why the extra pair is a policy change. Expected: The ordinary seven pairs plus(5,105) produce eight pairs. No C or D match is invented. Verify: Assert all eight ordered pairs and isolate the extra NULL-key pair.
// Exercise 6: Gate enrichment on a reviewed unique dimension. Inputs/task: Reject a dimension unless key is nonnull and unique, then left-enrich facts with label while retaining fact_id and amount_cents. The supplied reviewed dimension rows 103,104,106 are the explicit accepted fixture;do not invent an arbitrary duplicate winner. Expected: The raw dimension fails. The reviewed subset yields six facts, total 210, and labels alpha 3, alpha 3, beta, NULL, NULL, NULL for IDs 1..6. Verify: Catch raw-dimension rejection, assert every enriched row and reconcile count 6, total 210.
