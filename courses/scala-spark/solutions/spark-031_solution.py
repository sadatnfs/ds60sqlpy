from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType
from pathlib import Path
import tempfile
import shutil
import json
import re
import os
import uuid

event_schema = StructType([StructField("id",LongType(),True),StructField("team",StringType(),True),StructField("amount",LongType(),True)])

def publish_file(root, name, lines):
    if re.fullmatch(r"batch-[0-9]+\.json",name) is None:
        raise ValueError("Invalid input filename")
    target = root/"input"/name
    if target.exists():
        raise ValueError("Input file already exists")
    pending = root/"staging"/(uuid.uuid4().hex+".tmp")
    try:
        with pending.open("x",encoding="utf-8") as handle:
            handle.write("\n".join(lines)+"\n")
        os.replace(pending,target)
    finally:
        pending.unlink(missing_ok=True)

def input_stream(spark, root):
    return spark.readStream.schema(event_schema).option("maxFilesPerTrigger",1).json(str(root/"input"))

def team_summary(frame):
    return frame.groupBy("team").agg(F.count(F.lit(1)).alias("row_count"),F.count("amount").alias("known_amounts"),F.sum("amount").alias("total_amount"))

def run_available(summary, checkpoint, table):
    query = summary.writeStream.format("memory").queryName(table).outputMode("complete").option("checkpointLocation",str(checkpoint)).trigger(availableNow=True).start()
    try:
        if not query.awaitTermination(30):
            raise RuntimeError("AvailableNow deadline exceeded")
        if query.isActive or query.exception() is not None:
            raise RuntimeError("Query did not terminate cleanly")
        return query
    finally:
        query.stop()

def input_progress(query):
    return [(p["batchId"],p["numInputRows"]) for p in query.recentProgress]

def summary_rows(frame):
    return [tuple(r) for r in frame.orderBy("team").collect()]

def main():
    owned_root = None
    owned_table = None
    spark = (SparkSession.builder.appName("ds60-spark-031").master("local[2]")
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
        owned_root = Path(tempfile.mkdtemp(prefix=".ds60-spark-031-",dir=".")).resolve()
        (owned_root/"input").mkdir();(owned_root/"staging").mkdir()
        owned_table = "ds60_s031_"+uuid.uuid4().hex
        batches = [
         ['{"id":1,"team":"A","amount":10}','{"id":2,"team":"B","amount":20}','{"id":3,"team":"A","amount":0}'],
         ['{"id":4,"team":"B","amount":null}','{"id":5,"team":"C","amount":30}','{"id":6,"team":"A","amount":5}'],
         ['{"id":7,"team":"C","amount":0}','{"id":8,"team":"B","amount":15}','{"id":9,"team":"A","amount":null}']]
        # Exercise 1: Publish complete input files atomically
        for index,lines in enumerate(batches):
            publish_file(owned_root,f"batch-{index}.json",lines)
        assert len(list((owned_root/"input").glob("*.json"))) == 3
        try:
            publish_file(owned_root,"batch-0.json",batches[0])
        except ValueError:
            pass
        else:
            raise AssertionError("Existing input filename accepted")
        # Exercise 2: Construct an explicit streaming relation without starting it
        stream = input_stream(spark,owned_root)
        assert stream.isStreaming and [(f.name,f.dataType.simpleString()) for f in stream.schema.fields] == [("id","bigint"),("team","string"),("amount","bigint")]
        assert not spark.streams.active
        # Exercise 3: Define a cumulative aggregate with separate completeness counts
        summary = team_summary(stream)
        assert summary.isStreaming and summary.columns == ["team","row_count","known_amounts","total_amount"]
        # Exercise 4: Run AvailableNow with a deadline and owned cleanup
        query = run_available(summary,owned_root/"checkpoint",owned_table)
        assert not query.isActive and not spark.streams.active
        # Exercise 5: Reconcile processed input through progress evidence
        progress = input_progress(query)
        positive = [row for row in progress if row[1] > 0]
        assert sum(n for _,n in progress) == 9 and len(positive) == 3 and all(n == 3 for _,n in positive)
        assert len({batch for batch,_ in progress}) == len(progress)
        print("input_progress=",progress)
        # Exercise 6: Compare final streaming output with batch and literal oracles
        actual = summary_rows(spark.table(owned_table))
        batch = spark.read.schema(event_schema).json(str(owned_root/"input"))
        expected = [("A",4,3,15),("B",3,2,35),("C",2,2,30)]
        assert actual == expected and summary_rows(team_summary(batch)) == expected
        assert sum(r[1] for r in actual) == 9 and sum(r[2] for r in actual) == 7 and sum(r[3] for r in actual) == 80 and not spark.streams.active
        print("spark-031: six PySpark reference contracts passed; Spark=" + spark.version)
    finally:
        try:
            if any(q.name == owned_table for q in spark.streams.active):
                raise RuntimeError("Owned query still active; preserve scratch")
            if owned_table is not None:
                spark.catalog.dropTempView(owned_table)
            if owned_root is not None:
                shutil.rmtree(owned_root)
        finally:
            spark.stop()

if __name__ == "__main__":
    main()

# Exercise 1: Publish complete input files atomically. Inputs/task: Write each declared file in the owned staging directory, then atomically move it into input under a new batch-N.json name. Reject invalid names or an existing destination. Expected: Three input files, each with 3 completeJSON records;no staging temporary file remains. Reusing batch-0.json is rejected. Verify: Assert the file count and explicit existing-name rejection before starting any query.
# Exercise 2: Construct an explicit streaming relation without starting it. Inputs/task: Read the owned JSON input through readStream with the declared schema and maxFilesPerTrigger 1. Return the streamingDataFrame;do not call an ordinary batch collect on it. Expected: isStreaming istrue, columns areid, team, amount and their types arebigint, string, bigint. No query is started by construction alone. Verify: Assert streaming status and exact type mapping while the active query list remains empty.
# Exercise 3: Define a cumulative aggregate with separate completeness counts. Inputs/task: Group by team and compute row_count, known_amounts and total_amount. Use the same expression for streaming and batch relations without filling unknown amounts. Expected: The streaming result remains streaming and has one state/result row per team. Its eventual literal result isA(4,3,15), B(3,2,35), C(2,2,30). Verify: Assert output columns and streaming status now;verify the exact final tuples after bounded execution.
# Exercise 4: Run AvailableNow with a deadline and owned cleanup. Inputs/task: Start the aggregate in a uniquely named memory sink with complete mode, a fresh checkpoint and AvailableNow. Await at most 30 seconds, require termination and always stop the query in finally. Expected: The query terminates and isActive isfalse. The memory table holds the final finite aggregate;the checkpoint belongs only to this run. Verify: Assert bounded await success, no query exception and inactive state. No sleep or external producer is used.
# Exercise 5: Reconcile processed input through progress evidence. Inputs/task: Return(batch_id, num_input_rows) from retained query progress. Sum input rows and inspect positive-input batches without confusing cumulative sink snapshots with new input. Expected: Three positive-input batches of 3 records and total input 9. Any zero-input progress entry contributes zero to that total. Verify: Assert total 9, three positive batches of 3 and unique recorded batch IDs;print the actual ledger.
# Exercise 6: Compare final streaming output with batch and literal oracles. Inputs/task: Read the final memory table, compare its ordered summary tuples with a batch read of the same nine source records, and compare both with the literalA/B/C oracle. Expected: ExactlyA(4,3,15), B(3,2,35), C(2,2,30), whose record counts sum 9, known counts 7 and amounts 80. Verify: Assert both path comparisons and the independent literal tuple list;confirm no active query remains before cleanup.
