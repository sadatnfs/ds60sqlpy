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

PRODUCT_SCHEMA=StructType([StructField("delivery",LongType(),True),StructField("id",StringType(),True),StructField("event_second",LongType(),True),StructField("cents",LongType(),True)])
PRODUCT_ATTEMPTS=[]
PRODUCT_ATTEMPT_ROWS=[]
PRODUCT_RUNS=[]
def empty_product():return {"accepted":{},"deliveries":set(),"duplicates":0,"late":0,"invalid":0,"max_event":None}
def product_sha(text):
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
def decode_events(text):
    rows=json.loads(text)
    if not isinstance(rows,list) or len(rows)>8:raise ValueError("Bounded event array required")
    for row in rows:
        if not isinstance(row,dict) or set(row)!={"delivery","id","event_second","cents"}:raise ValueError("Event field contract mismatch")
        if type(row["delivery"]) is not int or not 1<=row["delivery"]<=12:raise ValueError("Delivery identity required")
        if row["id"] is not None and type(row["id"]) is not str:raise ValueError("ID must be text or NULL")
        if any(row[key] is not None and type(row[key]) is not int for key in ("event_second","cents")):raise ValueError("Integer or NULL event fields required")
    return rows

def state_json(state):
    node={"accepted":[{"cents":value[1],"event_second":value[0],"id":key} for key,value in sorted(state["accepted"].items())],"deliveries":sorted(state["deliveries"]),"duplicates":state["duplicates"],"invalid":state["invalid"],"late":state["late"],"max_event_second":state["max_event"],"total_cents":sum(value[1] for value in state["accepted"].values())}
    return json.dumps(node,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def product_path(sink,batch_id):
    if type(batch_id) is not int or not 0<=batch_id<=8:raise ValueError("Bounded batch ID required")
    return sink/f"batch-{batch_id:020d}.json"
def load_product(sink,batch_id):
    node=json.loads(product_path(sink,batch_id).read_text(encoding="utf-8"))
    keys={"query_identity","batch_id","previous_sha256","input_sha256","input_json","state_json"}
    if not isinstance(node,dict) or set(node)!=keys or type(node["batch_id"]) is not int or node["batch_id"]!=batch_id:raise ValueError("Commit fields or batch ID mismatch")
    if any(type(node[key]) is not str for key in keys-{"batch_id"}) or node["query_identity"]!="late-product-v1":raise ValueError("Commit identity/type mismatch")
    previous=empty_product() if batch_id==0 else load_product(sink,batch_id-1)
    previous_hash="" if batch_id==0 else product_sha(product_path(sink,batch_id-1).read_text(encoding="utf-8"))
    if node["previous_sha256"]!=previous_hash or node["input_sha256"]!=product_sha(node["input_json"]):raise ValueError("Commit chain/input mismatch")
    expected=advance_policy(previous,decode_events(node["input_json"]))
    if node["state_json"]!=state_json(expected):raise ValueError("Committed product state differs from event ledger")
    return expected

def commit_product(sink,batch_id,text,fail_after=False):
    import os
    target=product_path(sink,batch_id)
    if target.exists():
        node=json.loads(target.read_text(encoding="utf-8"))
        if node.get("input_json")!=text:raise ValueError("Replayed batch content changed")
        return load_product(sink,batch_id)
    previous=empty_product() if batch_id==0 else load_product(sink,batch_id-1)
    next_state=advance_policy(previous,decode_events(text))
    node={"query_identity":"late-product-v1","batch_id":batch_id,"previous_sha256":"" if batch_id==0 else product_sha(product_path(sink,batch_id-1).read_text(encoding="utf-8")),"input_sha256":product_sha(text),"input_json":text,"state_json":state_json(next_state)}
    staged=sink/("pending-"+uuid.uuid4().hex+".json")
    try:
        with staged.open("x",encoding="utf-8") as handle:json.dump(node,handle,sort_keys=True,separators=(",",":"),ensure_ascii=False)
        os.rename(staged,target)
        if fail_after:raise RuntimeError("injected_after_publication")
        return next_state
    finally:staged.unlink(missing_ok=True)
def run_product(spark,input_path,checkpoint,sink,fail_after=False):
    binding=sink/"binding.txt"
    contract=str(input_path.resolve())+"\n"+str(checkpoint.resolve())+"\nlate-product-v1;cutoff=previous_max-10;limit=12"
    if binding.exists():
        if binding.read_text(encoding="utf-8")!=contract:raise ValueError("Product namespace binding mismatch")
    else:
        with binding.open("x",encoding="utf-8") as handle:handle.write(contract)
    frame=spark.readStream.schema(PRODUCT_SCHEMA).option("maxFilesPerTrigger",1).option("mode","FAILFAST").json(str(input_path))
    def callback(batch,batch_id):
        batch.persist()
        try:
            encoded=canonical_product_input(batch)
            PRODUCT_ATTEMPTS.append(batch_id);PRODUCT_ATTEMPT_ROWS.append(len(decode_events(encoded)))
            commit_product(sink,batch_id,encoded,fail_after)
        finally:batch.unpersist()
    query=(frame.writeStream.option("checkpointLocation",str(checkpoint)).trigger(availableNow=True).foreachBatch(callback).start())
    OWNED_QUERIES.append(query);PRODUCT_RUNS.append((str(query.id),str(query.runId)))
    try:
        if not query.awaitTermination(45):raise TimeoutError("Product deadline exceeded")
        if query.exception() is not None:raise RuntimeError(str(query.exception()))
        progress=query.recentProgress
        return {"id":str(query.id),"run_id":str(query.runId),"input_rows":sum(p["numInputRows"] for p in progress),"batches":[p["batchId"] for p in progress]}
    finally:
        if query.isActive:query.stop()

def canonical_product_input(frame):
    raise NotImplementedError("Complete canonical_product_input")

def advance_policy(previous,events):
    raise NotImplementedError("Complete advance_policy")

def fail_after_commit(spark,input_path,checkpoint,sink):
    raise NotImplementedError("Complete fail_after_commit")

def recover_product(spark,input_path,checkpoint,sink):
    raise NotImplementedError("Complete recover_product")

def finish_product(spark,root,input_path,checkpoint,sink):
    raise NotImplementedError("Complete finish_product")

def handoff_state(state):
    raise NotImplementedError("Complete handoff_state")

def main():
    owned_root = None
    spark = (SparkSession.builder.appName("ds60-spark-042").master("local[2]")
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
        owned_root=Path(tempfile.mkdtemp(prefix="spark-042-",dir=Path.cwd()))
        input_path=owned_root/"input";checkpoint=owned_root/"checkpoint";sink=owned_root/"sink";sink.mkdir()
        publish_file(owned_root,input_path,"batch-01.json",['{"delivery":1,"id":"A","event_second":100,"cents":10}', '{"delivery":2,"id":"B","event_second":105,"cents":20}', '{"delivery":3,"id":"A","event_second":100,"cents":10}', '{"delivery":4,"id":null,"event_second":106,"cents":30}'])
        static_a=spark.read.schema(PRODUCT_SCHEMA).json(str(input_path))
        previous_max=105;cutoff=previous_max-10
        ordered_seconds=[120,95,94]
        assert [second for second in ordered_seconds if second>=cutoff]==[120,95]
        counts=[5,2,1,2];accepted_cents=[10,20,0,40,5]
        assert sum(counts)==10 and len(accepted_cents)==5 and sum(accepted_cents)==75
        print("spark-042: worked examples passed; six task implementations remain")
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

# Exercise 1: Validate and canonicalize each raw microbatch. Inputs/task: Require the explicit four-field schema, at most 8 rows and unique delivery IDs 1..12. Preserve NULL/business-invalid fields for classification and emit deterministic JSON. Expected: BatchA has four occurrences with IDsA, B, A, NULL;NULL is preserved in canonical input. An oversized batch is rejected before collection. Verify: Compare decoded delivery IDs 1..4 and the NULL marker;reject a12-row union.
# Exercise 2: Implement the explicit state and lateness policy. Inputs/task: Freeze cutoff at previous committed max_event_second minus 10. Validate domain, then classify existing equal ID payload as duplicate, conflicting payload as invalid, new old event as late, and remaining event as accepted. Expected: AfterA:accepted 2, duplicate 1, late 0, invalid 1, total 30, max 105. An invalid far-future row does not advance max time. Verify: Assert exact state and an invalid future control;preserve the original state value.
# Exercise 3: Inject failure after publication but before query completion. Inputs/task: Run the actual foreachBatch query with one injected exception after the atomic commit file becomes visible. Expected: The query fails with injected_after_publication;commit 0 is readable and contains the correct first-state ledger. Verify: Inspect the expected streaming exception, attempt 0 and unchanged source/checkpoint ownership.
# Exercise 4: Replay the committed batch without applying it twice. Inputs/task: Restart the same compatible query and checkpoint. Validate the existing batch input/content/chain and reuse its state. Expected: Attempts 0,0 and callback rows 4,4;commit 0 bytes and logical state remain unchanged. Verify: Compare query/run identities, exact bytes and all first-state counters.
# Exercise 5: Process late, boundary, duplicate and conflicting events. Inputs/task: PublishBatchB thenBatchC as separate immutable files and run each finite invocation against the same checkpoint. Expected: Final accepted IDsA, B, D, E, F, total 75;duplicate 2, late 1, invalid 2;10 logical occurrences. Zero-valuedD and cutoff-boundaryF remain accepted. Verify: Compare intermediateB counts and the final literal state;the high-timeE must not make same-batchD late.
# Exercise 6: Hand off correctness, recovery and resource evidence. Inputs/task: Return the exact final canonical state, record callback work 14 versus logical occurrences 10, and reject binding the existing sink to a different checkpoint. Expected: Literal golden state matches;attempt IDs 0,0,1,2;callback rows 4,4,4,2;only owned inactive queries are eligible for cleanup. Verify: Compare the complete state JSON and namespace-refusal negative;state the single-writer/local-filesystem limitations.
