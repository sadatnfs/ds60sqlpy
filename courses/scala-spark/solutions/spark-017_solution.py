from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType


payload_schema = StructType([StructField("parent_id",LongType(),True),StructField("items",ArrayType(StructType([StructField("sku",StringType(),True),StructField("qty",LongType(),True)]),True),True),StructField("_corrupt_record",StringType(),True)])

def parse_records(raw):
    return raw.withColumn("doc",F.from_json("raw",payload_schema,{"mode":"PERMISSIVE","columnNameOfCorruptRecord":"_corrupt_record"})).withColumn("reason",F.when(F.col("raw").isNull(),"missing_payload").when(F.col("doc._corrupt_record").isNotNull(),"malformed_json").when(F.col("doc.parent_id").isNull(),"missing_parent").otherwise("accepted"))

def parent_ledger(parsed):
    return parsed.filter(F.col("reason")=="accepted").select("source_id",F.col("doc.parent_id").alias("parent_id"),F.col("doc.items").alias("items")).withColumn("array_state",F.when(F.col("items").isNull(),"unknown").when(F.size("items")==0,"empty").otherwise("populated"))

def children(parents):
    return parents.select("parent_id",F.posexplode("items").alias("position","item")).select("parent_id","position",F.col("item.sku").alias("sku"),F.col("item.qty").alias("qty"))

def outer_children(parents):
    return parents.select("parent_id","array_state",F.posexplode_outer("items").alias("position","item")).select("parent_id","array_state","position",F.col("item.sku").alias("sku"),F.col("item.qty").alias("qty"))

def summarize_children(outer):
    return outer.groupBy("parent_id","array_state").agg(F.count("position").alias("child_count"),F.count("qty").alias("known_qty_count"),F.sum("qty").alias("total_qty"))

def array_relationships(spark):
    source = spark.sql("SELECT array('a','b') AS skus, array('web','shop','api') AS channels")
    cross = source.select(F.explode("skus").alias("sku"),"channels").select("sku",F.explode("channels").alias("channel"))
    zipped = source.select(F.posexplode(F.arrays_zip("skus","channels")).alias("position","pair")).select("position",F.col("pair.skus").alias("sku"),F.col("pair.channels").alias("channel"))
    return cross,zipped

def main():
    spark = (SparkSession.builder.appName("ds60-spark-017").master("local[2]")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.sql.adaptive.enabled", "false")
        .config("spark.sql.ansi.enabled", "true")
        .config("spark.sql.session.timeZone", "UTC").getOrCreate())
    try:
        assert spark.sparkContext.master == "local[2]"
        spark.sparkContext.setLogLevel("ERROR")
        input_schema = StructType([StructField("source_id",LongType(),False),StructField("raw",StringType(),True)])
        raw = spark.createDataFrame([(1,'{"parent_id":10,"items":[{"sku":"a","qty":2},{"sku":"a","qty":3}]}'),(2,'{"parent_id":20,"items":[]}'),(3,'{"parent_id":30,"items":null}'),(4,'{"parent_id":40,"items":[{"sku":"b","qty":null}]}'),(5,'{bad'),(6,'{"items":[]}'),(7,None)],schema=input_schema)
        # Exercise 1: Parse once and retain rejection evidence
        parsed = parse_records(raw)
        assert [tuple(r) for r in parsed.select("source_id","reason").orderBy("source_id").collect()] == [(1,"accepted"),(2,"accepted"),(3,"accepted"),(4,"accepted"),(5,"malformed_json"),(6,"missing_parent"),(7,"missing_payload")]
        assert parsed.count() == 7
        # Exercise 2: Record collection state before changing grain
        parents = parent_ledger(parsed)
        assert [tuple(r) for r in parents.select("parent_id","array_state").orderBy("parent_id").collect()] == [(10,"populated"),(20,"empty"),(30,"unknown"),(40,"populated")]
        assert parents.filter(F.col("parent_id")==10).select(F.size("items")).first()[0] == 2
        # Exercise 3: Flatten observed child occurrences
        child = children(parents)
        assert [tuple(r) for r in child.orderBy("parent_id","position").collect()] == [(10,0,"a",2),(10,1,"a",3),(40,0,"b",None)]
        assert child.select("parent_id","position").distinct().count() == 3
        # Exercise 4: Preserve parents without inventing observed children
        outer = outer_children(parents)
        assert tuple(outer.agg(F.count(F.lit(1)),F.countDistinct("parent_id"),F.count("position")).first()) == (5,4,3)
        assert [tuple(r) for r in outer.filter(F.col("position").isNull()).select("parent_id","array_state").orderBy("parent_id").collect()] == [(20,"empty"),(30,"unknown")]
        # Exercise 5: Reconcile child counts and nullable measures
        summary = summarize_children(outer).orderBy("parent_id")
        assert [tuple(r) for r in summary.select("parent_id","child_count","known_qty_count","total_qty").collect()] == [(10,2,2,5),(20,0,0,None),(30,0,0,None),(40,1,0,None)]
        # Exercise 6: Choose Cartesian or positional array semantics
        cross,zipped = array_relationships(spark)
        assert {tuple(r) for r in cross.collect()} == {(s,c) for s in ["a","b"] for c in ["web","shop","api"]}
        assert [tuple(r) for r in zipped.orderBy("position").collect()] == [(0,"a","web"),(1,"b","shop"),(2,None,"api")]
        print("spark-017: six PySpark reference contracts passed; Spark=" + spark.version)
    finally:
        spark.stop()

if __name__ == "__main__":
    main()

# Exercise 1: Parse once and retain rejection evidence. Inputs/task: Parse raw with the explicit payload schema and PERMISSIVE mode, then add reason using precedence missing_payload, malformed_json, missing_parent, accepted. Preserve source_id and raw. Expected: Sources 1-4 accepted;5 malformed_json;6 missing_parent;7 missing_payload. No source disappears and accepted count is 4. Verify: Assert all seven ordered source/reason rows and reconcile accepted 4 plus rejected 3 with input 7.
# Exercise 2: Record collection state before changing grain. Inputs/task: For accepted records return source_id, parent_id, items, array_state, with array_state unknown, empty or populated. Keep arrays typed and preserve the two repeated SKU occurrences. Expected: Parent 10 populated,20 empty,30 unknown,40 populated. Parent 10 has size 2;parent 40 size 1. Verify: Assert the four parent/state rows and item lengths independently of any later explode output.
# Exercise 3: Flatten observed child occurrences. Inputs/task: Use posexplode to return parent_id, position, sku, qty for actual items. Order by parent_id and position, and retain repeated SKU a. Expected: Rows(10,0, a,2),(10,1, a,3),(40,0, b, NULL). Exactly 3 children;parents 20 and 30 produce none. Verify: Assert the entire three-row occurrence list and unique(parent_id, position) count 3.
# Exercise 4: Preserve parents without inventing observed children. Inputs/task: Use posexplode_outer, preserving parent_id and array_state along with position, sku, qty. Keep null placeholders for empty and unknown arrays. Expected: Five rows:the three observed children plus(20, empty, NULL, NULL, NULL) and (30, unknown, NULL, NULL, NULL). Verify: Assert five rows, four distinct parents and exactly three nonnull generated positions.
# Exercise 5: Reconcile child counts and nullable measures. Inputs/task: Aggregate the outer relation to parent_id, array_state, child_count, known_qty_count, total_qty. Count positions for children and preserve SUM NULL when there are no known quantities. Expected: Parent 10:(2,2,5);20:(0,0, NULL);30:(0,0, NULL);40:(1,0, NULL). Empty and unknown collection states remain visible. Verify: Assert each parent count tuple and that summed child_count is 3 while known_qty_count is 2.
# Exercise 6: Choose Cartesian or positional array semantics. Inputs/task: For one parent with SKUs[a, b] and channels[web, shop, api], return both independent exploded pairs and arrays_zip positional rows. Explain the relationship required for each interpretation. Expected: Independent generators produce 6 pairs;zip produces(a, web),(b, shop),(NULL, api), three rows. Verify: Assert the complete Cartesian pair set and all three ordered zipped rows including the paddedNULL.
