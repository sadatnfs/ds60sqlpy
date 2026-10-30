"""Explicit CPU executor training entry point for a prepared Spark application.

Run with spark-submit after preparing the immutable snapshot, shared paths,
reviewed wrapper and Probe JAR. The caller owns the Spark application lifetime.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ds60_torch_training import data
from ds60_torch_training.launch import run_training
from ds60_torch_training.observer import ProbeObserver
from ds60_torch_training.training_examples import linear_sgd_oracle, mlp_adam_example
from pyspark.sql import SparkSession


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--probe-jar", type=Path, required=True)
    parser.add_argument("--probe-manifest", type=Path, required=True)
    parser.add_argument("--probe-source", type=Path, required=True)
    parser.add_argument("--mode", choices=("executor_single", "executor_ddp"), required=True)
    parser.add_argument("--recipe", choices=("linear-sgd", "mlp-adam"), required=True)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--steps-per-epoch", type=int, default=1)
    args = parser.parse_args()

    program = linear_sgd_oracle() if args.recipe == "linear-sgd" else mlp_adam_example()
    world = 1 if args.mode == "executor_single" else 2
    manifest = data.load_manifest(args.manifest)
    assignment = data.assign_shards(manifest, world)
    observer = ProbeObserver(
        probe_jar=args.probe_jar,
        probe_manifest=args.probe_manifest,
        probe_source=args.probe_source,
    )
    spark = SparkSession.builder.getOrCreate()
    try:
        receipt = run_training(
            spark,
            program,
            args.manifest,
            mode=args.mode,
            world_size=world,
            assignment=assignment,
            epochs=args.epochs,
            steps_per_epoch=args.steps_per_epoch,
            output_dir=args.output,
            observer=observer,
        )
        print(json.dumps(receipt, sort_keys=True))
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
