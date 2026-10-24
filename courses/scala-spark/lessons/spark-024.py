from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType


def canonical_rows(frame):
    return sorted(tuple(r) for r in frame.collect())
def partition_loads(frame, keys):
    return sorted(tuple(r) for r in frame.repartition(8,*keys).select(F.spark_partition_id().alias("pid")).groupBy("pid").count().collect())

def key_frequencies(facts):
    raise NotImplementedError("Complete key_frequencies")

def baseline_join(facts, dimension):
    raise NotImplementedError("Complete baseline_join")

def adaptive_join(facts, dimension):
    raise NotImplementedError("Complete adaptive_join")

def salt_facts(facts):
    raise NotImplementedError("Complete salt_facts")

def expand_dimension(dimension):
    raise NotImplementedError("Complete expand_dimension")

def salted_join(facts, dimension):
    raise NotImplementedError("Complete salted_join")

def main():

    spark = (SparkSession.builder.appName("ds60-spark-024").master("local[2]")
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
        spark.conf.set("spark.sql.autoBroadcastJoinThreshold","-1")
        spark.conf.set("spark.sql.adaptive.autoBroadcastJoinThreshold","-1")
        spark.conf.set("spark.sql.join.preferSortMergeJoin","true")
        spark.conf.set("spark.sql.shuffle.partitions","4")
        facts = spark.range(0,10000,1,4).withColumnRenamed("id","fact_id").withColumn("key",F.when(F.col("fact_id")<9000,0).otherwise((F.col("fact_id")-9000)%10+1)).withColumn("amount",F.lit(1).cast("long"))
        dimension = spark.range(0,11,1,2).withColumnRenamed("id","key").withColumn("factor",F.col("key")+1)
        hot = facts.filter(F.col("key")==0).count()
        assert hot == 9000 and hot/10000 == 0.9
        print("Observed hot-key fraction=",hot/10000)
        expected_weighted = 9000 + 100*sum(range(2,12))
        assert expected_weighted == 15500
        print("Weighted-total conservation oracle=",expected_weighted)
        print("spark-024: worked examples passed; six task implementations remain")
    finally:
        try:
            pass
        finally:
            spark.stop()

if __name__ == "__main__":
    main()

# Exercise 1: Measure the key-frequency imbalance. Inputs/task: Return ordered(key, n) counts for the fact relation. Derive total population and the hot-key fraction from this ledger. Expected: Key 0 has 9000;keys 1..10 each 100. Total 10000 and hot fraction 0.9. Verify: Assert all 11 ledger rows and the exact population/fraction.
# Exercise 2: Establish a baseline join with exact identity conservation. Inputs/task: Build an inner join withAQE disabled and broadcasting thresholds disabled, returning fact_id, key, amount, factor. Materialize the bounded result and compare every tuple with the generation formula. Expected: 10000 unique fact identities, amount total 10000 and weighted total 15500. The baseline plan contains a join and is printed. Verify: Assert all 10000 literal formula tuples and both totals before examining any optimization.
# Exercise 3: Observe an adaptive plan before and after execution. Inputs/task: Build a freshAQE-enabled join with skew handling enabled, coalescing disabled, skew factor 2, threshold 1024 bytes and advisory size 16384 bytes. Capture the initial plan, materialize the same DataFrame and capture the final plan. Expected: Initial/final text identifies AdaptiveSparkPlan;after materialization isFinalPlan=true. Every result tuple matches the baseline. Actual skew splitting is reported only if visible. Verify: Assert adaptive finalization and full row parity;print both plans and the small demonstration thresholds.
# Exercise 4: Split the hot logical key with a deterministic helper. Inputs/task: Add salt=fact_id modulo 4 only for key 0 and salt 0 otherwise. WithAQE disabled, compare eight-partition row-load ledgers by key and by(key, salt). Expected: Hot salt buckets 0..3 each have 2250 rows;cold facts all have salt 0. Both physical ledgers reconcile to 10000, and the unsalted maximum is at least 9000. Verify: Assert all four hot bucket counts and both reconciled ledgers;print actual salted loads without inventing perfect hash balance.
# Exercise 5: Replicate only the matching small-side hot row. Inputs/task: Expand dimension key 0 to salts 0,1,2,3 and every other dimension key to salt 0. Retain factor and verify uniqueness on the composite key. Expected: 14 dimension rows, with four key 0 variants and ten cold rows. Every(key, salt) pair is unique. Verify: Assert row count 14, distinct composite keys 14 and exact hot/cold salt populations.
# Exercise 6: Remove the physical helper and reconcile the business relation. Inputs/task: Join salted facts to the expanded dimension on key and salt, then project only fact_id, key, amount, factor. Compare the complete result with baseline and adaptive variants. Expected: All 10000 fact tuples remain exactly equal, with amount 10000 and weighted total 15500. Salt is absent from the final schema. Verify: Assert exact canonical bag equality and final column names;report the salted plan and row-load evidence separately from any speed claim.
