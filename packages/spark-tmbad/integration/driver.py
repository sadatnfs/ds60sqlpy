"""Execute baseline, controlled worker loss, recovery and bounded-result checks."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import sys
import time
import traceback
from pathlib import Path

from control import Control
from validate import coverage, two_workers

ROWS = 32768
PARTITIONS = 8
DESTINATION = Path("/work/evidence")


class RefuseClassroomImports:
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "ds60sqlpy" or fullname.startswith("ds60sqlpy."):
            raise ImportError("Integration forbids classroom imports")
        return None


def package_identity():
    package = (
        "ds60_spark_tmbad"
        if os.environ["INTEGRATION_PACKAGE"] == "spark-tmbad"
        else "ds60_spark_likelihood"
    )
    distribution = importlib.metadata.distribution(package.replace("_", "-"))
    root = Path(distribution.locate_file(package)).resolve()
    if not root.is_relative_to(Path("/work/python")):
        raise AssertionError(
            "The standalone wheel must be imported from its offline noneditable installation"
        )
    observed = {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*.py"))
    }
    expected = json.loads(Path("/probe/source-identity.json").read_text())
    if observed != expected["python_source_sha256"]:
        raise AssertionError(
            "Installed wheel source differs from the copied package under qualification"
        )
    return {
        "distribution": distribution.metadata["Name"],
        "version": distribution.version,
        "installed_location": str(root),
        "python_source_sha256": observed,
        "wheel_sha256": expected["wheel_sha256"],
    }


def oversized_result_guard(spark):
    try:
        spark.range(0, 20000, 1, 2).selectExpr(
            "id", "sha2(CAST(id AS STRING), 256) AS payload"
        ).collect()
    except Exception as error:
        if "maxResultSize" not in str(error):
            raise AssertionError("Oversized collection failed for an unrelated reason") from error
        return {"status": "passed", "configured_limit": "128k", "raw_collection": "refused"}
    raise AssertionError("The driver unexpectedly accepted an oversized raw-data collection")


def main():
    from pyspark.sql import DataFrame, SparkSession
    from workload import Workload

    sys.meta_path.insert(0, RefuseClassroomImports())
    DESTINATION.mkdir(parents=True, exist_ok=True)
    control = Control()
    spark = None
    result = {
        "schema_version": 1,
        "status": "failed",
        "package": os.environ["INTEGRATION_PACKAGE"],
        "scope": (
            "one native host, isolated Compose master/two worker containers/separate driver; "
            "no multi-host or GPU claim"
        ),
    }
    try:
        result["installed_package"] = package_identity()
        spark = SparkSession.builder.appName("Isolated package Compose acceptance").getOrCreate()
        spark.sparkContext.setLogLevel("WARN")
        probe = spark._jvm.io.ds60.integration.Probe
        probe.attach(spark._jsparkSession)
        result["spark_version"] = spark.version
        result["driver_result_guard"] = oversized_result_guard(spark)
        result["executors_before"] = two_workers(json.loads(probe.identities(spark._jsparkSession)))
        work = Workload(spark, ROWS, PARTITIONS)
        frame = work.training()
        control.set_phase("baseline_fit")
        baseline_frame = DataFrame(probe.gated(frame._jdf, "baseline"), spark)
        result["baseline"] = work.fit_and_predict(baseline_frame)
        result["named_targets_before"] = work.named_target_check(baseline_frame)
        result["forecast_before"] = work.forecast()
        control.set_phase("loss_fit")
        loss_frame = DataFrame(probe.gated(frame._jdf, "loss"), spark)
        result["recovered"] = work.fit_and_predict(loss_frame)
        work.compare(result["baseline"], result["recovered"])
        result["named_targets_recovered"] = work.named_target_check(loss_frame)
        work.compare_named_targets(result["named_targets_before"], result["named_targets_recovered"])
        control.wait_restored()
        result["executors_after"] = two_workers(json.loads(probe.identities(spark._jsparkSession)))
        result["forecast_after"] = work.forecast()
        # Allow the asynchronous Spark listener to finish receiving the final events.
        time.sleep(1)
        result["spark_tasks"] = json.loads(probe.eventsJson())
        result["partition_events"] = list(control.events)
        result["coverage"] = {
            token: coverage(control.events, token, ROWS, PARTITIONS)
            for token in ["baseline", "loss"]
        }
        result["status"] = "passed"
        control.set_phase("complete")
    except BaseException as error:
        result["error"] = {"type": type(error).__name__, "message": str(error)[:4000]}
        traceback.print_exc()
        control.set_phase("failed")
    finally:
        if spark is not None:
            try:
                result["spark_tasks"] = json.loads(
                    spark._jvm.io.ds60.integration.Probe.eventsJson()
                )
            finally:
                spark.stop()
        result["partition_events"] = control.close()
        (DESTINATION / "driver.json").write_text(
            json.dumps(result, indent=2, allow_nan=False) + "\n"
        )
    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
