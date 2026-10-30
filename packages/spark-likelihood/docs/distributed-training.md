# Distributed training is a separate execution model

The low-dimensional likelihood optimizer supports at most 64 parameters and moves only numerical objective/gradient summaries to its driver. It is not a general neural-network DDP trainer. Large neural networks use a training loop, distributed optimizer state, data sharding, checkpointing and a failure policy appropriate to that workload.

The package retains separate, original integration examples using Spark's actual TorchDistributor, PyTorch DDP and Lightning. They have one- and two-process CPU oracles, explicit unequal-rank loss scaling and a sampler-padding audit. They demonstrate local process coordination. The bounded CPU executor training route in [CPU executor training](CPU-TORCH-TRAINING.md) has its own immutable data, checkpoint and observer contract. None of these local checks establishes remote-cluster or GPU performance.

## Prepare explicitly before running

Prepare optional Torch/Spark/Lightning dependencies before execution. Never install them inside a loss, fit or worker callback. The reviewed Spark 4.0.1 torchrun wrapper can otherwise return success after a rank fails, even when a result was already serialized. The narrow correction is source-hash checked and preserves the original Apache license header. Unknown upstream bytes are rejected.

Read-only check of the Spark distribution archive:

```bash
python -m ds60_spark_likelihood.integrations.prepare_spark \
  --archive /opt/spark/python/lib/pyspark.zip
```

Explicitly apply during a writable image/environment preparation step:

```bash
python -m ds60_spark_likelihood.integrations.prepare_spark \
  --archive /opt/spark/python/lib/pyspark.zip --apply
```

For an unpacked PySpark installation, the same helper accepts `--file` pointing to its reviewed `torch_run_process_wrapper.py`. Do not apply the correction to a different Spark release merely because the filename matches. Package import, model registration and fitting never apply this patch. Training examples only check preparation and fail clearly when it is missing.

## Run the separate examples

Launch the integration module through a small `spark-submit` script that imports and calls `training.run("torch-distributor")` or `training.run("lightning-ddp")` from `ds60_spark_likelihood.integrations`. The prepared project supplies loopback Gloo networking, a valid unprivileged user, a writable temporary Java home and bounded process resources. These deployment settings are distinct from the model's mathematics.

The explicit failure probe calls `ds60_spark_likelihood.integrations.failure_check.run()`. A rank returns a result and then deliberately exits with code seven. Acceptance requires the launcher to report failure despite the serialized result. A file existing on disk is never a substitute for process success.

The sampler-only example needs Torch but does not start training:

```bash
python -m ds60_spark_likelihood.integrations.sharding
```

It shows that five observations across two ranks can be padded to six memberships or reduced to four with `drop_last`. Exact likelihood work must account for actual membership and weights. Lightning's conveniences do not remove the author's responsibility for those contracts.
