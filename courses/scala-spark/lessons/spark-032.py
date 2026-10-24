from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType
from pathlib import Path
from datetime import datetime,timedelta
import tempfile
import shutil
import os
import uuid
from pyspark.errors import AnalysisException

event_schema = StructType([StructField("id",LongType(),True),StructField("team",StringType(),True),StructField("amount",LongType(),True),StructField("event_time",TimestampType(),True)])
result_schema = StructType([StructField("window",StructType([StructField("start",TimestampType(),True),StructField("end",TimestampType(),True)]),True),StructField("team",StringType(),True),StructField("records",LongType(),True),StructField("total",LongType(),True)])
def publish(root,index,lines):
    target = root/"input"/f"batch-{index}.json"
    if target.exists(): raise ValueError("Input filename already published")
    staged = root/"staging"/(uuid.uuid4().hex+".tmp")
    try:
        with staged.open("x",encoding="utf-8") as handle: handle.write("\n".join(lines)+"\n")
        os.replace(staged,target)
    finally: staged.unlink(missing_ok=True)
def stream(spark,root):
    return spark.readStream.schema(event_schema).option("maxFilesPerTrigger",1).option("mode","FAILFAST").json(str(root/"input"))
def run_phase(spark,root):
    query = windowed(stream(spark,root)).writeStream.format("parquet").outputMode("append").option("checkpointLocation",str(root/"checkpoint")).trigger(availableNow=True).start(str(root/"output"))
    try:
        if not query.awaitTermination(30): raise TimeoutError("Finite phase timed out")
        if query.exception() is not None or query.isActive: raise RuntimeError("Phase did not terminate cleanly")
        return list(query.recentProgress)
    finally: query.stop()

def windowed(events):
    raise NotImplementedError("Complete windowed")

def watermarks(progress):
    raise NotImplementedError("Complete watermarks")

def final_rows(spark, root):
    raise NotImplementedError("Complete final_rows")

def dropped_rows(progress):
    raise NotImplementedError("Complete dropped_rows")

def event_ledger(phases, output):
    raise NotImplementedError("Complete event_ledger")

def reject_unsupported(spark, root, kind):
    raise NotImplementedError("Complete reject_unsupported")

def main():
    owned_root = None
    spark = (SparkSession.builder.appName("ds60-spark-032").master("local[2]")
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
        owned_root = Path(tempfile.mkdtemp(prefix=".ds60-spark-032-",dir=".")).resolve()
        (owned_root/"input").mkdir();(owned_root/"staging").mkdir()
        batches = [
         ['{"id":1,"team":"A","amount":10,"event_time":"2024-01-01T00:01:00Z"}','{"id":2,"team":"A","amount":20,"event_time":"2024-01-01T00:04:00Z"}'],
         ['{"id":3,"team":"A","amount":5,"event_time":"2024-01-01T00:03:00Z"}','{"id":4,"team":"A","amount":30,"event_time":"2024-01-01T00:12:00Z"}'],
         ['{"id":5,"team":"A","amount":999,"event_time":"2024-01-01T00:02:00Z"}','{"id":6,"team":"B","amount":7,"event_time":"2024-01-01T00:13:00Z"}'],
         ['{"id":7,"team":"__advance__","amount":0,"event_time":"2024-01-01T00:30:00Z"}']]
        first_window = [(1,10),(2,20),(3,5)]
        assert sum(amount for _,amount in first_window) == 35
        print("Retained out-of-order event contributes to35,not30")
        latest = datetime.fromisoformat("2024-01-01T00:30:00+00:00")
        assert latest-timedelta(minutes=5) == datetime.fromisoformat("2024-01-01T00:25:00+00:00")
        print("Five-minute delay is event-time arithmetic;actual watermark still needs a receipt")
        print("spark-032: worked examples passed; six task implementations remain")
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

# Exercise 1: Define watermark placement and window state. Inputs/task: Apply with Watermark(event_time,5minutes) before grouping by a 5-minute window and team. Aggregate records and total amount, retaining the window struct in the result. Expected: A streaming aggregate with window, team, records, total. The watermark is attached to the same event-time column used by the window. Verify: Assert streaming status and the four output fields before starting the first phase.
# Exercise 2: Record actual watermark progress after the first phase. Inputs/task: Run phase 1 and extract nonmissing watermark strings from retained progress. Parse them as instants rather than wall-clock elapsed duration. Expected: Exactly 2 input rows processed. At least one watermark observation exists;the final observed watermark is no later than 00:00 for this phase. Verify: Assert input count 2 and actual watermark presence/order;do not infer finalization from the file count alone.
# Exercise 3: Accept a retained out-of-order event and observe finalization. Inputs/task: Publish phase 2, run the compatible query again and read finalized sink rows as(start, team, records, total). Verify the 00:03 event contributed before the first window closed. Expected: The finalized sink contains only(00:00, A,3,35) at this point. The actual watermark reaches at least 00:07. Verify: Assert the exact first-window tuple and the observed progress boundary.
# Exercise 4: Observe a far-late drop after the window has closed. Inputs/task: Publish phase 3 after phase 2 has terminated. Read the actual state-operator dropped-by-watermark counters and verify the 999 event does not change the finalized first window. Expected: Two new source rows consumed, one observed watermark drop and unchanged first-window result 35. B at 00:13 remains in pending state. Verify: Assert input 2, drop counter 1 and the unchanged sink tuple. Preserve missing metric evidence as an error rather than guessing zero.
# Exercise 5: Advance event time and distinguish finalized frompending output. Inputs/task: Publish the 00:30 administrative advancer, run phase 4 and return a ledger of total source inputs, observed drops and final business-window records. Expected: Seven total inputs, one observed drop, five finalized business records across three tuples:(00:00, A,3,35),(00:10, A,1,30),(00:10, B,1,7). The advancer window remains pending. Verify: Assert all final tuples, input/drop reconciliation and actual watermark at least 00:25.
# Exercise 6: Verify output-mode and sink eligibility through explicit failures. Inputs/task: Attempt two invalid configurations in separate owned paths:Update mode to Parquet, and Append mode for an unwatermarked team aggregate. Require analysis rejection and stop any unexpectedly created query in finally. Expected: Both configurations raiseAnalysisException;no active query remains. The valid windowed append sink stays intact. Verify: Assert each named analysis failure and the unchanged three-row valid sink after the checks.
