from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    LongType,
    IntegerType,
    StringType,
    DoubleType,
    BooleanType,
    ArrayType,
    MapType,
    TimestampType,
    DecimalType,
)


def run_grouped(frame, group):
    sc = frame.sparkSession.sparkContext
    sc.setJobGroup(group, "Bounded shuffle evidence", interruptOnCancel=True)
    try:
        return sorted((r[0], r[1]) for r in frame.collect())
    finally:
        sc.setLocalProperty("spark.jobGroup.id", None)
        sc.setLocalProperty("spark.job.description", None)
        sc.setLocalProperty("spark.job.interruptOnCancel", None)


def source_metrics(source):
    return tuple(source.agg(F.count(F.lit(1)), F.countDistinct("key"), F.sum("id")).first())


def build_grouped(source, partitions):
    if isinstance(partitions, bool) or not isinstance(partitions, int) or not 1 <= partitions <= 16:
        raise ValueError("Partition budget is1..16")
    source.sparkSession.conf.set("spark.sql.shuffle.partitions", str(partitions))
    return source.groupBy("key").agg(F.count(F.lit(1)).alias("n"))


def exchange_metrics(frame):
    result = []
    pending = [frame._jdf.queryExecution().executedPlan()]
    while pending:
        node = pending.pop()
        if node.nodeName() == "Exchange":
            metrics = {}
            iterator = node.metrics().iterator()
            while iterator.hasNext():
                entry = iterator.next()
                metrics[str(entry._1())] = int(entry._2().value())
            result.append(metrics)
        children = node.children().iterator()
        while children.hasNext():
            pending.append(children.next())
    return result


def stage_evidence(spark, group):
    tracker = spark.sparkContext.statusTracker()
    stages = set()
    for job_id in tracker.getJobIdsForGroup(group):
        job = tracker.getJobInfo(job_id)
        if job is not None:
            stages.update(job.stageIds)
    result = []
    for stage_id in sorted(stages):
        info = tracker.getStageInfo(stage_id)
        if info is not None:
            result.append((stage_id, info.numTasks, info.numCompletedTasks, info.numFailedTasks))
    return result


def compare_results(left, right):
    if left != right or len(left) != 1000 or sum(n for _, n in left) != 20000:
        raise ValueError("Grouped result contract changed")


def work_model(reducers):
    if isinstance(reducers, bool) or not isinstance(reducers, int) or reducers <= 0:
        raise ValueError("Positive reducer count required")
    return 20000 // 4, 4 * 1000, 1000 / reducers


def main():

    spark = (
        SparkSession.builder.appName("ds60-spark-022")
        .master("local[2]")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.sql.adaptive.enabled", "false")
        .config("spark.sql.ansi.enabled", "true")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    try:
        assert spark.sparkContext.master == "local[2]"
        spark.sparkContext.setLogLevel("ERROR")
        source = spark.range(0, 20000, 1, 4).withColumn("key", F.col("id") % 1000)
        original_shuffle = spark.conf.get("spark.sql.shuffle.partitions")
        # Exercise 1: Establish the high-cardinality fixture oracle
        assert source_metrics(source) == (20000, 1000, 199990000)
        assert 20000 * 19999 // 2 == 199990000
        # Exercise 2: Build and execute a controlled grouped query
        two = build_grouped(source, 2)
        two_rows = run_grouped(two, "ds60-spark-022-p2")
        expected = [(key, 20) for key in range(1000)]
        assert two_rows == expected and sum(n for _, n in two_rows) == 20000
        assert "Exchange" in two._jdf.queryExecution().executedPlan().toString()
        try:
            build_grouped(source, 0)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid partition budget accepted")
        # Exercise 3: Read actual exchange metrics after the action
        two_exchange = exchange_metrics(two)
        assert (
            len(two_exchange) == 1
            and two_exchange[0]["numPartitions"] == 2
            and two_exchange[0]["dataSize"] > 0
        )
        print("p2_exchange=", two_exchange)
        # Exercise 4: Attach stage and task evidence to the named action
        two_stages = stage_evidence(spark, "ds60-spark-022-p2")
        assert (
            two_stages
            and any(row[1] == 2 for row in two_stages)
            and all(all(n >= 0 for n in row[1:]) for row in two_stages)
        )
        print("p2_stages=", two_stages)
        # Exercise 5: Change reduce parallelism while preserving the complete result
        five = build_grouped(source, 5)
        five_rows = run_grouped(five, "ds60-spark-022-p5")
        compare_results(two_rows, five_rows)
        assert five_rows == expected
        five_exchange = exchange_metrics(five)
        five_stages = stage_evidence(spark, "ds60-spark-022-p5")
        assert (
            len(five_exchange) == 1
            and five_exchange[0]["numPartitions"] == 5
            and five_exchange[0]["dataSize"] > 0
        )
        assert any(row[1] == 5 for row in five_stages)
        print("p5_exchange=", five_exchange, "p5_stages=", five_stages)
        # Exercise 6: Separate a workload model from measured evidence
        assert work_model(2) == (5000, 4000, 500) and work_model(5) == (5000, 4000, 200)
        print(
            "version=",
            spark.version,
            "aqe=",
            spark.conf.get("spark.sql.adaptive.enabled"),
            "master=",
            spark.sparkContext.master,
            "model_only=",
            [work_model(2), work_model(5)],
        )
        spark.conf.set("spark.sql.shuffle.partitions", original_shuffle)
        print("spark-022: six PySpark reference contracts passed; Spark=" + spark.version)
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
