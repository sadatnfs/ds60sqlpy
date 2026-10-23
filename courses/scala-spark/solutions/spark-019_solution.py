from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType
from pyspark.sql import Window



def validate_candidates(events):
    total,unique = events.agg(F.count(F.lit(1)),F.countDistinct("event_id")).first()
    if total != unique or events.filter((F.col("event_id")<=0)|F.col("entity").isNull()).count():
        raise ValueError("Known positive unique event IDs and known entity keys required")

def rank_candidates(events):
    order = Window.partitionBy("entity").orderBy(F.col("event_time").desc_nulls_last(),F.col("event_id").desc())
    return events.withColumn("candidate_rank",F.row_number().over(order))

def winners(events):
    validate_candidates(events)
    return rank_candidates(events).filter(F.col("candidate_rank")==1).drop("candidate_rank")

def top_time_candidates(events):
    order = Window.partitionBy("entity").orderBy(F.col("event_time").desc_nulls_last())
    return events.withColumn("time_rank",F.dense_rank().over(order)).filter(F.col("time_rank")==1).drop("time_rank")

def running_totals(events):
    rows_frame = Window.partitionBy("entity").orderBy(F.col("event_time").asc_nulls_last(),"event_id").rowsBetween(Window.unboundedPreceding,Window.currentRow)
    peer_frame = Window.partitionBy("entity").orderBy(F.col("event_time").asc_nulls_last()).rangeBetween(Window.unboundedPreceding,Window.currentRow)
    return events.withColumn("rows_total",F.sum("amount").over(rows_frame)).withColumn("peer_total",F.sum("amount").over(peer_frame)).select("event_id","rows_total","peer_total")

def previous_evidence(events):
    order = Window.partitionBy("entity").orderBy(F.col("event_time").asc_nulls_last(),"event_id")
    return events.withColumn("previous_id",F.lag("event_id",1).over(order)).withColumn("previous_time",F.lag("event_time",1).over(order)).withColumn("gap_seconds",F.unix_timestamp("event_time")-F.unix_timestamp("previous_time")).select("event_id","previous_id","gap_seconds")

def main():
    spark = (SparkSession.builder.appName("ds60-spark-019").master("local[2]")
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
        schema = StructType([StructField("event_id",LongType(),False),StructField("entity",StringType(),False),StructField("time_text",StringType(),True),StructField("amount",LongType(),False)])
        events = spark.createDataFrame([(1,"A","2024-01-01 00:00:00",10),(2,"A","2024-01-01 00:01:00",20),(3,"A","2024-01-01 00:01:00",30),(4,"B","2024-01-01 00:00:00",40),(5,"B","2024-01-01 00:02:00",50),(6,"B","2024-01-01 00:02:00",60),(7,"C",None,70),(8,"C","2024-01-01 00:01:00",80)],schema=schema).withColumn("event_time",F.to_timestamp("time_text"))
        # Exercise 1: Validate identities before defining a winner
        validate_candidates(events)
        try:
            validate_candidates(events.unionByName(events.filter(F.col("event_id")==1)))
        except ValueError:
            pass
        else:
            raise AssertionError("Duplicate event identity was accepted")
        # Exercise 2: Rank all candidates with an explicit NULL rule
        ranked = rank_candidates(events)
        assert [tuple(r) for r in ranked.select("event_id","candidate_rank").orderBy("event_id").collect()] == [(1,3),(2,2),(3,1),(4,3),(5,2),(6,1),(7,2),(8,1)]
        # Exercise 3: Select stable winners across physical layouts
        for partitions in [1,3,4]:
            assert [r[0] for r in winners(events.repartition(partitions)).select("event_id").orderBy("event_id").collect()] == [3,6,8]
        events.createOrReplaceTempView("ds60_spark_019_events")
        assert [r[0] for r in spark.sql("SELECT event_id FROM (SELECT *,row_number() OVER(PARTITION BY entity ORDER BY event_time DESC NULLS LAST,event_id DESC) AS rn FROM ds60_spark_019_events) WHERE rn=1 ORDER BY event_id").collect()] == [3,6,8]
        # Exercise 4: Prove why timestamp-only ordering is incomplete
        top = top_time_candidates(events)
        assert [r[0] for r in top.select("event_id").orderBy("event_id").collect()] == [2,3,5,6,8]
        assert [r[0] for r in top.groupBy("entity").count().filter(F.col("count")>1).select("entity").orderBy("entity").collect()] == ["A","B"]
        # Exercise 5: Distinguish occurrence totals from time-peer totals
        assert [tuple(r) for r in running_totals(events).orderBy("event_id").collect()] == [(1,10,10),(2,30,60),(3,60,60),(4,40,40),(5,90,150),(6,150,150),(7,150,150),(8,80,80)]
        # Exercise 6: Interpret lag without claiming strict temporal availability
        assert [tuple(r) for r in previous_evidence(events).orderBy("event_id").collect()] == [(1,None,None),(2,1,60),(3,2,0),(4,None,None),(5,4,120),(6,5,0),(7,8,None),(8,None,None)]
        print("spark-019: six PySpark reference contracts passed; Spark=" + spark.version)
    finally:
        spark.stop()

if __name__ == "__main__":
    main()

# Exercise 1: Validate identities before defining a winner. Inputs/task: Reject an input unless event_id is known, positive and unique and entity is known. Allow missing event_time under the declared last-priority policy. Return Unit/None on success. Expected: The eight-event fixture passes;adding another copy of event 1 fails. Missing-time event 7 is allowed. Verify: Assert normal acceptance and explicit rejection after unioning a duplicate identity.
# Exercise 2: Rank all candidates with an explicit NULL rule. Inputs/task: Add candidate_rank using row_number per entity, descending event_time with NULL last, then descending event_id. Keep all eight rows. Expected: Ranks byevent_id are 1:3,2:2,3:1,4:3,5:2,6:1,7:2,8:1. Verify: Assert the full ID/rank table and input count 8.
# Exercise 3: Select stable winners across physical layouts. Inputs/task: Validate candidates, rank them and retain rank 1. Compare winner IDs after repartitioning to 1,3 and 4 partitions, then compare an equivalentSQL row_number query. Expected: Every case yields event IDs[3,6,8], one per entity. SQL returns the same literal winners. Verify: Assert exact winners in every layout and SQL, not just equal row counts.
# Exercise 4: Prove why timestamp-only ordering is incomplete. Inputs/task: Use dense_rank ordered only by descending event_time with NULL last, returning all rank 1 candidates. Report the candidate IDs rather than choosing an arbitrary winner. Expected: Top-time candidates[2,3,5,6,8]. EntitiesA andB each have two admissible candidates under the incomplete rule. Verify: Assert the five candidate identities and the two ambiguous entity keys. Do not require unstable executions to change output.
# Exercise 5: Distinguish occurrence totals from time-peer totals. Inputs/task: Return event_id, rows_total, peer_total. ROWS uses ascending time NULL last then ID and an unbounded-preceding/current-row frame. RANGE uses only ascending time NULL last over the same cumulative boundary. Expected: By ID:1(10,10),2(30,60),3(60,60),4(40,40),5(90,150),6(150,150),7(150,150),8(80,80). Verify: Assert all eight tuples, especially tied IDs 2/3 and the missing-time event 7.
# Exercise 6: Interpret lag without claiming strict temporal availability. Inputs/task: Using ascending time NULL last then event_id, return event_id, previous_id, gap_seconds. Lag the event identity and time, then subtract epoch seconds. Expected: 1(NULL, NULL),2(1,60),3(2,0),4(NULL, NULL),5(4,120),6(5,0),7(8, NULL),8(NULL, NULL). Verify: Assert the complete identity/gap rows and explain zero gaps and the known previous ID with unknown duration.
