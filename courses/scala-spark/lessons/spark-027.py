from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType
from pyspark import StorageLevel



def transform(source):
    raise NotImplementedError("Complete transform")

def schema_contract(frame):
    raise NotImplementedError("Complete schema_contract")

def assert_same_bag(actual, expected):
    raise NotImplementedError("Complete assert_same_bag")

def cached_summary(frame):
    raise NotImplementedError("Complete cached_summary")

def failing_reuse(frame):
    raise NotImplementedError("Complete failing_reuse")

def difference_counts(actual, expected):
    raise NotImplementedError("Complete difference_counts")

def main():

    spark = (SparkSession.builder.appName("ds60-spark-027").master("local[2]")
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
        schema = StructType([StructField("entity_id",LongType(),False),StructField("segment",StringType(),True),StructField("amount",LongType(),True)])
        source = spark.createDataFrame([(1,"a",10),(1,"a",10),(2,"a",None),(3,"b",0),(4,"b",20),(4,"b",20),(5,None,5),(6,"c",-5)],schema=schema)
        golden_schema = StructType([StructField("entity_id",LongType(),False),StructField("segment",StringType(),True),StructField("doubled",LongType(),True)])
        golden = spark.createDataFrame([(1,"a",20),(1,"a",20),(2,"a",None),(3,"b",0),(4,"b",40),(4,"b",40),(5,None,10)],schema=golden_schema)
        assert source.count() == 8 and source.select("entity_id","segment","amount").distinct().count() == 6
        assert golden.count() == 7 and golden.agg(F.sum("doubled")).first()[0] == 130
        print("Golden bag contains duplicates and unknown values deliberately")
        numeric = spark.sql("SELECT CAST(1 AS BIGINT) AS entity_id")
        textual = spark.sql("SELECT CAST('1' AS STRING) AS entity_id")
        assert numeric.schema["entity_id"].dataType != textual.schema["entity_id"].dataType
        print("Identical displayed digits can have different field types")
        print("spark-027: worked examples passed; six task implementations remain")
    finally:
        try:
            pass
        finally:
            spark.stop()

if __name__ == "__main__":
    main()

# Exercise 1: Transform without collapsing occurrences or unknowns. Inputs/task: Keep rows whose amount is nonnegative orNULL, then return entity_id, segment, doubled=amount*2. Preserve duplicate occurrences and unknown values. Expected: Seven rows, known total 130 and oneNULL doubled value. The negative entity 6 row is excluded. Verify: Assert population, total and unknown count, then compare with the literal golden relation in later tasks.
# Exercise 2: Define an ordered field/type contract. Inputs/task: Return ordered(name, simple_type) pairs from the result schema. Compare with entity_id bigint, segment string, doubled bigint. Expected: Exactly those three fields in that order. Casting entity_id to string changes the contract even when printed values look alike. Verify: Assert the correct type list and a different list after the deliberate cast.
# Exercise 3: Compare schemas before duplicate-sensitive values. Inputs/task: Reject a schema mismatch first, then require both exceptAll differences to be empty. Accept a repartitioned correct result and reject the deliberate string-ID result. Expected: Correct result passes in different physical layouts;string-ID candidate fails with a named schema contract error. Verify: Assert acceptance for golden/repartitioned values and explicit schema rejection before a coercing bag comparison.
# Exercise 4: Register, materialize, reuse and release one cached relation. Inputs/task: Persist the supplied transformed relation with MEMORY_AND_DISK, materialize via count, reuse for a total and inspect a filtered consumer plan. Unpersist with blocking cleanup in finally. Expected: Count 7, total 130, an InMemoryTableScan reuse marker, and no registered storage level after return. Verify: Assert result values, cache-scan evidence and post-returnStorageLevel.NONE. Do not use a timing threshold.
# Exercise 5: Release persistence when a consumer fails. Inputs/task: Persist and materialize the relation, then raise an injected failure before a later consumer. Unpersist in finally and verify the original error reaches the caller. Expected: The injected_after_materialize error is observed and storage level isNONE afterward. Correct uncached output still passes the golden oracle. Verify: Assert the named failure, post-failure release and full golden equality on a subsequent computation.
# Exercise 6: Demonstrate why set equality misses duplicate loss. Inputs/task: Return directional exceptAll row counts after schema validation. Compare transformed.distinct with golden and require the golden validator to reject it. Expected: Distinct has 5 rows;unexpected occurrences 0 and missing expected occurrences 2. The bag validator raises a named bag contract mismatch. Verify: Assert(0,2), count 5 and the explicit negative-control rejection.
