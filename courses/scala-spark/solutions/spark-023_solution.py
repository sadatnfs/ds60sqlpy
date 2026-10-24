from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType


def logical_metrics(frame):
    return tuple(frame.agg(F.count(F.lit(1)),F.countDistinct("fact_id"),F.sum("amount"),F.sum(F.col("amount")*F.col("factor"))).first())
def join_plan(frame):
    return frame._jdf.queryExecution().executedPlan().toString()

def estimated_bytes(frame):
    return int(str(frame._jdf.queryExecution().optimizedPlan().stats().sizeInBytes()))

def ordinary_join(facts, dimension):
    return facts.join(dimension,on="key",how="inner").select("fact_id","key","amount","factor")

def without_automatic_broadcast(facts, dimension):
    facts.sparkSession.conf.set("spark.sql.autoBroadcastJoinThreshold","-1")
    return ordinary_join(facts,dimension)

def hinted_join(facts, dimension):
    return facts.join(F.broadcast(dimension),on="key",how="inner").select("fact_id","key","amount","factor")

def unsupported_hint(facts, dimension):
    return facts.join(F.broadcast(dimension),on="key",how="full_outer").select("fact_id","key","amount","factor")

def bounded_broadcast(dimension):
    if dimension.isStreaming:
        raise ValueError("Streaming input is not a bounded build table")
    rows = dimension.limit(101).count()
    if rows > 100:
        raise ValueError("Broadcast row budget exceeded")
    if dimension.select("key").distinct().count() != rows or dimension.filter(F.col("key").isNull()).count():
        raise ValueError("Build keys must be unique and known")
    if not 0 < estimated_bytes(dimension) <= 1048576:
        raise ValueError("Broadcast estimate outside declared budget")
    return F.broadcast(dimension)

def main():

    spark = (SparkSession.builder.appName("ds60-spark-023").master("local[2]")
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
        facts = spark.range(0,20000,1,4).withColumnRenamed("id","fact_id").withColumn("key",F.col("fact_id")%20).withColumn("amount",F.col("fact_id")%7+1)
        dimension = spark.range(0,20,1,2).withColumnRenamed("id","key").withColumn("factor",F.col("key")+1)
        spark.conf.set("spark.sql.autoBroadcastJoinThreshold","10485760")
        spark.conf.set("spark.sql.join.preferSortMergeJoin","true")
        # Exercise 1: Inspect statistics and the automatic threshold separately
        estimate = estimated_bytes(dimension)
        threshold = int(spark.conf.get("spark.sql.autoBroadcastJoinThreshold"))
        assert 0 < estimate < threshold == 10485760
        print("dimension_estimated_bytes=",estimate,"threshold=",threshold,"actual_rows=",dimension.count(),"version=",spark.version)
        # Exercise 2: Observe the automatic plan and verify its relational output
        automatic = ordinary_join(facts,dimension)
        assert logical_metrics(automatic) == (20000,20000,79997,839916)
        automatic_plan = join_plan(automatic)
        assert "Join" in automatic_plan
        print("automatic_threshold=",spark.conf.get("spark.sql.autoBroadcastJoinThreshold"),"plan=",automatic_plan)
        # Exercise 3: Disable automatic broadcasting for a fresh comparison
        shuffled = without_automatic_broadcast(facts,dimension)
        assert logical_metrics(shuffled) == (20000,20000,79997,839916)
        assert "BroadcastHashJoin" not in join_plan(shuffled) and spark.conf.get("spark.sql.adaptive.enabled") == "false"
        print("disabled_threshold=-1;plan=",join_plan(shuffled))
        # Exercise 4: Request an eligible explicit broadcast and reconcile bags
        hinted = hinted_join(facts,dimension)
        assert logical_metrics(hinted) == (20000,20000,79997,839916)
        hinted_plan = join_plan(hinted)
        assert "BroadcastHashJoin" in hinted_plan and "BroadcastExchange" in hinted_plan
        assert hinted.exceptAll(shuffled).count() == 0 and shuffled.exceptAll(hinted).count() == 0
        print("explicit_broadcast_plan=",hinted_plan)
        # Exercise 5: Observe an unsupported hint without changing the business result
        full = unsupported_hint(facts,dimension)
        assert logical_metrics(full) == (20000,20000,79997,839916)
        assert "BroadcastHashJoin" not in join_plan(full)
        print("full_outer_observed_plan=",join_plan(full))
        # Exercise 6: Gate a broadcast candidate on explicit bounded evidence
        assert logical_metrics(ordinary_join(facts,bounded_broadcast(dimension))) == (20000,20000,79997,839916)
        for candidate in [dimension.unionByName(dimension.filter(F.col("key")==0)),spark.range(101).withColumnRenamed("id","key").withColumn("factor",F.lit(1))]:
            try:
                bounded_broadcast(candidate)
            except ValueError:
                pass
            else:
                raise AssertionError("Invalid broadcast candidate accepted")
        print("spark-023: six PySpark reference contracts passed; Spark=" + spark.version)
    finally:
        try:
            pass
        finally:
            spark.stop()

if __name__ == "__main__":
    main()

# Exercise 1: Inspect statistics and the automatic threshold separately. Inputs/task: Return the optimized-plan size estimate for dimension as a nonnegative integer, and record the configured automatic broadcast threshold and actual dimension row count. Expected: A positive finite estimate below 10485760 bytes, threshold 10485760 and actual row count 20. The estimate is not a peak-memory measurement. Verify: Assert the finite estimate range and print estimate, threshold, rows andSpark version as separate fields.
# Exercise 2: Observe the automatic plan and verify its relational output. Inputs/task: Build an ordinary inner equality join on key, projecting fact_id, key, amount, factor. Execute logical metrics and record the physical plan chosen with the declared threshold. Expected: Metrics(20000,20000,79997,839916). The observed plan identifies a join strategy and is printed with current threshold. Verify: Assert all metrics and a join operator marker. Report the observed automatic strategy without treating a default as a universal guarantee.
# Exercise 3: Disable automatic broadcasting for a fresh comparison. Inputs/task: Set automatic broadcast threshold to-1, build a fresh ordinary join and record its plan withAQE disabled. Keep the logical result contract. Expected: Same metrics as automatic. No BroadcastHashJoin in this fresh query underAQEfalse and threshold-1. Verify: Assert all four metrics, the disabled setting and observed absence of BroadcastHashJoin.
# Exercise 4: Request an eligible explicit broadcast and reconcile bags. Inputs/task: Apply broadcast to the dimension for an inner equality join while automatic threshold remains-1. Project the same columns and compare duplicate-sensitive output with the ordinary join in both directions. Expected: BroadcastHashJoin and BroadcastExchange appear. Both exceptAll differences are empty and logical metrics remain exact. Verify: Assert the two operator markers, all metrics and both bag differences.
# Exercise 5: Observe an unsupported hint without changing the business result. Inputs/task: Request a broadcast dimension in a full outer equality join and inspect the chosen plan. Explain why this fixture still has the same output rows as the inner join. Expected: No BroadcastHashJoin for this unsupported full-outer hash strategy. Metrics remain(20000,20000,79997,839916) because both key domains are fully covered. Verify: Assert the observed absence of BroadcastHashJoin and exact output metrics;report a hint warning if emitted rather than hiding it.
# Exercise 6: Gate a broadcast candidate on explicit bounded evidence. Inputs/task: Reject streaming inputs, more than 100 rows, missing/duplicate keys, or an estimated size outside(0,1MiB]. Return the bounded dimension with a broadcast hint only after those checks. Expected: The 20-row dimension passes;the same dimension with a duplicate key and a101-row candidate fail. No unbounded input is collected or materialized by the gate. Verify: Assert accepted logical join metrics and explicit rejection for duplicate and row-budget cases.
