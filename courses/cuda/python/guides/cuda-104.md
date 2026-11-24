# cuda-104: Capstone: an evidence-based GPU systems decision

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-085`, `cuda-092`, `cuda-096`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **write three constraints**, **preserve rollback**, and **state evidence gaps** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A systems decision balances correctness, model quality, latency, throughput, memory, cost and maintainability. Start with explicit constraints and a reproducible baseline. Choose an optimization tied to a measured bottleneck: input preparation, transfer, arithmetic, memory traffic or communication. A custom kernel and multiple GPUs are optional solutions, not achievements that must be forced into every project.

Retain source, environment, data recipe, checkpoint and rollback instructions. Report distributions and failure behavior, including unsupported shapes and resource limits. An acceptance matrix should show which claims have live evidence and which are still hypotheses. CPU-only work can produce a valuable model and decision report while honestly leaving GPU execution and deployment qualification open.



### Key terms

- **Explicit constraint:** A stated limit on correctness, quality, latency, memory, cost or maintainability that a decision must respect.
- **Bottleneck hypothesis:** A testable claim about which stage limits performance, stated before code changes.
- **Rollback instructions:** A recorded way to return to the last known good configuration if a change fails.
- **Acceptance matrix:** A table showing which claims have live evidence and which are still hypotheses.

## Worked examples

### Worked example 1

CandidateA uses 8 GiB and meets a 20 ms latency target; candidate B uses 12 GiB on an 8 GiB device. B is infeasible regardless of its optimistic kernel timing.

### Worked example 2

CandidateC meets latency but reduces held-out accuracy below the required threshold. Performance and quality constraints both belong in acceptance.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
candidates = [
    {"name": "A", "memory": 8, "latency": 18, "quality": 0.95},
    {"name": "B", "memory": 12, "latency": 10, "quality": 0.96},
    {"name": "C", "memory": 6, "latency": 12, "quality": 0.80},
]
valid = [
    c["name"] for c in candidates if c["memory"] <= 8 and c["latency"] <= 20 and c["quality"] >= 0.9
]
assert valid == ["A"]
print("CPU decision fixture:", valid)
```

**Expected observation:** Only candidate A satisfies all three constraints.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `valid` | `['A']` |

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Equal framework lanes

### PyTorch

Choose either a single-device or a separately qualified distributed/custom-op PyTorch path. Preserve an ordinary eager baseline and source-bound evidence for every claimed gain.

### TensorFlow

Choose the equivalent bounded TensorFlow path, preserve an eager baseline and report graph/placement changes. TensorFlow needs its own acceptance evidence, not a copied PyTorch benchmark.

Choose either lane first, then compare the other using identical mathematical inputs. Framework-specific shape, mode and optimizer rules must be checked separately. Both use offline synthetic examples; no model hub or dataset download is triggered.

## Practice and transfer

### Exercise 1: Write three constraints

**Trap to avoid:** Writing a single goal of maximizing speed ignores memory and quality, so the fastest candidate wins even when it cannot run on the device or produces worse answers.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Filter infeasible candidates

**Trap to avoid:** Ranking all candidates by latency first and picking B, then trying to make it fit later, wastes effort and treats a hard constraint as a preference.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Choose a bottleneck hypothesis

**Trap to avoid:** Making several optimizations at once without a hypothesis means any improvement cannot be attributed to a cause, and regressions get hidden by gains elsewhere.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Preserve rollback

**Trap to avoid:** Replacing the baseline code in place leaves no way to reproduce earlier results or revert quickly.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Design failure tests

**Trap to avoid:** Testing only valid inputs leaves error paths untested, and those paths are where GPU services typically fail in production.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: State evidence gaps

**Trap to avoid:** Presenting fixture numbers such as 18 ms as measured performance claims evidence that does not exist.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Write three constraints".
2. Change one assumption in worked example 2 while preserving the declared contract: filter infeasible candidates.
3. Trace the CPU program's variables before adding hardware behavior: choose a bottleneck hypothesis.
4. Draw producers, consumers and the exact operation boundary for the task "Preserve rollback".
5. Separate what the small fixture establishes from what the real runtime must show: design failure tests.
6. Write a counterexample to an overbroad claim before you state evidence gaps.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Write three constraints`. For the final claim use `State evidence gaps`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

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
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-104: Capstone: an evidence-based GPU systems decision.
Read courses/cuda/python/guides/cuda-104.md and courses/cuda/python/lessons/cuda-104.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
