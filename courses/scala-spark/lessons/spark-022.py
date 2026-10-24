from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType


def run_grouped(frame, group):
    sc = frame.sparkSession.sparkContext
    sc.setJobGroup(group,"Bounded shuffle evidence",interruptOnCancel=True)
    try:
        return sorted((r[0],r[1]) for r in frame.collect())
    finally:
        sc.setLocalProperty("spark.jobGroup.id",None)
        sc.setLocalProperty("spark.job.description",None)
        sc.setLocalProperty("spark.job.interruptOnCancel",None)

def source_metrics(source):
    raise NotImplementedError("Complete source_metrics")

def build_grouped(source, partitions):
    raise NotImplementedError("Complete build_grouped")

def exchange_metrics(frame):
    raise NotImplementedError("Complete exchange_metrics")

def stage_evidence(spark, group):
    raise NotImplementedError("Complete stage_evidence")

def compare_results(left, right):
    raise NotImplementedError("Complete compare_results")

def work_model(reducers):
    raise NotImplementedError("Complete work_model")

def main():

    spark = (SparkSession.builder.appName("ds60-spark-022").master("local[2]")
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
        source = spark.range(0,20000,1,4).withColumn("key",F.col("id")%1000)
        original_shuffle = spark.conf.get("spark.sql.shuffle.partitions")
        assert source.count() == 20000 and source.rdd.getNumPartitions() == 4
        assert source.select("key").distinct().count() == 1000
        print("Input:20000 rows,1000 keys,4 partitions,local[2]")
        partial_upper = 4*1000
        assert partial_upper == 4000 and partial_upper < 20000
        print("Local partial aggregation can reduce occurrences before redistribution;this is a model")
        print("spark-022: worked examples passed; six task implementations remain")
    finally:
        try:
            pass
        finally:
            spark.stop()

if __name__ == "__main__":
    main()

# Exercise 1: Establish the high-cardinality fixture oracle. Inputs/task: Compute input row count, distinct key count and total id sum. Confirm the key formula supports exactly 20 occurrences per key. Expected: Metrics(20000,1000,199990000);keys 0..999 each occur 20 times by construction. Verify: Assert the aggregate tuple and independent arithmetic sum 0+...+19999.
# Exercise 2: Build and execute a controlled grouped query. Inputs/task: Require 1..16 shuffle partitions, set that configuration in the owned session and return key, n from groupBy/count. Execute the two-partition case under the supplied unique job group. Expected: Sorted output[(0,20),...,(999,20)], with total counts 20000 and an Exchange in the executed plan. Verify: Assert every key/count pair and the plan Exchange marker. Reject an out-of-budget partition request.
# Exercise 3: Read actual exchange metrics after the action. Inputs/task: Traverse the executed classic Spark plan, collecting each Exchange metric map. Use the version-pinned internal diagnostic API only for evidence after collection. Expected: One exchange map for this aggregate, with numPartitions 2 and dataSize>0. Record other available metrics without inventing units or missing values. Verify: Assert one observed exchange, its partition metric and positive serialized data size;print the complete available map.
# Exercise 4: Attach stage and task evidence to the named action. Inputs/task: Use the status tracker to find jobs for a supplied group and their retained stages. Return stage_id, num_tasks, completed_tasks, failed_tasks ordered by stage identity. Expected: Nonempty retained stage evidence for the p2 action, including a stage with 2 tasks. All task counters are nonnegative. Verify: Assert nonempty stage rows and a two-task stage, and print the actual counters rather than asserting a universal stage count.
# Exercise 5: Change reduce parallelism while preserving the complete result. Inputs/task: Run the same source aggregation with 5 shuffle partitions under its own job group. Compare all 1000 group tuples, then report exchange and stage evidence tied to p5. Expected: Exact output matches p2 and the literal oracle. Exchange numPartitions 5 and positive dataSize;retained task evidence includes a five-task stage. Verify: Assert result parity before inspecting the 5-partition metric and corresponding action-group stages.
# Exercise 6: Separate a workload model from measured evidence. Inputs/task: For the declared 20000-row,1000-key, four-mapper fixture, return source_rows_per_mapper, partial_group_upper and average_output_groups_per_reducer for a positive reducer count. Label them as arithmetic estimates and print version/configuration beside the actual metrics. Expected: For reducers 2:5000,4000,500. For reducers 5:5000,4000,200. These values do not assert actual balanced hash buckets or network bytes. Verify: Assert the two model tuples and print Spark 4.0.1, AQEfalse, local[2] with the distinct p2/p5 observations.
