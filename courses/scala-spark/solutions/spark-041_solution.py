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
    return runtime_versions(spark)

def golden_metrics(frame):
    return tuple(frame.agg(F.count(F.lit(1)),F.count("cents"),F.sum("cents"),F.countDistinct("id")).first())

def require_compatible(old_keys,new_keys):
    if old_keys!=new_keys:raise ValueError("State-key change requires separate checkpoint and output")

def candidate_run(spark,root,input_path):
    publish_file(root,input_path,"batch-02.json",['{"id":1,"cents":999}'])
    return run_keys(spark,input_path,root/"candidate-checkpoint",root/"candidate-output",["id","cents"])

def rollback(spark,input_path,checkpoint,output):
    return run_keys(spark,input_path,checkpoint,output,["id"])

def may_promote(profile_qualified,golden_passed,recovery_reviewed,product_passed):
    return profile_qualified and golden_passed and recovery_reviewed and product_passed

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
        # Exercise 1: Capture the actual runtime tuple
        versions=version_receipt(spark)
        assert versions["spark"]=="4.0.1" and versions["scala"].startswith("2.13.") and versions["java_major"]=="17" and versions["python"]
        print("actual_versions=",versions)
        # Exercise 2: Run a type, NULL and multiplicity golden suite
        assert golden_metrics(golden)==(4,3,200,3)
        typed=spark.sql("SELECT CAST('12345678.90' AS DECIMAL(10,2)) AS price, CAST(to_timestamp('2026-10-23T12:00:00-07:00') AS STRING) AS instant").first()
        assert str(typed.price)=="12345678.90" and typed.instant=="2026-10-23 19:00:00"
        # Exercise 3: Preserve baseline state and reject incompatible reuse
        baseline=run_keys(spark,input_path,old_checkpoint,old_output,["id"])
        assert bag(spark,old_output)==["1:100","2:200"]
        query_count=len(OWNED_QUERIES)
        try:
            require_compatible(["id"],["id","cents"])
        except ValueError as error:
            assert "State-key change" in str(error)
        else:
            raise AssertionError("Incompatible checkpoint reuse accepted")
        assert len(OWNED_QUERIES)==query_count and old_checkpoint.is_dir() and bag(spark,old_output)==["1:100","2:200"]
        # Exercise 4: Run the changed query in a separate candidate namespace
        candidate=candidate_run(spark,owned_root,input_path)
        candidate_rows=bag(spark,owned_root/"candidate-output")
        assert candidate_rows==["1:100","1:999","2:200"] and candidate_rows!=["1:100","2:200"]
        assert candidate["id"]!=baseline["id"] and bag(spark,old_output)==["1:100","2:200"]
        # Exercise 5: Rehearse rollback to the preserved compatible query
        restored=rollback(spark,input_path,old_checkpoint,old_output)
        assert restored["id"]==baseline["id"] and bag(spark,old_output)==["1:100","2:200"]
        assert old_checkpoint.is_dir() and (owned_root/"candidate-checkpoint").is_dir()
        # Exercise 6: Gate a proposed runtime change on actual evidence
        assert not may_promote(False,True,True,True) and not may_promote(True,True,True,False) and may_promote(True,True,True,True)
        print("spark-041: six PySpark reference contracts passed; Spark=" + spark.version)
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
