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

ATTEMPTS=[]
STARTED_QUERIES=[]
def canonical_batch(frame):
    if [(f.name,f.dataType.simpleString()) for f in frame.schema.fields]!=[("id","bigint"),("cents","bigint")]:raise ValueError("Schema mismatch")
    if frame.count()>8:raise ValueError("At most8 rows per teaching microbatch")
    if frame.filter(F.col("id").isNull()|F.col("cents").isNull()|(F.col("id")<=0)|(F.col("cents")<0)).count():raise ValueError("Invalid records")
    return "".join(f"{r.id},{r.cents}\n" for r in frame.orderBy("id","cents").collect())
def sha(text):
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
def commit_path(root,identity,batch_id):
    import re
    if re.fullmatch(r"[a-z][a-z0-9-]{0,31}",identity) is None or type(batch_id) is not int or not 0<=batch_id<=1000:raise ValueError("Invalid query identity or bounded batch ID")
    return root/identity/f"batch-{batch_id:020d}.json"
def publish_batch(root,identity,batch_id,text,fail_before=False):
    import os
    target=commit_path(root,identity,batch_id);target.parent.mkdir(exist_ok=True)
    node={"query_identity":identity,"batch_id":batch_id,"sha256":sha(text),"data":text}
    if target.exists():
        existing=json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(existing,dict) or set(existing)!=set(node) or type(existing.get("batch_id")) is not int or any(type(existing.get(key)) is not str for key in ("query_identity","sha256","data")) or existing!=node:
            raise ValueError("Batch key reused for different content")
        return False
    staged=target.parent/("pending-"+uuid.uuid4().hex+".json")
    try:
        with staged.open("x",encoding="utf-8") as handle:json.dump(node,handle,sort_keys=True)
        if fail_before:raise RuntimeError("injected_before_publication")
        os.rename(staged,target)
        return True
    finally:
        staged.unlink(missing_ok=True)
def published_rows(root,identity):
    import re
    if re.fullmatch(r"[a-z][a-z0-9-]{0,31}",identity) is None:raise ValueError("Invalid identity")
    rows=[]
    for path in sorted((root/identity).glob("batch-*.json")):
        node=json.loads(path.read_text(encoding="utf-8"));text=node["data"]
        if node["query_identity"]!=identity or node["sha256"]!=sha(text):raise ValueError("Published receipt mismatch")
        rows.extend(text.splitlines())
    return sorted(rows)
def run_foreach(spark,input_path,checkpoint,sink,identity,fail_before=False):
    commit_path(sink,identity,0)
    binding=sink/(identity+"-binding.txt")
    expected=str(input_path.resolve())+"\n"+str(checkpoint.resolve())+"\nid:bigint,cents:bigint"
    if binding.exists():
        if binding.read_text(encoding="utf-8")!=expected:raise ValueError("Query namespace bound to another source/checkpoint/schema")
    else:
        with binding.open("x",encoding="utf-8") as handle:handle.write(expected)
    frame=spark.readStream.schema(EVENT_SCHEMA).option("maxFilesPerTrigger",1).option("mode","FAILFAST").json(str(input_path))
    def callback(batch,batch_id):
        ATTEMPTS.append(batch_id)
        batch.persist()
        try:publish_batch(sink,identity,batch_id,canonical_batch(batch),fail_before)
        finally:batch.unpersist()
    query=(frame.writeStream.option("checkpointLocation",str(checkpoint)).trigger(availableNow=True).foreachBatch(callback).start())
    OWNED_QUERIES.append(query);STARTED_QUERIES.append((str(query.id),str(query.runId)))
    try:
        if not query.awaitTermination(45):raise TimeoutError("Finite foreachBatch deadline exceeded")
        if query.exception() is not None:raise RuntimeError(str(query.exception()))
        progress=query.recentProgress
        return {"id":str(query.id),"run_id":str(query.runId),"input_rows":sum(p["numInputRows"] for p in progress),"batches":[p["batchId"] for p in progress]}
    finally:
        if query.isActive:query.stop()

def encode_batch(frame):
    return canonical_batch(frame)

def publish_once(root,identity,batch_id,text):
    return publish_batch(root,identity,batch_id,text,False)

def fail_callback(spark,input_path,checkpoint,sink):
    from pyspark.errors import StreamingQueryException
    try:
        run_foreach(spark,input_path,checkpoint,sink,"stream-v1",True)
    except StreamingQueryException as error:
        if "injected_before_publication" not in str(error):raise
    else:
        raise AssertionError("Expected injected streaming failure")

def recover_callback(spark,input_path,checkpoint,sink):
    return run_foreach(spark,input_path,checkpoint,sink,"stream-v1",False)

def unsafe_append(path,text):
    with path.open("a",encoding="utf-8") as handle:handle.write(text)

def reject_collision(root,text):
    try:
        publish_batch(root,"manual-v1",7,text+"9,999\n",False)
    except ValueError:
        pass
    else:
        raise AssertionError("Changed content reused a committed batch key")

def main():
    owned_root = None
    spark = (SparkSession.builder.appName("ds60-spark-036").master("local[2]")
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
        owned_root=Path(tempfile.mkdtemp(prefix="spark-036-",dir=Path.cwd()))
        input_path=owned_root/"input";checkpoint=owned_root/"checkpoint";sink=owned_root/"sink";sink.mkdir()
        publish_file(owned_root,input_path,"batch-01.json",['{"id":1,"cents":100}','{"id":2,"cents":200}'])
        static_frame=spark.read.schema(EVENT_SCHEMA).json(str(input_path))
        # Exercise 1: Define canonical bounded microbatch content
        encoded=encode_batch(static_frame)
        assert encoded=="1,100\n2,200\n" and sha(encode_batch(static_frame.repartition(2)))==sha(encoded)
        try:
            encode_batch(static_frame.withColumn("cents",F.lit(None).cast("long")))
        except ValueError:
            pass
        else:
            raise AssertionError("NULL cents accepted")
        # Exercise 2: Publish one logical batch idempotently
        assert publish_once(sink,"manual-v1",7,encoded)
        original=commit_path(sink,"manual-v1",7).read_bytes()
        assert not publish_once(sink,"manual-v1",7,encoded)
        assert commit_path(sink,"manual-v1",7).read_bytes()==original and published_rows(sink,"manual-v1")==["1,100","2,200"]
        # Exercise 3: Inject a real callback failure before publication
        fail_callback(spark,input_path,checkpoint,sink)
        assert ATTEMPTS==[0] and published_rows(sink,"stream-v1")==[] and not OWNED_QUERIES[-1].isActive
        # Exercise 4: Recover the same checkpoint and observe replay
        recovered=recover_callback(spark,input_path,checkpoint,sink)
        assert ATTEMPTS==[0,0] and published_rows(sink,"stream-v1")==["1,100","2,200"]
        assert STARTED_QUERIES[0][0]==STARTED_QUERIES[1][0] and STARTED_QUERIES[0][1]!=STARTED_QUERIES[1][1]
        # Exercise 5: Expose a non-idempotent append counterexample
        unsafe=owned_root/"unsafe-demo.txt"
        unsafe_append(unsafe,encoded);unsafe_append(unsafe,encoded)
        assert unsafe.read_text().splitlines()==["1,100","2,200","1,100","2,200"]
        assert len(published_rows(sink,"stream-v1"))==2
        # Exercise 6: Reject identity collisions and admit the next batch
        reject_collision(sink,encoded)
        assert commit_path(sink,"manual-v1",7).read_bytes()==original
        publish_file(owned_root,input_path,"batch-02.json",['{"id":3,"cents":300}'])
        recover_callback(spark,input_path,checkpoint,sink)
        assert ATTEMPTS==[0,0,1] and published_rows(sink,"stream-v1")==["1,100","2,200","3,300"]
        print("spark-036: six PySpark reference contracts passed; Spark=" + spark.version)
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

# Exercise 1: Define canonical bounded microbatch content. Inputs/task: Validate the explicit bigint schema, nonnegative cents, positive IDs and at most 8 rows;return sorted id, cents newline records preserving multiplicity. Expected: Exact text 1,100 newline 2,200 newline, with a stable SHA256 after repartitioning. Verify: Compare exact bytes and reject NULL cents before publication.
# Exercise 2: Publish one logical batch idempotently. Inputs/task: Publish the same canonical content twice under identity manual-v1 and batch 7. Compare the existing receipt instead of appending. Expected: First call publishes true;second returns false;exactly 2 logical rows remain. Verify: Assert return values, unchanged receipt bytes and one batch file.
# Exercise 3: Inject a real callback failure before publication. Inputs/task: Run the actual foreachBatch query with failure after staging and before rename. Retain the wrapped streaming exception and attempted batch ID. Expected: The query fails with injected_before_publication;no stream-v1 batch is visible and the attempted batch ID is 0. Verify: Check the exception marker, empty published rows and inactive query.
# Exercise 4: Recover the same checkpoint and observe replay. Inputs/task: Restart the same source/checkpoint/query namespace without failure. Compare attempts and logical query/run IDs. Expected: Batch 0 is attempted again and publishes 2 rows once. Query ID persists;run ID changes. Verify: Assert attempt sequence 0,0, exact rows and corresponding identities.
# Exercise 5: Expose a non-idempotent append counterexample. Inputs/task: Append the same canonical batch text twice to a separate unsafe-demo file, then compare it with the idempotent published batch. Expected: Unsafe append has 4 row occurrences;the committed batch remains 2. Verify: Compare exact repeated lines and preserve the unsafe file as a separate diagnostic until owned cleanup.
# Exercise 6: Reject identity collisions and admit the next batch. Inputs/task: Reject different content under an existing batch key, then publish a new source file 3:300 and resume the real query. Expected: The conflicting key fails without replacing its receipt. Stream batch 1 adds one row, leaving IDs 1,2,3 and total 600 across two batch files. Verify: Assert collision rejection, old receipt equality, attempt sequence 0,0,1 and exact 3-row sink.
