from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType
from pathlib import Path
from datetime import datetime
import tempfile
import shutil
import os
import uuid
from pyspark.errors import AnalysisException

impression_schema = StructType([StructField("impression_id",StringType(),True),StructField("key",StringType(),True),StructField("impression_time",TimestampType(),True)])
click_schema = StructType([StructField("click_id",StringType(),True),StructField("key",StringType(),True),StructField("click_time",TimestampType(),True)])
result_schema = StructType([StructField("impression_id",StringType(),True),StructField("click_id",StringType(),True),StructField("impression_time",TimestampType(),True),StructField("click_time",TimestampType(),True)])
def publish(root,side,index,lines):
    if side not in {"impressions","clicks"}: raise ValueError("Unknown input side")
    target = root/side/f"batch-{index}.json"
    if target.exists(): raise ValueError("New input filename required")
    staged = root/"staging"/(uuid.uuid4().hex+".tmp")
    try:
        with staged.open("x",encoding="utf-8") as handle: handle.write("\n".join(lines)+"\n")
        os.replace(staged,target)
    finally: staged.unlink(missing_ok=True)

def inputs(spark, root):
    impressions = spark.readStream.schema(impression_schema).option("maxFilesPerTrigger",1).option("mode","FAILFAST").json(str(root/"impressions")).withWatermark("impression_time","5 minutes")
    clicks = spark.readStream.schema(click_schema).option("maxFilesPerTrigger",1).option("mode","FAILFAST").json(str(root/"clicks")).withWatermark("click_time","5 minutes")
    return impressions,clicks

def bounded_join(impressions, clicks, kind):
    if kind not in {"inner","left_outer"}: raise ValueError("Unsupported join kind")
    i = impressions.alias("i");c = clicks.alias("c")
    condition = (F.col("i.key")==F.col("c.key"))&(F.col("c.click_time")>=F.col("i.impression_time"))&(F.col("c.click_time")<F.col("i.impression_time")+F.expr("INTERVAL 10 MINUTES"))
    return i.join(c,condition,kind).select("i.impression_id","c.click_id","i.impression_time","c.click_time")

def run_join(spark, root, kind):
    left,right = inputs(spark,root)
    query = bounded_join(left,right,kind).writeStream.format("parquet").outputMode("append").option("checkpointLocation",str(root/(kind+"-checkpoint"))).trigger(availableNow=True).start(str(root/(kind+"-output")))
    try:
        if not query.awaitTermination(30): raise TimeoutError("Finite join deadline exceeded")
        if query.exception() is not None or query.isActive: raise RuntimeError("Join failed")
        return list(query.recentProgress)
    finally: query.stop()

def pairs(spark, root, kind):
    frame = spark.read.schema(result_schema).parquet(str(root/(kind+"-output")))
    return [tuple(r) for r in frame.select("impression_id","click_id").orderBy(F.col("impression_id"),F.col("click_id").asc_nulls_last()).collect()]

def progress_evidence(progress):
    operators = [operator for p in progress for operator in p.get("stateOperators",[])]
    if not operators or any("numRowsRemoved" not in operator for operator in operators): raise ValueError("Missing join state evidence")
    marks = [p["eventTime"]["watermark"] for p in progress if p.get("eventTime",{}).get("watermark") is not None]
    return sum(p["numInputRows"] for p in progress),marks,sum(operator["numRowsRemoved"] for operator in operators)

def reject_unbounded_outer(spark, root):
    left,right = inputs(spark,root)
    invalid = left.alias("i").join(right.alias("c"),F.col("i.key")==F.col("c.key"),"left_outer").select("i.impression_id","c.click_id")
    query = None; rejected = False
    try:
        query = invalid.writeStream.format("parquet").outputMode("append").option("checkpointLocation",str(root/"invalid-checkpoint")).trigger(availableNow=True).start(str(root/"invalid-output"))
        query.awaitTermination(30)
    except AnalysisException:
        rejected = True
    finally:
        if query is not None: query.stop()
    if not rejected: raise AssertionError("Unbounded outer join unexpectedly accepted")

def main():
    owned_root = None
    spark = (SparkSession.builder.appName("ds60-spark-034").master("local[2]")
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
        spark.conf.set("spark.sql.streaming.stopTimeout","10000")
        spark.conf.set("spark.sql.streaming.multipleWatermarkPolicy","min")
        owned_root = Path(tempfile.mkdtemp(prefix=".ds60-spark-034-",dir=".")).resolve()
        for name in ["impressions","clicks","staging"]: (owned_root/name).mkdir()
        impression_lines = ['{"impression_id":"i1","key":"A","impression_time":"2024-01-01T00:00:00Z"}','{"impression_id":"i2","key":"B","impression_time":"2024-01-01T00:00:00Z"}','{"impression_id":"i3","key":"C","impression_time":"2024-01-01T00:05:00Z"}']
        click_lines = ['{"click_id":"c1","key":"A","click_time":"2024-01-01T00:03:00Z"}','{"click_id":"c2","key":"C","click_time":"2024-01-01T00:10:00Z"}','{"click_id":"c3","key":"A","click_time":"2024-01-01T00:10:00Z"}','{"click_id":"c4","key":"Z","click_time":"2024-01-01T00:04:00Z"}']
        # Exercise 1: Declare both streaming schemas and watermark policies
        publish(owned_root,"impressions",0,impression_lines);publish(owned_root,"clicks",0,click_lines)
        sources = inputs(spark,owned_root)
        assert all(frame.isStreaming for frame in sources) and isinstance(sources[0].schema["impression_time"].dataType,TimestampType) and isinstance(sources[1].schema["click_time"].dataType,TimestampType)
        assert spark.conf.get("spark.sql.streaming.multipleWatermarkPolicy") == "min" and not spark.streams.active
        # Exercise 2: Express key equality and the exact time range
        planned = bounded_join(sources[0],sources[1],"inner")
        assert planned.isStreaming and planned.columns == ["impression_id","click_id","impression_time","click_time"]
        try:
            bounded_join(sources[0],sources[1],"cross")
        except ValueError:
            pass
        else:
            raise AssertionError("Unsupported join kind accepted")
        # Exercise 3: Run inner and outer queries with separate owned recovery state
        inner_first = run_join(spark,owned_root,"inner");outer_first = run_join(spark,owned_root,"left_outer")
        assert sum(p["numInputRows"] for p in inner_first) == 7 and sum(p["numInputRows"] for p in outer_first) == 7 and not spark.streams.active
        # Exercise 4: Distinguish immediate matches frompending unmatched impressions
        expected_matched = [("i1","c1"),("i3","c2")]
        assert pairs(spark,owned_root,"inner") == expected_matched and pairs(spark,owned_root,"left_outer") == expected_matched
        # Exercise 5: Advance both sides and observe delayed outer finalization
        publish(owned_root,"impressions",1,['{"impression_id":"__left_advance__","key":"__left__","impression_time":"2024-01-01T00:30:00Z"}'])
        publish(owned_root,"clicks",1,['{"click_id":"__right_advance__","key":"__right__","click_time":"2024-01-01T00:30:00Z"}'])
        inner_second = run_join(spark,owned_root,"inner");outer_second = run_join(spark,owned_root,"left_outer")
        assert pairs(spark,owned_root,"inner") == expected_matched
        assert pairs(spark,owned_root,"left_outer") == [("i1","c1"),("i2",None),("i3","c2")]
        progress = progress_evidence(outer_second)
        assert progress[0] == 2 and sum(p["numInputRows"] for p in inner_second) == 2 and progress[2] > 0
        assert any(datetime.fromisoformat(value.replace("Z","+00:00")) >= datetime.fromisoformat("2024-01-01T00:25:00+00:00") for value in progress[1])
        print("outer_finalization_progress=",progress)
        # Exercise 6: Reject an outer join without an event-time bound
        reject_unbounded_outer(spark,owned_root)
        assert not spark.streams.active and pairs(spark,owned_root,"left_outer") == [("i1","c1"),("i2",None),("i3","c2")]
        print("spark-034: six PySpark reference contracts passed; Spark=" + spark.version)
    finally:
        try:
            if spark.streams.active:
                raise RuntimeError("Query still active; preserve scratch")
            if owned_root is not None:
                shutil.rmtree(owned_root)
        finally:
            spark.stop()

if __name__ == "__main__":
    main()

# Exercise 1: Declare both streaming schemas and watermark policies. Inputs/task: Read the owned impression and click file directories with their explicit schemas, maxFilesPerTrigger 1 and five-minute watermarks on their respective event-time columns. Expected: Both relations are streaming;the minimum multiple-watermark policy isexplicit and no query runs merely fromconstruction. Verify: Assert both streaming flags, the declared timestamp fields and policymin before execution.
# Exercise 2: Express key equality and the exact time range. Inputs/task: Build either an inner orleft_outer join using key equality, click_time>=impression_time and click_time<impression_time+10minutes. Project impression_id, click_id and both timestamps. Expected: A streaming relation with the four declared columns. The condition can matchi 1/c1 and i 3/c2 butnot boundaryclickc 3. Verify: Assert output shape and reject an unsupported kind value;later exact pair checks validate both predicates.
# Exercise 3: Run inner and outer queries with separate owned recovery state. Inputs/task: Execute a named join kind with AvailableNow, Parquet append and its own checkpoint/output paths. Await at most 30 seconds and stop in finally. Run both kinds for the first input phase. Expected: Each query consumes 7 source rows across its two inputs and terminates. The two checkpoints are distinct. Verify: Assert input 7 for each query and inactive state after both bounded runs;do not combine their processing counts into 14 unique source events.
# Exercise 4: Distinguish immediate matches frompending unmatched impressions. Inputs/task: Read either owned output as ordered(impression_id, click_id) pairs. After phase 1, compare inner and outer sinks with the two-pair literal oracle. Expected: Both sinks contain(i1, c1),(i3, c2). i2/NULL isabsent because its possible match interval isnot yet finalized. c3 and c 4 produce no pair. Verify: Assert exact pair lists and absence of prematurei 2/NULL;do not rely only on output count 2.
# Exercise 5: Advance both sides and observe delayed outer finalization. Inputs/task: Publish distinct-key 00:30 advancers toboth sources, rerun both compatible queries and extract actual watermark/state-removal evidence. Expected: Inner remains two pairs. Outer becomes(i1, c1),(i2, NULL),(i3, c2). Actual watermark reaches at least 00:25 and state removal ispositive;the new advancer impression remains pending. Verify: Assert the complete outer ledger, input 2 for each new run, observed progress boundary and removed-state count.
# Exercise 6: Reject an outer join without an event-time bound. Inputs/task: In a separate owned checkpoint/output namespace, attempt a stream-stream left outer join using only key equality despite input watermarks. Require analysis rejection and stop any unexpectedly created query. Expected: AnalysisException because this design lacks the required bounded match/finalization condition. The valid inner/outer sinks remain unchanged and no query isactive. Verify: Assert the named rejection, inactive state and unchanged final valid outer pairs.
