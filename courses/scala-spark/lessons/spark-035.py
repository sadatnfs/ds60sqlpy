from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType
from pathlib import Path
import tempfile
import shutil
import json
import uuid

EVENT_SCHEMA=StructType([StructField("id",LongType(),True),StructField("cents",LongType(),True)])
OWNED_QUERIES=[]
def publish_file(root,input_path,name,lines):
    import re,os
    if re.fullmatch(r"batch-[0-9]{2}\.json",name) is None or len(lines)>8 or any(len(line)>256 for line in lines):
        raise ValueError("Fixed finite file contract required")
    input_path.mkdir(exist_ok=True)
    staged=root/("pending-"+uuid.uuid4().hex+".json")
    try:
        with staged.open("x",encoding="utf-8") as handle:
            handle.write("\n".join(lines)+"\n")
        if (input_path/name).exists():raise ValueError("Input file identity already exists")
        os.rename(staged,input_path/name)
    finally:
        staged.unlink(missing_ok=True)
def run_parquet(spark,input_path,checkpoint,output):
    source=(spark.readStream.schema(EVENT_SCHEMA).option("maxFilesPerTrigger",1).option("mode","FAILFAST").json(str(input_path)))
    query=(source.writeStream.format("parquet").outputMode("append")
        .option("checkpointLocation",str(checkpoint)).trigger(availableNow=True).start(str(output)))
    OWNED_QUERIES.append(query)
    try:
        if not query.awaitTermination(45):raise TimeoutError("Finite query exceeded45-second deadline")
        if query.exception() is not None:raise RuntimeError(str(query.exception()))
        progress=query.recentProgress
        return {"id":str(query.id),"run_id":str(query.runId),"input_rows":sum(p["numInputRows"] for p in progress),"batches":[p["batchId"] for p in progress]}
    finally:
        if query.isActive:query.stop()
def bag(spark,path):
    frame=spark.read.parquet(str(path))
    if [(f.name,f.dataType.simpleString()) for f in frame.schema.fields]!=[("id","bigint"),("cents","bigint")]:raise ValueError("Result schema mismatch")
    if frame.count()>8:raise ValueError("Tiny result bound exceeded")
    return [f"{r.id}:{r.cents}" for r in frame.orderBy("id","cents").collect()]

def validated_bag(frame):
    raise NotImplementedError("Complete validated_bag")

def first_run(spark,input_path,checkpoint,output):
    raise NotImplementedError("Complete first_run")

def resume_new_file(spark,root,input_path,checkpoint,output):
    raise NotImplementedError("Complete resume_new_file")

def resume_empty(spark,input_path,checkpoint,output):
    raise NotImplementedError("Complete resume_empty")

def separate_replay(spark,input_path,checkpoint,output,old_checkpoint,old_output):
    raise NotImplementedError("Complete separate_replay")

def guarantee_ledger(frame):
    raise NotImplementedError("Complete guarantee_ledger")

def main():
    owned_root = None
    spark = (SparkSession.builder.appName("ds60-spark-035").master("local[2]")
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
        if spark.version!="4.0.1":raise ValueError("Prepared Spark4.0.1 required")
        spark.conf.set("spark.sql.streaming.stopTimeout","5000")
        owned_root=Path(tempfile.mkdtemp(prefix="spark-035-",dir=Path.cwd()))
        input_path=owned_root/"input";checkpoint=owned_root/"checkpoint";output=owned_root/"output"
        publish_file(owned_root,input_path,"batch-01.json",['{"id":1,"cents":100}','{"id":2,"cents":200}'])
        demo_input=owned_root/"demo-input"
        publish_file(owned_root,demo_input,"batch-01.json",['{"id":1,"cents":100}','{"id":2,"cents":200}'])
        demo_first=run_parquet(spark,demo_input,owned_root/"demo-checkpoint",owned_root/"demo-output")
        assert demo_first["input_rows"]==2 and bag(spark,owned_root/"demo-output")==["1:100","2:200"]
        publish_file(owned_root,demo_input,"batch-02.json",['{"id":2,"cents":200}','{"id":3,"cents":300}'])
        demo_second=run_parquet(spark,demo_input,owned_root/"demo-checkpoint",owned_root/"demo-output")
        assert demo_second["input_rows"]==2 and bag(spark,owned_root/"demo-output")==["1:100","2:200","2:200","3:300"]
        print("spark-035: worked examples passed; six task implementations remain")
    finally:
        try:
            for query in OWNED_QUERIES:
                if query.isActive:query.stop()
            if any(query.isActive for query in OWNED_QUERIES):raise RuntimeError("Do not remove scratch while an owned query is active")
            if owned_root is not None:
                if owned_root.parent!=Path.cwd() or not owned_root.name.startswith("spark-"):raise ValueError("Owned cleanup boundary mismatch")
                shutil.rmtree(owned_root)
        finally:
            spark.stop()

if __name__ == "__main__":
    main()

# Exercise 1: Validate the finite input and output grain. Inputs/task: Read a static copy of the two-row schema fixture and require bigint id/cents, known nonnull values and at most 8 rows. Return its canonical ordered bag without removing duplicates. Expected: The first bag is 1:100,2:200. A NULL identity or cents value is rejected. Verify: Compare the exact two-row bag and reject an explicit null-id DataFrame.
# Exercise 2: Run the first finite file stream. Inputs/task: Execute the AvailableNow Parquet query with its owned checkpoint/output and retain query ID, run ID, input count and batch IDs. Expected: Two input rows and exactly 1:100,2:200 in the committed sink. Verify: Assert the progress input count is 2, query is terminated, and readback bag is exact.
# Exercise 3: Resume the same checkpoint after a new file. Inputs/task: Publish a second file with 2:200 and 3:300, then restart the compatible query with the same checkpoint and sink. Expected: Only 2 new input rows are processed. The sink bag is 1:100,2:200,2:200,3:300. Query ID persists and run ID changes. Verify: Compare both identities, progress count and all 4 output occurrences.
# Exercise 4: Resume with no new source files. Inputs/task: Run the same compatible query again without adding input and compare output before/after. Expected: Zero new input rows and an unchanged 4-row output bag. Verify: Assert zero progress input sum and exact unchanged sink rows.
# Exercise 5: Replay with a separate checkpoint and output. Inputs/task: Start from a new checkpoint only when the output namespace is also new. Replay the same source and preserve the old checkpoint/sink. Expected: The separate output has 4 rows, with a new logical query ID. The old output remains 4 rows. Verify: Assert checkpoint/output paths differ and both independent bags equal the literal 4-row oracle.
# Exercise 6: Write a guarantee ledger from exact counts. Inputs/task: Return output row count, distinct business IDs and total cents, then explain why source recovery is not business-ID deduplication or a universal exactly-once guarantee. Expected: 4 occurrences,3 distinct IDs, total 800. Verify: Compare all three independent values and preserve the duplicate occurrence.
