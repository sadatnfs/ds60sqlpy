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
    raise NotImplementedError("Complete inputs")

def bounded_join(impressions, clicks, kind):
    raise NotImplementedError("Complete bounded_join")

def run_join(spark, root, kind):
    raise NotImplementedError("Complete run_join")

def pairs(spark, root, kind):
    raise NotImplementedError("Complete pairs")

def progress_evidence(progress):
    raise NotImplementedError("Complete progress_evidence")

def reject_unbounded_outer(spark, root):
    raise NotImplementedError("Complete reject_unbounded_outer")

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
        impression_minute = 0
        assert 3 >= impression_minute and 3 < impression_minute+10
        assert not (10 >= impression_minute and 10 < impression_minute+10)
        print("Minute3 matches;minute10 is outside the half-open window")
        impressions = [("i1","A",0),("i2","B",0),("i3","C",5)]
        clicks = [("c1","A",3),("c2","C",10),("c3","A",10),("c4","Z",4)]
        pairs = [(i[0],c[0]) for i in impressions for c in clicks if i[1]==c[1] and i[2] <= c[2] < i[2]+10]
        assert pairs == [("i1","c1"),("i3","c2")]
        print("Independent business pair oracle=",pairs)
        print("spark-034: worked examples passed; six task implementations remain")
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
