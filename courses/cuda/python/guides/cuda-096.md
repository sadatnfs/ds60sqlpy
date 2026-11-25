# cuda-096: Capstone: a trustworthy GPU model report

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-088`, `cuda-089`, `cuda-090`, `cuda-092`, `cuda-094`, `cuda-095`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Compute the validation metric.
- Write the sample ledger.
- Define a memory budget.
- Design a restart comparison.
- Choose one optimization.
- State pending hardware evidence.

## Mechanism and vocabulary

Train a tiny offline regressor or classifier using either complete framework lane. Define a held-out split before tuning. Preserve the CPU baseline, the training objective and the total number of examples. A report should separate numerical agreement, learning quality, device placement, throughput, memory and restart behavior. An optimization that drops hard examples or changes effective batch size needs a new experiment label.

Use a small bounded search over one variable at a time. Retain a failed hypothesis and explain what evidence rejected it. Save the software/hardware ledger, source revision, seeds, split, timing boundary and checkpoint test. CPU-only learners can complete the mathematical and reporting sections now, while GPU timings and placement remain pending. A capstone completion marker records learning work, not a production certification.



### Key terms

- **Held-out split:** Data excluded from training and tuning and used only to estimate generalization.
- **Validation metric:** A quality measure computed on held-out data to compare runs or select checkpoints.
- **Software and hardware ledger:** A record of source revision, versions, device, seeds and split that lets another person reproduce the report.
- **Restart comparison:** Checking that a run resumed from a checkpoint matches an uninterrupted run under the same recipe.

## Worked examples

### Worked example 1

Predictions [1,2,3] against targets [1,3,2] have MSE 2/3. Record this validation metric separately from the training loss.

### Worked example 2

A candidate that runs twice as fast but evaluates only half the held-out examples cannot use the original metric denominator. Compare the same examples and preserve sample accounting.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-096_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-096_cpu.py
```

```python
predictions, targets = [1, 2, 3], [1, 3, 2]
mse = sum((p - t) ** 2 for p, t in zip(predictions, targets, strict=True)) / len(targets)
assert abs(mse - 2 / 3) < 1e-12
report = {"backend": "CPU reference", "examples": len(targets), "mse": mse, "gpu_verified": False}
assert report["examples"] == 3 and not report["gpu_verified"]
print(report)
```

**Expected observation:** Three examples, MSE 2/3, GPU verification explicitly false.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `predictions` | `[1, 2, 3]` |
| `targets` | `[1, 3, 2]` |
| `mse` | `0.6666666666666666` |

## Equal framework lanes

### PyTorch

Submit the PyTorch state and data ledger, reference loss/gradient tests, complete timing, memory observations and restart evidence. GPU-only claims need the CUDA variant on real hardware.

### TensorFlow

Submit the TensorFlow variable/optimizer and input-pipeline ledger with equally complete numerical, timing, memory and restart evidence. One framework's successful run does not qualify the other.

Lane rules: [framework labs](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-096.md) before opening hints.

### Exercise 1: Compute the validation metric

**Trap to avoid:** Reporting the training loss in place of the validation metric mixes data used for fitting with data held out for evaluation.

### Exercise 2: Write the sample ledger

**Trap to avoid:** Accepting a candidate that is twice as fast but evaluates only half the held-out examples compares different metrics.

### Exercise 3: Define a memory budget

**Trap to avoid:** Giving a single total from a monitoring tool mixes reserved and live memory. It also hides which component to shrink when the budget is exceeded, such as switching optimizers or lowering the batch.

### Exercise 4: Design a restart comparison

**Trap to avoid:** Testing only that the checkpoint loads without errors says nothing about continuation. A checkpoint missing momentum or sampler position loads cleanly and still diverges on the next step.

### Exercise 5: Choose one optimization

**Trap to avoid:** Applying a popular optimization without measuring may target a stage that is not the bottleneck. Mixed precision, for example, does little when the GPU sits idle waiting for host input.

### Exercise 6: State pending hardware evidence

**Trap to avoid:** Leaving out the verification field lets readers assume the GPU path was tested. A later reader cannot then distinguish a validated deployment from a desk check.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Square the error for each prediction and target pair, then average.
2. Count examples assigned to training and validation and how many each step consumed.
3. List weights, optimizer state, activations and allocator reserve as separate entries.
4. Compare an uninterrupted run with one that stops, restores and continues over the same steps.
5. Choose the change that targets the bottleneck your measurements identified, and only that one.
6. Write which results came from the CPU and which GPU checks have not run yet.

## Common mistakes and self-check

A common capstone mistake is reporting a faster candidate that quietly evaluates fewer held-out examples or changes the effective batch size. Its metric is no longer comparable with the baseline. Another mistake is merging CPU results and pending GPU evidence into one claim. Fix both by preserving the split and sample accounting, labeling any change in objective or examples as a new experiment, and marking CPU verification and GPU verification as separate fields in the report.

**Evidence limit:** The reference checks three examples with MSE 2/3 and records GPU verification as false. It shows the report structure, not learning quality, device placement or throughput, which require running a framework lane on a supported device.

1. Why define the held-out split before tuning?
2. Why keep a failed hypothesis in the report?
3. What does a capstone completion marker certify?

Answers: [self-check answers](../solutions/cuda-096_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-096: Capstone: a trustworthy GPU model report.
Read courses/cuda/python/guides/cuda-096.md and courses/cuda/python/lessons/cuda-096.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
