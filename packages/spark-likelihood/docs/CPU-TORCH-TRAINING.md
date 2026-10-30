# CPU executor training examples

The current examples use named, importable factories in
`ds60_torch_training.training_examples`. Importing their descriptors does not load
Torch. Actual training uses `run_training` on an existing Spark Classic 4.0.1
session, a prepared torchrun exit-status wrapper, an immutable shard manifest,
and an independent Spark task observer. Both admitted modes set
`local_mode=False` and `use_gpu=False` in the public `TorchDistributor.run` API.

## Weighted six-row SGD check

`linear_sgd_oracle()` constructs an ordinary `nn.Linear(1, 1)` with weight and
bias set to zero, `BCEWithLogitsLoss(reduction="none")`, and `SGD(lr=0.1)`.
Use the same feature value `x=1` for six rows and explicitly map four rows to
rank 0 and two to rank 1. With labels `[0,1,1,0,1,1]` and unit weights, the
global initial gradient is `-1/6`; one full-batch step makes both parameters
`1/60`. With labels `[0,1,1,0,1,0]` and weights `[1,3,1,0,2,1]`, the global
weight mass is `8`, the initial gradient is `-1/4`, and both parameters become
`1/40`. These are per-step numerical oracles, not convergence claims.

```python
from ds60_torch_training import data
from ds60_torch_training.launch import run_training
from ds60_torch_training.training_examples import linear_sgd_oracle

# Keep this directory on storage visible to every executor and its replacement.
manifest_path = data.prepare_rows(
    rows, "/shared/owned/oracle-data", feature_names=["x"], num_shards=6
)
manifest = data.load_manifest(manifest_path)
assignment = data.assign_shards(
    manifest, 2,
    rank_files=[
        ["shards/part-00000.jsonl", "shards/part-00001.jsonl",
         "shards/part-00002.jsonl", "shards/part-00003.jsonl"],
        ["shards/part-00004.jsonl", "shards/part-00005.jsonl"],
    ],
)
receipt = run_training(
    spark, linear_sgd_oracle(), manifest_path,
    mode="executor_ddp", world_size=2, assignment=assignment,
    epochs=1, steps_per_epoch=1, max_batch_rows=4, seed=17,
    output_dir="/shared/owned/oracle-run", observer=observer,
)
```

The `rows`, `spark`, and `observer` values must come from the caller's explicit
data and integration setup. `prepare_rows` is only for bounded original rows.
For a Spark DataFrame, call `prepare_dataframe` separately so its writers run on
executors and only metadata returns to the driver. The observer must verify
executor placement and task attempts independently. A returned worker result
alone is provisional.

The [spark-submit entry point](../examples/cpu_torch_training.py) accepts an
already prepared manifest, an owned output directory and the prepared Probe
source/JAR identity. It does not prepare Spark or download dependencies.

## Ordinary MLP and exact continuation

`mlp_adam_example()` creates `Linear(2,16)`, ReLU, Dropout(0.2),
`Linear(16,8)`, Tanh, `Linear(8,1)`, the same per-row binary loss, and Adam.
It has more than 64 parameters. A checkpoint is committed at each completed
epoch. To resume, start a new `run_training` attempt with the same program,
snapshot, assignment, complete schedule, and a verified committed
`CheckpointRef` from the prior attempt. The new `output_dir` must be fresh.
Only a changed physical worker placement is permitted during exact resume;
the logical rank-to-shard map and all source, layout, optimizer and RNG
identities remain fixed. A committed checkpoint from a failed run does not
claim that run succeeded.

## Prediction from a trusted completed checkpoint

After the launcher records a completed attempt and independently verifies its
final checkpoint, trusted application code can construct the same named model,
loss, and optimizer, derive the exact checkpoint binding from the accepted plan,
load rank 0 with `checkpoint.load_rank`, and restore with
`torch_adapter.restore_rank_state`. Then call `model.eval()` and compute
`torch.sigmoid(model(x))` for a bounded, explicitly ordered CPU feature tensor.
This is a local inference example; the training package does not expose a
distributed prediction API or a fitted likelihood interface. Do not load a
module or arbitrary callable from checkpoint data.

The initial scope excludes GPU, Spark Connect, mutable model buffers, class
weighting or ignored class labels, changing world size, custom callbacks,
gradient accumulation, automatic data cycling, and implicit model downloads.
