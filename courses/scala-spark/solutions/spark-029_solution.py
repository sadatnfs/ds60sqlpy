from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    LongType,
    IntegerType,
    StringType,
    DoubleType,
    BooleanType,
    ArrayType,
    MapType,
    TimestampType,
    DecimalType,
)
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
    if not isinstance(run_id, str) or re.fullmatch(r"[a-z0-9-]{1,32}", run_id) is None:
        raise ValueError("Invalid run ID")


def receipt_text(run_id, digest):
    return json.dumps(
        {
            "run_id": run_id,
            "data_path": "runs/" + run_id + "/data",
            "row_count": 30,
            "schema": SCHEMA_TEXT,
            "sha256": digest,
        },
        separators=(",", ":"),
    )


def data_file_count(root):
    return sum(p.is_file() for p in root.rglob("*.parquet"))


def product_digest(frame):
    if [(f.name, f.dataType.simpleString()) for f in frame.schema.fields] != [
        ("id", "bigint"),
        ("value", "bigint"),
    ]:
        raise ValueError("Product schema mismatch")
    metrics = tuple(
        frame.agg(
            F.count(F.lit(1)), F.countDistinct("id"), F.min("id"), F.max("id"), F.sum("value")
        ).first()
    )
    if metrics != (30, 30, 0, 29, 870):
        raise ValueError("Product population mismatch")
    if frame.filter(
        F.col("id").isNull() | F.col("value").isNull() | (F.col("value") != F.col("id") * 2)
    ).count():
        raise ValueError("Product value mismatch")
    canonical = "\n".join(frame.orderBy("id").toJSON().collect())
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def stage_run(spark, root, run_id, source):
    check_run_id(run_id)
    digest = product_digest(source)
    run = root / "runs" / run_id
    if run.exists():
        existing = validate_staged(spark, root, run_id)
        if json.loads(existing)["sha256"] != digest:
            raise ValueError("Run identity has different content")
        return existing
    run.mkdir()
    source.write.mode("errorifexists").parquet(str(run / "data"))
    if product_digest(spark.read.parquet(str(run / "data"))) != digest:
        raise ValueError("Staging readback mismatch")
    text = receipt_text(run_id, digest)
    with (run / "receipt.json").open("x", encoding="utf-8") as handle:
        handle.write(text)
    return text


def validate_staged(spark, root, run_id):
    check_run_id(run_id)
    run = root / "runs" / run_id
    text = (run / "receipt.json").read_text(encoding="utf-8")
    node = json.loads(text)
    if node.get("run_id") != run_id or node.get("data_path") != "runs/" + run_id + "/data":
        raise ValueError("Receipt identity/path mismatch")
    if node.get("row_count") != 30 or node.get("schema") != SCHEMA_TEXT:
        raise ValueError("Receipt schema/count mismatch")
    if node.get("sha256") != product_digest(spark.read.parquet(str(run / "data"))):
        raise ValueError("Receipt content mismatch")
    return text


def publish_run(spark, root, run_id, fail_before_replace=False):
    text = validate_staged(spark, root, run_id)
    pending = root / ("manifest-pending-" + uuid.uuid4().hex + ".json")
    try:
        with pending.open("x", encoding="utf-8") as handle:
            handle.write(text)
        if fail_before_replace:
            raise RuntimeError("injected_before_publication")
        os.replace(pending, root / "current.json")
    finally:
        pending.unlink(missing_ok=True)


def read_published(spark, root):
    current = (root / "current.json").read_text(encoding="utf-8")
    node = json.loads(current)
    run_id = node.get("run_id")
    validated = validate_staged(spark, root, run_id)
    if json.loads(validated) != node:
        raise ValueError("Published manifest differs from validated receipt")
    return spark.read.parquet(str(root / "runs" / run_id / "data"))


def retry_product(spark, root, run_id, source):
    stage_run(spark, root, run_id, source)
    publish_run(spark, root, run_id)
    return product_digest(read_published(spark, root))


def main():
    owned_root = None
    spark = (
        SparkSession.builder.appName("ds60-spark-029")
        .master("local[2]")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.sql.adaptive.enabled", "false")
        .config("spark.sql.ansi.enabled", "true")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    try:
        assert spark.sparkContext.master == "local[2]"
        spark.sparkContext.setLogLevel("ERROR")
        owned_root = Path(tempfile.mkdtemp(prefix=".ds60-spark-029-", dir=".")).resolve()
        (owned_root / "runs").mkdir()
        source = spark.range(0, 30, 1, 2).withColumn("value", F.col("id") * 2)
        # Exercise 1: Validate the product before computing its digest
        digest = product_digest(source)
        assert (
            digest == "b4eaf827f5ce5797e0df60939b503b2ca6f264c0c167c9ca557db2aeb6cc2879"
            and product_digest(source.repartition(3)) == digest
        )
        try:
            product_digest(spark.range(31).withColumn("value", F.col("id") * 2))
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid31-row product accepted")
        # Exercise 2: Stage a run and validate the persisted readback
        staged_a = stage_run(spark, owned_root, "run-a", source)
        assert (owned_root / "runs/run-a/receipt.json").is_file()
        assert json.loads(staged_a)["sha256"] == digest
        # Exercise 3: Validate a receipt against a fixed owned data path
        assert validate_staged(spark, owned_root, "run-a") == staged_a
        try:
            validate_staged(spark, owned_root, "../outside")
        except ValueError:
            pass
        else:
            raise AssertionError("Traversal run ID accepted")
        # Exercise 4: Publish only a validated run at one explicit visibility point
        publish_run(spark, owned_root, "run-a")
        published_a = (owned_root / "current.json").read_text(encoding="utf-8")
        assert published_a == staged_a and json.loads(published_a)["run_id"] == "run-a"
        # Exercise 5: Keep the previous publication readable after an interrupted replacement
        stage_run(spark, owned_root, "run-b", source)
        try:
            publish_run(spark, owned_root, "run-b", True)
        except RuntimeError as error:
            assert str(error) == "injected_before_publication"
        else:
            raise AssertionError("Injected publication failure was lost")
        assert (owned_root / "current.json").read_text(encoding="utf-8") == published_a
        assert product_digest(read_published(spark, owned_root)) == digest
        # Exercise 6: Replay the same input without appending another product
        files_before = data_file_count(owned_root)
        assert retry_product(spark, owned_root, "run-a", source.repartition(3)) == digest
        assert (
            data_file_count(owned_root) == files_before
            and (owned_root / "current.json").read_text(encoding="utf-8") == published_a
        )
        try:
            retry_product(
                spark, owned_root, "run-c", spark.range(31).withColumn("value", F.col("id") * 2)
            )
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid replay product accepted")
        assert (owned_root / "current.json").read_text(encoding="utf-8") == published_a
        assert read_published(spark, owned_root).count() == 30
        print("spark-029: six PySpark reference contracts passed; Spark=" + spark.version)
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
