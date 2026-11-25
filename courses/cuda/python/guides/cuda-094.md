# cuda-094: Reproducible, restartable GPU training

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-069`, `cuda-087`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- List checkpoint fields.
- Compute momentum continuation.
- Diagnose weights-only restart.
- Record sampler position.
- Choose a safe save boundary.
- Define cross-hardware tolerance.

## Mechanism and vocabulary

A training checkpoint is a state contract, not simply model weights. It may include optimizer moments, learning-rate schedule, gradient scaler, RNG states, sample position and preprocessing metadata. Saving at an update boundary avoids ambiguous partially accumulated gradients unless the format explicitly handles them. The storage must outlive the disposable execution process.

PyTorch state dictionaries and TensorFlow checkpoints track state differently; both need restore tests. Compare a short uninterrupted run with an interrupted/restored run under a declared tolerance and deterministic configuration. GPU algorithm choices and hardware changes can limit bitwise equality. A model checkpoint restores numerical training state, not an arbitrary live GPU context or in-flight stream.



### Key terms

- **Training checkpoint:** Saved state sufficient to resume training identically, which includes much more than model weights.
- **Optimizer moments:** Per-parameter running averages stored by optimizers such as Adam that must be restored with the weights.
- **RNG state:** Saved generator states for each library and device that make dropout and shuffling continue the same sequence.
- **Sampler position:** The epoch and index in the data order, which prevents repeating or skipping batches after resume.
- **Update boundary:** A point between complete optimizer steps where state is consistent and safe to save.

## Worked examples

### Worked example 1

Momentum update \(v=0.9v+g\) stores v as well as weight w. Restoring w but resetting v changes the next update even with the same gradient.

### Worked example 2

A checkpoint after batch 2 should resume with batch 3. Replaying batch 2 or skipping batch 3 changes data exposure and invalidates a claimed exact continuation.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-094_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-094_cpu.py
```

```python
w, v = 1.0, 0.5
checkpoint = {"w": w, "v": v, "next_batch": 3}
grad = 0.2
continued = checkpoint["w"] - 0.1 * (0.9 * checkpoint["v"] + grad)
weights_only = w - 0.1 * grad
assert abs(continued - 0.935) < 1e-12
assert continued != weights_only
print("CPU restart model:", continued, weights_only)
```

**Expected observation:** Correct restored update 0.935 differs from weights-only 0.98.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `w` | `1.0` |
| `v` | `0.5` |
| `checkpoint` | `{'w': 1.0, 'v': 0.5, 'next_batch': 3}` |
| `grad` | `0.2` |
| `continued` | `0.935` |
| `weights_only` | `0.98` |

## Equal framework lanes

### PyTorch

Checkpoint model and optimizer state, scaler and RNG state as applicable. The included in-memory momentum restore proves the numerical state contract; it is not durable storage or a process snapshot.

### TensorFlow

Use tracked variables and tf.train.Checkpoint for a durable prepared project. The included in-memory weight/velocity restore isolates the mathematical contract before file and optimizer-trackable integration.

Lane rules: [framework labs](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Executable framework practice

Run the **PyTorch** and **TensorFlow** variants on CPU first; [lab rules](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-094.md) before opening hints.

### Exercise 1: List checkpoint fields

**Trap to avoid:** Saving only `model.state_dict()` because that is what inference needs leaves out optimizer and sampler state, which training needs.

### Exercise 2: Compute momentum continuation

**Trap to avoid:** Recomputing velocity from the current gradient alone, `v = g`, gives `1.0 - 0.1*0.2 = 0.98`, the weights-only value, which ignores accumulated history.

### Exercise 3: Diagnose weights-only restart

**Trap to avoid:** Treating the difference as random noise from reloading misses that it is deterministic: the same restart always produces the same wrong value.

### Exercise 4: Record sampler position

**Trap to avoid:** Restarting the epoch from the beginning replays batches 1 and 2, which double counts them, while skipping to a new shuffle may omit batch 3 entirely.

### Exercise 5: Choose a safe save boundary

**Trap to avoid:** Saving from a signal handler at an arbitrary moment can capture a half-updated state.

### Exercise 6: Define cross-hardware tolerance

**Trap to avoid:** Requiring byte-identical weights across hardware leads to false failures that obscure real restart bugs.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. List every quantity the next optimizer step reads, not only the weights.
2. Apply the velocity update with the saved velocity, then update the weight.
3. Repeat the step with the velocity reset to zero and compare the two new weights.
4. Ask which batch must come next after restore, and what state lets the sampler produce it.
5. Ask what is ambiguous about saving in the middle of gradient accumulation.
6. Decide how close two runs on different hardware must be, and write that tolerance down.

## Common mistakes and self-check

The most common mistake is checkpointing only model weights. Optimizer moments, the learning-rate schedule, the gradient scaler, random states and the sampler position all affect the next step; resetting momentum alone changes the next weight from 0.935 to 0.98 in the reference. Another mistake is expecting byte-identical results on different hardware. Fix both by saving complete state at an update boundary and testing an interrupted run against an uninterrupted one under a declared tolerance.

**Evidence limit:** The reference compares a restored momentum update with a weights-only restart in plain Python. It does not save or load a PyTorch or TensorFlow checkpoint, so format details and GPU algorithm differences remain untested.

1. Why save at an update boundary?
2. Does a checkpoint restore a running GPU context?
3. Why must checkpoint storage outlive the training process?

Answers: [self-check answers](../solutions/cuda-094_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-094: Reproducible, restartable GPU training.
Read courses/cuda/python/guides/cuda-094.md and courses/cuda/python/lessons/cuda-094.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
