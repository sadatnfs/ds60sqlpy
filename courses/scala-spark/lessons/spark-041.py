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

def runtime_versions(spark):
    import sys,importlib.metadata
    try:arrow=importlib.metadata.version("pyarrow")
    except importlib.metadata.PackageNotFoundError:arrow="not-installed"
    jvm=spark.sparkContext._jvm
    return {"spark":spark.version,"scala":str(jvm.scala.util.Properties.versionNumberString()),"scala_binary":"2.13","java":str(jvm.java.lang.System.getProperty("java.version")),"java_major":str(jvm.java.lang.System.getProperty("java.specification.version")),"python":sys.version.split()[0],"arrow":arrow}
def run_keys(spark,input_path,checkpoint,output,keys):
    if keys not in (["id"],["id","cents"]):raise ValueError("Unknown state-key contract")
    frame=spark.readStream.schema(EVENT_SCHEMA).option("maxFilesPerTrigger",1).json(str(input_path)).dropDuplicates(keys)
    query=(frame.writeStream.format("parquet").outputMode("append").option("checkpointLocation",str(checkpoint)).trigger(availableNow=True).start(str(output)))
    OWNED_QUERIES.append(query)
    try:
        if not query.awaitTermination(45):raise TimeoutError("Compatibility rehearsal deadline")
        if query.exception() is not None:raise RuntimeError(str(query.exception()))
        progress=query.recentProgress
        return {"id":str(query.id),"run_id":str(query.runId),"input_rows":sum(p["numInputRows"] for p in progress),"batches":[p["batchId"] for p in progress]}
    finally:
        if query.isActive:query.stop()

def version_receipt(spark):
    raise NotImplementedError("Complete version_receipt")

def golden_metrics(frame):
    raise NotImplementedError("Complete golden_metrics")

def require_compatible(old_keys,new_keys):
    raise NotImplementedError("Complete require_compatible")

def candidate_run(spark,root,input_path):
    raise NotImplementedError("Complete candidate_run")

def rollback(spark,input_path,checkpoint,output):
    raise NotImplementedError("Complete rollback")

def may_promote(profile_qualified,golden_passed,recovery_reviewed,product_passed):
    raise NotImplementedError("Complete may_promote")

def main():
    owned_root = None
    spark = (SparkSession.builder.appName("ds60-spark-041").master("local[2]")
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
        owned_root=Path(tempfile.mkdtemp(prefix="spark-041-",dir=Path.cwd()))
        input_path=owned_root/"input";old_checkpoint=owned_root/"baseline-checkpoint";old_output=owned_root/"baseline-output"
        publish_file(owned_root,input_path,"batch-01.json",['{"id":1,"cents":100}','{"id":2,"cents":200}'])
        golden=spark.createDataFrame([(1,100),(1,100),(2,None),(3,0)],EVENT_SCHEMA)
        keys=["id"];changed=["id","cents"]
        assert keys!=changed
        same_instant=spark.sql("SELECT CAST(to_timestamp('2026-10-23T12:00:00-07:00') AS STRING)").first()[0]
        assert same_instant=="2026-10-23 19:00:00"
        print("spark-041: worked examples passed; six task implementations remain")
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

# Exercise 1: Capture the actual runtime tuple. Inputs/task: Record Spark, Scala binary and patch, JDK major and patch, Python version and optional PyArrow distribution version without installing anything. Expected: Spark 4.0.1, Scala 2.13 family, JDK 17;actual patch strings and explicit not-installed Arrow when absent. Verify: Inspect actual values and reject a claimed target qualification based only on a proposed version string.
# Exercise 2: Run a type, NULL and multiplicity golden suite. Inputs/task: Evaluate the supplied four-row bag plus exact decimal and timezone expressions. Expected: 4 rows,3 known amounts, total 200,3 distinct IDs;decimal 12345678.90;instant 19:00UTC. Verify: Compare exact metrics and rendered values under the UTC baseline.
# Exercise 3: Preserve baseline state and reject incompatible reuse. Inputs/task: Run the baseline ID-only deduplication query, then reject a request to change its state keys to id, cents while retaining that checkpoint. Expected: Baseline output 1:100,2:200;preflight rejects changed keys before starting a new query. Verify: Compare owned-query count before/after the refusal and confirm the old checkpoint/output remain present and unchanged.
# Exercise 4: Run the changed query in a separate candidate namespace. Inputs/task: Add a new occurrence 1:999 and run id, cents deduplication using a new checkpoint/output. Expected: Candidate bag 1:100,1:999,2:200, which fails the baseline one-row-per-ID product gate. Verify: Compare candidate and baseline exact bags and preserve old checkpoint/output.
# Exercise 5: Rehearse rollback to the preserved compatible query. Inputs/task: Resume the original ID-only query with its original checkpoint after the candidate is rejected. Expected: The same baseline query ID resumes;the new occurrence of already-seen ID 1 does not add a row;baseline output stays 1:100,2:200. Verify: Check query identity and exact sink bag without deleting either checkpoint.
# Exercise 6: Gate a proposed runtime change on actual evidence. Inputs/task: Require a qualified target profile, golden-suite pass, compatible recovery design and product acceptance before promotion. Expected: The supplied unqualified target or failed candidate is rejected;all four true permits a proposal in this pure decision model. Verify: Check missing-profile and wrong-product negatives, then record that no second runtime was provisioned.
