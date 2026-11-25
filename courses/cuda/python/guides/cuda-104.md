# cuda-104: Capstone: an evidence-based GPU systems decision

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-085`, `cuda-092`, `cuda-096`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Write three constraints.
- Filter infeasible candidates.
- Choose a bottleneck hypothesis.
- Preserve rollback.
- Design failure tests.
- State evidence gaps.

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

Candidate A uses 8 GiB and meets a 20 ms latency target; candidate B uses 12 GiB on an 8 GiB device. B is infeasible regardless of its optimistic kernel timing.

### Worked example 2

Candidate C meets latency but reduces held-out accuracy below the required threshold. Performance and quality constraints both belong in acceptance.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-104_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-104_cpu.py
```

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

## Equal framework lanes

### PyTorch

Choose either a single-device or a separately qualified distributed/custom-op PyTorch path. Preserve an ordinary eager baseline and source-bound evidence for every claimed gain.

### TensorFlow

Choose the equivalent bounded TensorFlow path, preserve an eager baseline and report graph/placement changes. TensorFlow needs its own acceptance evidence, not a copied PyTorch benchmark.

Lane rules: [framework labs](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-104.md) before opening hints.

### Exercise 1: Write three constraints

**Trap to avoid:** Writing a single goal of maximizing speed ignores memory and quality, so the fastest candidate wins even when it cannot run on the device or produces worse answers.

### Exercise 2: Filter infeasible candidates

**Trap to avoid:** Ranking all candidates by latency first and picking B, then trying to make it fit later, wastes effort and treats a hard constraint as a preference.

### Exercise 3: Choose a bottleneck hypothesis

**Trap to avoid:** Making several optimizations at once without a hypothesis means any improvement cannot be attributed to a cause, and regressions get hidden by gains elsewhere.

### Exercise 4: Preserve rollback

**Trap to avoid:** Replacing the baseline code in place leaves no way to reproduce earlier results or revert quickly.

### Exercise 5: Design failure tests

**Trap to avoid:** Testing only valid inputs leaves error paths untested, and those paths are where GPU services typically fail in production.

### Exercise 6: State evidence gaps

**Trap to avoid:** Presenting fixture numbers such as 18 ms as measured performance claims evidence that does not exist.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Write each constraint as a number with a unit, such as a memory ceiling, a latency target and a quality floor.
2. Check memory and quality against their limits first and drop any candidate that fails either one before comparing speed.
3. Point to the part of a measured trace that shows where time goes, then pick the change that targets it.
4. Ask how you would return to the baseline tomorrow if the new version fails in use.
5. Send an unsupported shape and a request beyond the resource limit and describe the correct refusal.
6. Mark each claim as measured live, measured on the CPU only or still a hypothesis.

## Common mistakes and self-check

A common mistake is ranking candidates by kernel speed before checking feasibility. Candidate B in worked example 1 needs 12 GiB on an 8 GiB device, so its timing is irrelevant, and candidate C misses the accuracy threshold. Another mistake is adding a custom kernel or more GPUs because they sound advanced. Fix both by filtering on every stated constraint first and choosing one optimization tied to a measured bottleneck, with the unchanged baseline kept runnable for rollback.

**Misconception:** A capstone decision must recommend some optimization, or the project has failed. **Correction:** Keeping the reproducible baseline is a valid outcome when no candidate meets every constraint. The acceptance matrix should show which claims have live evidence and which remain hypotheses, so a reviewer can see why the baseline was kept.

**Evidence limit:** The reference filters three described candidates and accepts only candidate A. Its memory, latency and accuracy figures are given, not measured, so a real decision needs live evidence for each claim in the acceptance matrix.

1. Why must quality be part of acceptance?
2. Which bottlenecks can an optimization target?
3. What can CPU-only work honestly deliver?

Answers: [self-check answers](../solutions/cuda-104_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-104: Capstone: an evidence-based GPU systems decision.
Read courses/cuda/python/guides/cuda-104.md and courses/cuda/python/lessons/cuda-104.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
