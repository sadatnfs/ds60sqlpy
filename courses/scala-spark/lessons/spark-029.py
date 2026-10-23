from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType
from pathlib import Path
import tempfile
import shutil
import json
import hashlib
import re
import os
import uuid

SCHEMA_TEXT = "id:bigint,value:bigint"
def check_run_id(run_id):
    if not isinstance(run_id,str) or re.fullmatch(r"[a-z0-9-]{1,32}",run_id) is None:
        raise ValueError("Invalid run ID")
def receipt_text(run_id,digest):
    return json.dumps({"run_id":run_id,"data_path":"runs/"+run_id+"/data","row_count":30,"schema":SCHEMA_TEXT,"sha256":digest},separators=(",",":"))
def data_file_count(root):
    return sum(p.is_file() for p in root.rglob("*.parquet"))

def product_digest(frame):
    raise NotImplementedError("Complete product_digest")

def stage_run(spark, root, run_id, source):
    raise NotImplementedError("Complete stage_run")

def validate_staged(spark, root, run_id):
    raise NotImplementedError("Complete validate_staged")

def publish_run(spark, root, run_id, fail_before_replace=False):
    raise NotImplementedError("Complete publish_run")

def read_published(spark, root):
    raise NotImplementedError("Complete read_published")

def retry_product(spark, root, run_id, source):
    raise NotImplementedError("Complete retry_product")

def main():
    owned_root = None
    spark = (SparkSession.builder.appName("ds60-spark-029").master("local[2]")
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
        owned_root = Path(tempfile.mkdtemp(prefix=".ds60-spark-029-",dir=".")).resolve()
        (owned_root/"runs").mkdir()
        source = spark.range(0,30,1,2).withColumn("value",F.col("id")*2)
        ids = range(30)
        assert sum(i*2 for i in ids) == 870
        print("Declared30-row product total=870")
        a = receipt_text("run-a","0"*64);b = receipt_text("run-b","0"*64)
        assert json.loads(a)["data_path"] == "runs/run-a/data" and a != b
        print("A publication points to one run-specific product")
        print("spark-029: worked examples passed; six task implementations remain")
    finally:
        try:
            if owned_root is not None:
                shutil.rmtree(owned_root)
        finally:
            spark.stop()

if __name__ == "__main__":
    main()

# Exercise 1: Validate the product before computing its digest. Inputs/task: Require ordered fieldsid, value with bigint types, exactly 30 known unique IDs 0..29, known values equal to 2*id and total 870. ReturnSHA-256 of sorted SparkJSON lines joined by newline without a trailing newline. Expected: A64-character lowercase digest for the valid product. Wrong values, counts, types or identities are rejected before hashing. Verify: Assert a64-hex digest and equal digest after repartitioning;reject a31-row source.
# Exercise 2: Stage a run and validate the persisted readback. Inputs/task: Restrict run IDs to 1..32 lowercase letters, digits or hyphens. Validate input, write a fresh run-specific Parquet product, validate readback and save its receipt. If that run already exists, require its validated digest to match instead of appending. Expected: run-a has one 30-row data product and a receipt with the declared schema/count/path/digest. Reusing it never appends another product. Verify: Assert staged receipt existence and digest equality;all paths remain within the fresh owned root.
# Exercise 3: Validate a receipt against a fixed owned data path. Inputs/task: Read a run receipt and require its run_id, data_path, row_count, schema and digest to match the declared contract and actual Parquet readback. Construct the read path from validated runId rather than trusting arbitrary receipt text. Expected: Validrun-a receipt returns unchanged. A traversal-style run ID is rejected before path access. Verify: Assert receipt equality and explicit rejection of../outside.
# Exercise 4: Publish only a validated run at one explicit visibility point. Inputs/task: Validate the staged receipt, write it to a fresh temporary manifest beside current.json, and atomically replace current.json. Support an injected failure before replacement and clean any unpublished temporary manifest in finally. Expected: Publishingrun-a creates current.json selecting its 30-row product. No data is appended or rewritten during publication. Verify: Assert the current manifest equals the validated receipt and points torun-a.
# Exercise 5: Keep the previous publication readable after an interrupted replacement. Inputs/task: Read the current manifest, validate its selected run and return that product. Stage run-b, inject failure before its manifest replacement, and confirm the reader still seesrun-a. Expected: The injected error occurs, current.json bytes remain identical torun-a, and the published product still has 30 rows with the original digest. Verify: Assert the named exception, unchanged manifest and exact published product digest;run-b staging must not enter the reader population.
# Exercise 6: Replay the same input without appending another product. Inputs/task: Compose stage, validate/publish and readback for a repeated run ID. Retryrun-a with a different execution partition layout, then attempt an invalid 31-row product and confirm publication stays intact. Expected: Manifest bytes and data-file count are unchanged by validrun-a replay;published count remains 30. Invalid input fails before changing current.json. Verify: Assert digest, manifest bytes, file-count equality and negative-control rejection.
