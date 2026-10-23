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

TEST_SCHEMA=StructType([StructField("id",LongType(),True),StructField("event_second",LongType(),True),StructField("cents",LongType(),True)])
def run_scenario(spark,input_path,checkpoint,output,mode):
    if mode not in {"restart","duplicates","late","invalid"}:raise ValueError("Unknown scenario")
    raw=spark.readStream.schema(TEST_SCHEMA).option("maxFilesPerTrigger",1).option("mode","FAILFAST").json(str(input_path))
    if mode=="duplicates":selected=raw.select("id","cents").dropDuplicates(["id"])
    elif mode=="late":selected=raw.filter(F.col("event_second")>=90).select("id","cents")
    elif mode=="invalid":selected=raw.filter(F.col("id").isNotNull()&F.col("event_second").isNotNull()&F.col("cents").isNotNull()&(F.col("id")>0)&(F.col("cents")>=0)).select("id","cents")
    else:selected=raw.select("id","cents")
    query=(selected.writeStream.format("parquet").outputMode("append").option("checkpointLocation",str(checkpoint)).trigger(availableNow=True).start(str(output)))
    OWNED_QUERIES.append(query)
    try:
        if not query.awaitTermination(45):raise TimeoutError("Scenario deadline exceeded")
        if query.exception() is not None:raise RuntimeError(str(query.exception()))
        progress=query.recentProgress
        return {"id":str(query.id),"run_id":str(query.runId),"input_rows":sum(p["numInputRows"] for p in progress),"batches":[p["batchId"] for p in progress]}
    finally:
        if query.isActive:query.stop()
def prepare_case(root,name,lines):
    if name not in {"restart","duplicates","late","invalid","demo"}:raise ValueError("Unknown owned case")
    input_path=root/(name+"-input")
    publish_file(root,input_path,"batch-01.json",lines)
    return input_path,root/(name+"-checkpoint"),root/(name+"-output")

def baseline(spark,paths):
    return run_scenario(spark,*paths,"restart")

def restart_empty(spark,paths):
    return run_scenario(spark,*paths,"restart")

def duplicate_case(spark,paths):
    return run_scenario(spark,*paths,"duplicates")

def late_case(spark,paths):
    return run_scenario(spark,*paths,"late")

def invalid_case(spark,paths):
    return run_scenario(spark,*paths,"invalid")

def require_bag(actual,expected):
    if actual!=expected:raise ValueError("Canonical bag mismatch")

def main():
    owned_root = None
    spark = (SparkSession.builder.appName("ds60-spark-037").master("local[2]")
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
        owned_root=Path(tempfile.mkdtemp(prefix="spark-037-",dir=Path.cwd()))
        restart_paths=prepare_case(owned_root,'restart',['{"id":1,"event_second":100,"cents":100}', '{"id":2,"event_second":110,"cents":200}'])
        duplicate_paths=prepare_case(owned_root,'duplicates',['{"id":1,"event_second":100,"cents":100}', '{"id":1,"event_second":100,"cents":100}'])
        late_paths=prepare_case(owned_root,'late',['{"id":1,"event_second":80,"cents":100}', '{"id":2,"event_second":90,"cents":200}', '{"id":3,"event_second":110,"cents":300}'])
        invalid_paths=prepare_case(owned_root,'invalid',['{"id":null,"event_second":100,"cents":100}', '{"id":2,"event_second":100,"cents":-1}', '{"id":3,"event_second":100,"cents":300}'])
        # Exercise 1: Establish a finite restart baseline
        first=baseline(spark,restart_paths)
        assert first["input_rows"]==2 and bag(spark,restart_paths[2])==["1:100","2:200"] and not OWNED_QUERIES[-1].isActive
        # Exercise 2: Prove no-input recovery without a sleep
        again=restart_empty(spark,restart_paths)
        assert again["id"]==first["id"] and again["run_id"]!=first["run_id"] and again["input_rows"]==0
        assert bag(spark,restart_paths[2])==["1:100","2:200"]
        # Exercise 3: Test real streaming duplicate suppression
        duplicate=duplicate_case(spark,duplicate_paths)
        assert duplicate["input_rows"]==2 and bag(spark,duplicate_paths[2])==["1:100"]
        # Exercise 4: Test the exact event-time boundary
        late=late_case(spark,late_paths)
        late_raw_rows=spark.read.schema(TEST_SCHEMA).json(str(late_paths[0])).count()
        late_rows=bag(spark,late_paths[2])
        print("late_raw_rows=",late_raw_rows,"progress_input_rows=",late["input_rows"],"committed=",late_rows,"json_pushdown=",spark.conf.get("spark.sql.json.filterPushdown.enabled"))
        assert late_raw_rows==3 and late_rows==["2:200","3:300"] and len(late_rows)<=late["input_rows"]<=late_raw_rows
        # Exercise 5: Keep invalid rows visible in the case ledger
        invalid=invalid_case(spark,invalid_paths)
        invalid_rows=bag(spark,invalid_paths[2])
        raw_count=spark.read.schema(TEST_SCHEMA).json(str(invalid_paths[0])).count()
        print("invalid_raw_rows=",raw_count,"progress_input_rows=",invalid["input_rows"],"committed=",invalid_rows)
        assert raw_count==3 and invalid_rows==["3:300"] and len(invalid_rows)<=invalid["input_rows"]<=raw_count
        invalid_raw=spark.read.schema(TEST_SCHEMA).json(str(invalid_paths[0]))
        assert invalid_raw.filter(F.col("id").isNull()|(F.col("cents")<0)).count()==2
        # Exercise 6: Prove the oracle rejects a plausible regression
        require_bag(bag(spark,duplicate_paths[2]),["1:100"])
        try:
            require_bag(["1:100","1:100"],["1:100"])
        except ValueError as error:
            assert str(error)=="Canonical bag mismatch"
        else:
            raise AssertionError("Unsafe duplicate publication escaped the oracle")
        assert all(not q.isActive for q in OWNED_QUERIES)
        print("spark-037: six PySpark reference contracts passed; Spark=" + spark.version)
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

# Exercise 1: Establish a finite restart baseline. Inputs/task: Run the restart scenario with two supplied records and retain progress plus exact sink values. Expected: 2 input rows and bag 1:100,2:200. Verify: Assert the literal bag, input count 2 and inactive query.
# Exercise 2: Prove no-input recovery without a sleep. Inputs/task: Restart the compatible baseline with its existing checkpoint and no new file. Expected: Same query ID, new run ID, zero new rows and unchanged sink. Verify: Compare identities, input sum and exact bag;allow empty progress entries.
# Exercise 3: Test real streaming duplicate suppression. Inputs/task: Use native streaming dropDuplicates on the id key for two identical occurrences of 1:100. Expected: 2 source rows,1 committed row 1:100. Verify: Compare input count 2 and the one-row bag.
# Exercise 4: Test the exact event-time boundary. Inputs/task: Apply the explicitly declared admission cutoff event_second>=90 to rows at 80,90 and 110. Expected: 3 source rows;accepted IDs 2,3 with cents 200,300. Verify: Compare exact two-row bag and explain why 90 is retained.
# Exercise 5: Keep invalid rows visible in the case ledger. Inputs/task: Reject a NULL identity and a negative amount while retaining valid 3:300. Expected: 3 input occurrences,2 invalid,1 accepted. Verify: Compare raw source count 3, actual progress, sink bag 3:300 and static predicate count 2.
# Exercise 6: Prove the oracle rejects a plausible regression. Inputs/task: Compare the correct duplicate-case bag with an unsafe two-copy append result and reject the mismatch. Confirm every owned query is inactive before cleanup. Expected: Correct bag passes;duplicated bag raises an assertion-contract error;all owned queries are inactive. Verify: Catch the specific mismatch and compare the exact offending rows.
