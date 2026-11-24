# cuda-096: Capstone: a trustworthy GPU model report

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-088`, `cuda-089`, `cuda-090`, `cuda-092`, `cuda-094`, `cuda-095`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute the validation metric**, **design a restart comparison**, and **state pending hardware evidence** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

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

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

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

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Equal framework lanes

### PyTorch

Submit the PyTorch state and data ledger, reference loss/gradient tests, complete timing, memory observations and restart evidence. GPU-only claims need the CUDA variant on real hardware.

### TensorFlow

Submit the TensorFlow variable/optimizer and input-pipeline ledger with equally complete numerical, timing, memory and restart evidence. One framework's successful run does not qualify the other.

Choose either lane first, then compare the other using identical mathematical inputs. Framework-specific shape, mode and optimizer rules must be checked separately. Both use offline synthetic examples; no model hub or dataset download is triggered.

## Practice and transfer

### Exercise 1: Compute the validation metric

**Trap to avoid:** Reporting the training loss in place of the validation metric mixes data used for fitting with data held out for evaluation.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Write the sample ledger

**Trap to avoid:** Accepting a candidate that is twice as fast but evaluates only half the held-out examples compares different metrics.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Define a memory budget

**Trap to avoid:** Giving a single total from a monitoring tool mixes reserved and live memory. It also hides which component to shrink when the budget is exceeded, such as switching optimizers or lowering the batch.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Design a restart comparison

**Trap to avoid:** Testing only that the checkpoint loads without errors says nothing about continuation. A checkpoint missing momentum or sampler position loads cleanly and still diverges on the next step.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Choose one optimization

**Trap to avoid:** Applying a popular optimization without measuring may target a stage that is not the bottleneck. Mixed precision, for example, does little when the GPU sits idle waiting for host input.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: State pending hardware evidence

**Trap to avoid:** Leaving out the verification field lets readers assume the GPU path was tested. A later reader cannot then distinguish a validated deployment from a desk check.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Compute the validation metric".
2. Change one assumption in worked example 2 while preserving the declared contract: write the sample ledger.
3. Trace the CPU program's variables before adding hardware behavior: define a memory budget.
4. Draw producers, consumers and the exact operation boundary for the task "Design a restart comparison".
5. Separate what the small fixture establishes from what the real runtime must show: choose one optimization.
6. Write a counterexample to an overbroad claim before you state pending hardware evidence.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Compute the validation metric`. For the final claim use `State pending hardware evidence`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-096: Capstone: a trustworthy GPU model report.
Read courses/cuda/python/guides/cuda-096.md and courses/cuda/python/lessons/cuda-096.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
