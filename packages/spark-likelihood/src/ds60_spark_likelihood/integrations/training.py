"""Exercise Spark's actual launcher with two CPU ranks on one machine."""

from __future__ import annotations

import argparse
import json

from pyspark.ml.torch.distributor import TorchDistributor
from pyspark.sql import SparkSession

from .distributed_cases import train_ddp_step, train_lightning_step
from .prepare_spark import require_prepared_wrapper


def run(case):
    require_prepared_wrapper()
    spark = (
        SparkSession.builder.master("local[2]")
        .appName("ds60-distributor-check")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.driver.host", "127.0.0.1")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    try:
        function = train_ddp_step if case == "torch-distributor" else train_lightning_step
        # local_mode=True invokes torchrun on the driver with two local ranks.
        # Spark's distributed executor mode is a separate deployment qualification.
        for count in (1, 2) if case == "torch-distributor" else (2,):
            output = TorchDistributor(num_processes=count, local_mode=True, use_gpu=False).run(
                function
            )
            output["spark"] = spark.version
            output["launcher_local_mode"] = True
            print(json.dumps(output, sort_keys=True))

    finally:
        spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=("torch-distributor", "lightning-ddp"))
    run(parser.parse_args().case)
