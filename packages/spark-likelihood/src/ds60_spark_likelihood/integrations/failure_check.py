"""Require a rank failure after output serialization to remain a failed launch."""

from __future__ import annotations

import json

from pyspark.ml.torch.distributor import TorchDistributor
from pyspark.sql import SparkSession

from .prepare_spark import require_prepared_wrapper


def fail_after_return():
    import atexit
    import os

    # Spark serializes this result before Python exits. That artifact must not
    # conceal the deliberately failed worker process.
    atexit.register(os._exit, 7)
    return {"numeric_result_before_failed_exit": 123}


def run():
    require_prepared_wrapper()
    spark = (
        SparkSession.builder.master("local[1]")
        .appName("ds60-failed-rank-check")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.driver.host", "127.0.0.1")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    try:
        # Capture the expected diagnostic so the outer successful check log
        # contains no misleading successful-training traceback.
        import contextlib
        import io

        captured = io.StringIO()
        try:
            with contextlib.redirect_stdout(captured):
                TorchDistributor(num_processes=1, local_mode=True, use_gpu=False).run(
                    fail_after_return
                )
        except RuntimeError as error:
            assert "failed with return code" in str(error)
            assert "ChildFailedError" in captured.getvalue()
        else:
            raise AssertionError("serialized output concealed a failed training rank")
        print(
            json.dumps(
                {
                    "kind": "spark-distributor-failed-exit-propagation",
                    "passed": True,
                    "worker_exit_code": 7,
                    "serialized_result_did_not_override_failure": True,
                }
            )
        )
    finally:
        spark.stop()


if __name__ == "__main__":
    run()
