# Independent one-wheel CPU Torch training qualification

This directory qualifies the copied `ds60-spark-likelihood` 0.2.0 candidate from its own source tree and one noneditable wheel. It does not import from the original workspace or the earlier work-only draft. The existing `integration/` likelihood and worker-loss baseline remains separate and unchanged.

## Admission

Build the candidate wheel first from this copied project. `run.py` accepts only an existing local image ID and one `ds60_spark_likelihood-0.2.0-*.whl`. Before any container starts, it compares every Python module under this copy's `src/` with the corresponding wheel member and SHA256 entry in the wheel RECORD. It repeats that comparison after the run and records the image ID, source hashes, wheel hash, Probe source/JAR hashes, exact owned project and service IDs, failures and cleanup. It rejects image/engine architecture mismatch. It does not pull, build or publish an image.

```bash
python training-integration/run.py \
  --image LOCAL_PREPARED_IMAGE_ID \
  --wheel FRESH_INTEGRATED_WHEEL \
  --output FRESH_PRIVATE_EVIDENCE_DIRECTORY \
  --timeout 1200
```

`--case-set dataframe` runs only the typed Spark DataFrame snapshot and two-rank weighted oracle. The default `full` sequence runs `single`, `reference`, `fault`, and `resume`. Each call requires a new output directory. The host timeout must be between 180 and 1800 seconds. Keep one local heavy runtime at a time.

## Owned topology and cases

Compose uses one master, two one-core worker containers and a separate driver on an internal-only network. Memory caps are 384, 2048, 2048 and 1408 MiB, totaling 5.75 GiB. CPU caps total 3. The setup has no ports, volumes, engine socket mount or registry pull. The original Probe is compiled offline before Compose and its loaded JAR identity is checked. All Spark services run as the image's existing UID/GID 65534. Fresh bind scratch is writable only within the private run output; the wheel and Probe mounts are read-only. The driver application uses `spark.task.maxFailures=1`, disables speculation and dynamic allocation, and keeps both CPU modes on public `TorchDistributor.run` with `local_mode=False`.

The six-row SGD controls run with one and two executors. Their expected weight and bias after a 0.1 step are 1/60 for the unweighted data and 1/40 for the unequal-weight data. The DataFrame case writes immutable typed JSONL shards on executors, collects bounded metadata, verifies all six IDs through executor bitmasks and checks the 1/40 two-rank result. A separate MLP/Adam/Dropout reference runs for two epochs with more than 64 parameters.

The worker-loss model is a named, source-bound private integration fixture in `src/ds60_torch_training/_integration_fixture.py`. The same model factory and configuration are used for the uninterrupted reference, fault and resume. Only the fault application receives a fresh exact gate token through executor environment. Rank 1 writes a token-bound marker after epoch 0 is committed and before epoch 1's forward pass. The host verifies that marker, stops the actual owned worker container, requires the failed attempt and driver exit, recreates only that worker, then explicitly starts a new application from the committed checkpoint. The resumed model, optimizer, RNG, data ledgers and progress must match the uninterrupted control on both ranks. The public runner has no fault-token parameter.

Exit and case reports are published through same-directory temporary files and atomic replacement. The host reads bounded private evidence through the owning container UID so native Linux bind permissions cannot hide 0600 checkpoint files. Before cleanup it copies at most 128 MiB of owned shared evidence back to a host-owned `shared-collected/` directory. The host retains all failure receipts and only cleans its own Compose project. A checkpoint alone never makes a failed training attempt successful.

`prediction_followup.py` can separately load the two committed final checkpoints with the same one wheel, construct the trusted private MLP in eval mode and compare fixed response-free float64 sigmoid scores. That is local checkpoint inference. It does not claim a generic Spark prediction or forecast API.

## Preparation and evidence limits

The copied project's default Dockerfile uses neutral public Python and Spark bases, native architecture locks and explicit Spark 4.0.1 wrapper preparation. It does not require a classroom image. Its default build needs access to the public base registries, PyTorch CPU package index and PyPI. Offline dependency preparation requires a separately populated wheelhouse, which is not bundled here. A passing source-only check or the earlier work-only local ARM64 result does not qualify this integrated wheel. Run the neutral default Docker build, installed wheel checks, existing likelihood integration, this training integration and artifact retention as separate gates on native AMD64 and ARM64.

The first local work-only accepted receipt remains under the sibling `project-integration/actual-compose-04` and uses a different two-wheel draft snapshot. It is evidence for the design, not a qualification of this integrated one-wheel candidate. Hosted, real multi-machine, GPU, larger world sizes, broad model classes and numerical convergence claims remain outside this case set.
