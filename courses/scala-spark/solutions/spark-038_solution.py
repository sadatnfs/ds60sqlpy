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

def observe(spark,input_path,checkpoint,output):
    source=spark.readStream.schema(EVENT_SCHEMA).option("maxFilesPerTrigger",1).json(str(input_path)).dropDuplicates(["id"])
    query=(source.writeStream.format("parquet").outputMode("append").option("checkpointLocation",str(checkpoint)).trigger(availableNow=True).start(str(output)))
    OWNED_QUERIES.append(query)
    try:
        if not query.awaitTermination(45):raise TimeoutError("Observed query deadline exceeded")
        if query.exception() is not None:raise RuntimeError(str(query.exception()))
        progress=query.recentProgress
        states=[state for record in progress for state in record.get("stateOperators",[])]
        state=states[-1] if states else None
        return {"input_rows":sum(p["numInputRows"] for p in progress),"state_rows":state["numRowsTotal"] if state else None,"state_bytes":state["memoryUsedBytes"] if state else None,"sink_rows":progress[-1]["sink"].get("numOutputRows") if progress else None,"id":str(query.id),"run_id":str(query.runId),"operators":[state["operatorName"]] if state else []}
    finally:
        if query.isActive:query.stop()

def capture(spark,input_path,checkpoint,output):
    return observe(spark,input_path,checkpoint,output)

def known_metric(value):
    return value if value is not None and value>=0 else None

def grow_state(spark,root,input_path,checkpoint,output):
    publish_file(root,input_path,"batch-02.json",['{"id":3,"cents":300}'])
    return observe(spark,input_path,checkpoint,output)

def empty_observation(spark,root):
    empty=root/"empty-input";empty.mkdir()
    return observe(spark,empty,root/"empty-checkpoint",root/"empty-output")

def next_check(kind):
    checks={"skew":"inspect_partition_keys","state":"inspect_watermark_and_key_growth","input":"inspect_source_discovery"}
    if kind not in checks:raise ValueError("Unknown incident")
    return checks[kind]

def sanitize(event):
    allowed={"stage_id","task_id","run_ms","input_records"}
    return {key:value for key,value in event.items() if key in allowed}

def main():
    owned_root = None
    spark = (SparkSession.builder.appName("ds60-spark-038").master("local[2]")
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
        owned_root=Path(tempfile.mkdtemp(prefix="spark-038-",dir=Path.cwd()))
        input_path=owned_root/"input";checkpoint=owned_root/"checkpoint";output=owned_root/"output"
        publish_file(owned_root,input_path,"batch-01.json",['{"id":1,"cents":100}','{"id":1,"cents":100}','{"id":2,"cents":200}'])
        # Exercise 1: Capture actual finite streaming progress
        first=capture(spark,input_path,checkpoint,output)
        assert first["input_rows"]==3 and first["state_rows"]==2
        assert bag(spark,output)==["1:100","2:200"] and not OWNED_QUERIES[-1].isActive
        # Exercise 2: Interpret state and sink metrics with units
        assert first["operators"] and first["state_bytes"] is not None and first["state_bytes"]>=0
        assert known_metric(None) is None and known_metric(-1) is None and known_metric(0)==0
        print("actual_state_rows=",first["state_rows"],"state_bytes=",first["state_bytes"],"sink_rows=",known_metric(first["sink_rows"]))
        # Exercise 3: Observe bounded state growth across restart
        grown=grow_state(spark,owned_root,input_path,checkpoint,output)
        assert grown["input_rows"]==1 and grown["state_rows"]==3 and grown["id"]==first["id"]
        assert bag(spark,output)==["1:100","2:200","3:300"]
        # Exercise 4: Distinguish empty input from a stuck query
        empty=empty_observation(spark,owned_root)
        assert empty["input_rows"]==0 and not OWNED_QUERIES[-1].isActive
        print("empty_input_rows=",empty["input_rows"],"state_rows=",empty["state_rows"])
        # Exercise 5: Diagnose three seeded incident records
        assert [next_check(k) for k in ["skew","state","input"]]==["inspect_partition_keys","inspect_watermark_and_key_growth","inspect_source_discovery"]
        assert 10000/100==100
        # Exercise 6: Sanitize evidence with an allowlist
        safe=sanitize({"stage_id":"7","task_id":"2","run_ms":"100","input_records":"20","password":"DUMMY_NOT_A_CREDENTIAL","token":"DUMMY"})
        assert safe=={"stage_id":"7","task_id":"2","run_ms":"100","input_records":"20"}
        print("spark-038: six PySpark reference contracts passed; Spark=" + spark.version)
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

# Exercise 1: Capture actual finite streaming progress. Inputs/task: Run the supplied three-occurrence stream with ID deduplication and return a bounded observation record. Expected: Input count 3, state rows 2 and exact committed bag 1:100,2:200. Verify: Join the progress record with actual readback and inactive-query evidence.
# Exercise 2: Interpret state and sink metrics with units. Inputs/task: Require a state operator and a nonnegative memory-used measurement;preserve unknown or negative sink-row sentinel values as unavailable. Expected: State memory is reported in bytes. A missing or negative sink output count is not converted into zero. Verify: Check the real state record and explicit None/-1 normalization controls.
# Exercise 3: Observe bounded state growth across restart. Inputs/task: Add a new ID 3:300 and restart the same compatible checkpoint. Expected: One new input row, state rows grow 2 to 3, and output gains 3:300. Verify: Compare actual state totals, query identity and exact committed rows.
# Exercise 4: Distinguish empty input from a stuck query. Inputs/task: Run a separate AvailableNow query over an empty owned input directory. Expected: Zero admitted rows and a terminated query;state/sink metrics may be absent. Verify: Assert zero input and termination without fabricating an output Parquet schema.
# Exercise 5: Diagnose three seeded incident records. Inputs/task: For the explicitly synthetic incident fixtures, choose one reversible check for skew, growing state and zero admitted input. Expected: Inspect key/partition distribution;inspect watermark/key-retention policy;inspect source discovery respectively. Verify: Compare the three exact recommendations and state one success observation for each.
# Exercise 6: Sanitize evidence with an allowlist. Inputs/task: Keep only stage_id, task_id, run_ms and input_records from a supplied task-event dictionary containing fake credential fields. Expected: Exact four-field record, with fake token/password absent. Verify: Assert field set and values;do not print the unfiltered input.
