# torch-028: Restartable training, optimizer state and RNG evidence

## Level and prerequisites

Advanced; approximately 135 minutes. Direct prerequisites: `torch-027`.

## Learning objectives

Save and restore every state that determines the next training update, and show that weights alone do not resume training.

Central investigation: Take two Adam updates, checkpoint model, optimizer, RNG and data position, then continue in place and in a fresh interpreter.

Finish condition: The checkpoint holds Adam step 2 and data position 2, the fresh-process continuation reproduces the random probe and the next weight within 1e-6, a weights-only restart diverges, and the owned directory is removed.

## Purpose and mental model

Restartable training requires the state that determines the next update, not merely weights that reproduce the current prediction. Adam stores moment estimates and a step counter. Random draws can affect the next batch or target perturbation. Data position determines which observation comes next. A checkpoint contract must name all of these components and define what is fixed or restored. A weights-only restart can match immediate predictions while taking a different subsequent step.

This lesson saves a small linear model, Adam state, CPU RNG state and an explicit data-position counter after two updates. It compares an uninterrupted next draw and update with a fresh interpreter restoring the trusted local checkpoint. The literal batch is fixed; this does not claim to restore a multiprocessing DataLoader or a distributed sampler. Temporary artifacts are owned and removed by the lesson. Float32 comparisons use a declared tolerance rather than promising cross-platform bitwise identity.

## Design decisions and when to use this method

Choose a checkpoint boundary by asking what determines the next update. An inference artifact may need only the predictor's parameters, buffers and construction/preprocessing contract. A training continuation also needs optimizer history and every active source of randomness, scheduling and data position. Save only the components actually used, while stating which are fixed or absent.

Use a fresh-process next-step comparison to test reconstruction. Match the next batch and stochastic draws before comparing updated weights. The lesson deliberately uses one CPU generator and a literal batch; restoring workers, distributed sampling or partially consumed external streams remains a separate contract.

## Paired TensorFlow comparison

Compare [tf-028](../../deep-learning-tensorflow/guides/tf-028.md) after deriving the shared numerical contract.

TensorFlow Checkpoints track model and optimizer objects; PyTorch commonly saves explicit state dictionaries. Both need optimizer history and any random/data state affecting the next step. The paired TensorFlow example's resource ownership and fresh-process checks serve the same evidence purpose.

## Vocabulary and concepts

**Training checkpoint:** State sufficient for a declared continuation contract.

**RNG state:** The position of a pseudorandom generator used by future operations.

**Data position:** The declared next point in the training input sequence.

**Next-step parity:** Agreement after one identical restored and uninterrupted update.

## How to run this lesson

Run `torch-028` on the `llm-torch-cpu` worker ([launch, save and tolerance rules](../STUDY-GUIDE.md#launch-a-lesson)).

Examples B and C reuse `model`, `optimizer`, `step` and `parameter` from earlier blocks; run all three in order.

## Syntax anatomy and reasoning sequence

Save a dictionary of model.state_dict, optimizer.state_dict, torch.get_rng_state and simple metadata. Reconstruct fresh objects before load_state_dict, and restore RNG after object construction so initialization draws do not advance the restored stream. torch.load uses weights_only=True for this trusted tensor-and-primitive checkpoint. The child program is dedented, compiled before launch, bounded by a timeout, and includes stderr in a failure.

## Reconstruct the next state transition, not just the current prediction

Training state is the input to a transition. A useful inventory separates components by how they influence the next step:

| Component | Role in this fixture | What weights alone omit |
| --- | --- | --- |
| model tensors | current scalar predictor | current value if absent |
| Adam moments and step | update direction/normalization | history-dependent next update |
| optimizer group options | rate and optimizer configuration | the intended update policy |
| CPU RNG state | next probe and target-noise draws | position in the random stream |
| data_position=2 | declared completed-update marker | progress metadata |
| literal x and target rule | fixed next-batch construction | a reproducible input contract |

Adam maintains \(m_t=\beta_1m_{t-1}+(1-\beta_1)g_t\) and \(v_t=\beta_2v_{t-1}+(1-\beta_2)g_t^2\), then uses step-dependent bias correction and an epsilon-stabilized normalized update. Two models with identical weights but different m, v, t need not take the same next step. Saving after two real updates makes those histories nontrivial; checkpointing before any update would leave a much weaker test.

The weights-only negative control is deliberately given the same next noise tensor as the uninterrupted run. Its different result therefore isolates missing optimizer history rather than simultaneously changing the batch and the optimizer. It is a stronger experiment than comparing two restarted jobs whose data order and RNG streams are also unknown. The paired TensorFlow chapter tests the same reconstruction principle, although its scalar objective and optimizer rate differ from this PyTorch fixture; their literal weights are not a cross-framework equality oracle.

The RNG timeline has an easily missed construction step. torch.manual_seed(7) sets an initial stream. Creating nn.Linear consumes initialization randomness even though the code subsequently overwrites its weight with zero. The two initial updates use zero noise and no further random draws. The saved RNG state therefore represents a particular position after construction, not simply the number 7. The uninterrupted path next draws a three-value probe, then a 2×1 noise tensor, and then updates.

The child reconstructs the model and optimizer, loads their saved state, and only then restores torch RNG state. Restoring before constructing Linear would let initialization consume a draw from the restored stream. Setting the seed again would return to the stream's beginning instead of its saved position. Matching the three-value probe checks this ordering directly before the weight comparison tests the next noisy update. [PyTorch 2.9 reproducibility guidance](https://docs.pytorch.org/docs/2.9/notes/randomness.html).

Other randomness is absent from this particular continuation. Python random, NumPy Generator objects, DataLoader generators, worker processes and accelerator generators would need their own explicit treatment if used. A global torch seed does not automatically serialize every library's current generator state. Likewise, a data_position integer does not restore a real iterator here: the next batch is always constructed from literal x=[1, 2]. Incrementing the marker to three proves the stated bookkeeping, not worker-prefetch or distributed-sampler recovery.

State dictionaries also have ownership semantics. model.state_dict() provides references to model state tensors; holding that mapping in memory is not an immutable copy while later updates mutate the model. The example immediately serializes the mapping before continuation, so the file preserves that point. For an in-memory before/after comparison, clone the values; for a restore comparison, reload the completed saved file rather than assuming a still-live dictionary remained unchanged.

Reconstruct the same architecture and optimizer parameter-group structure before loading. Optimizer state is associated with the supplied parameter groups and their ordering; similar tensor shapes do not prove the state was attached to the intended semantic parameter after an architecture edit. A scheduler, gradient scaler, EMA model or accumulated-but-not-yet-stepped gradients would add more continuation state when present. None is silently claimed restored by this small Adam example.

weights_only=True restricts the object forms used by the local tensor-and-primitive checkpoint loader. It is not a publisher-authentication mechanism or a complete resource/shape validation policy for arbitrary outside files. map_location='cpu' establishes the intended device boundary. The child process uses the existing interpreter, has a timeout and exposes stderr on failure, so a failed reconstruction is not replaced by expected output text.

Finally, the tested boundary is a completed torch.save followed by a fresh-process load. It does not inject a crash halfway through writing or prove power-loss durability. A persistent production checkpoint needs its own staged-publication, integrity and retention procedure. The local directory is owned and disposable, and the successful test removes it. Next-step parity is valuable evidence for this exact transition and environment, not a promise of bitwise agreement across versions, hardware or nondeterministic pipelines.

## Worked example / walkthrough

### Example A: Create nontrivial training state

Saving before any updates would not test nonzero optimizer moments. Two steps create history that a fresh optimizer lacks.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
import tempfile, json, subprocess, sys, textwrap
from pathlib import Path


def make_state():
    model = nn.Linear(1, 1, bias=False)
    with torch.no_grad():
        model.weight.zero_()
    return model, torch.optim.Adam(model.parameters(), lr=0.05)


def step(model, optimizer, noise):
    x = torch.tensor([[1.0], [2.0]])
    target = 2 * x + noise
    optimizer.zero_grad(set_to_none=True)
    (model(x) - target).square().mean().backward()
    optimizer.step()


torch.manual_seed(7)
model, optimizer = make_state()
for _ in range(2):
    step(model, optimizer, torch.zeros((2, 1)))
parameter = next(model.parameters())
assert optimizer.state[parameter]["step"].item() == 2 and parameter.item() > 0
```

**Expected:** optimizer step 2 and positive weight.

### Example B: Save the complete local contract

The state dictionary values are serialized at this point. The checkpoint is local and trusted; the example does not load arbitrary external pick led objects.

```python
temporary = tempfile.TemporaryDirectory()
folder = Path(temporary.name)
path = folder / "checkpoint.pt"
checkpoint = {
    "model": model.state_dict(),
    "optimizer": optimizer.state_dict(),
    "rng": torch.get_rng_state(),
    "data_position": 2,
}
torch.save(checkpoint, path)
assert path.is_file() and checkpoint["data_position"] == 2
```

**Expected:** file exists and metadata position 2.

### Example C: Record uninterrupted continuation

The order of random draws is part of the continuation contract. Restoring only the seed without the consumed generator state would not reproduce this point.

```python
probe = torch.rand(3)
noise = torch.rand((2, 1)) * 0.01
step(model, optimizer, noise)
expected = parameter.item()
assert (
    torch.isfinite(probe).all()
    and optimizer.state[parameter]["step"].item() == 3
    and np.isfinite(expected)
)
```

**Expected:** finite weight, step 3, and saved three-value random probe.

## Prediction before your attempt

Derive Example A again with its **Expected** line covered: Create nontrivial training state. Predict exercise 6, Verify cleanup and bounded claims, from its prompt alone: Remove the owned checkpoint directory and report that the literal CPU batch contract was tested. Then explain why this finish condition holds: The checkpoint holds Adam step 2 and data position 2, the fresh-process continuation reproduces the random probe and the next weight within 1e-6, a weights-only restart diverges, and the owned directory is removed. Keep each prediction beside the observed value.

## Exercises

1. **Predict Adam's first step.** From a fresh make_state(), take one step with zero noise and compare the weight with the learning rate 0.05.
   **Expected:** weight 0.05 within 1e-6.
   **Verify:** In a fresh process, the exercise checks confirm `fresh_model.weight.item()` matches `0.05` within 1e-06.

2. **Inspect the new optimizer state.** List the state entries Adam stores for that parameter after one step.
   **Expected:** keys step, exp_avg and exp_avg_sq; step equals 1.
   **Verify:** In a fresh process, the exercise checks confirm `set(fresh_adam.state[fresh_param]) == {'step', 'exp_avg', 'exp_avg_sq'}` and `fresh_adam.state[fresh_param]['step'].item() == 1`.

3. **Replay a saved random state.** Save torch.get_rng_state(), draw three values, restore the state and draw again.
   **Expected:** the two draws are identical.
   **Verify:** In a fresh process, the exercise checks confirm `torch.equal(torch.rand(3), first_draw)`.

4. **Restore in a fresh interpreter.** Recreate model and Adam, restore all state, repeat the same draws and update.
   **Expected:** probe matches and next weight agrees within 1e-6; position 3.
   **Verify:** In a fresh process, the exercise checks confirm `not (result.returncode)`, `restored['probe']` matches `probe.tolist()` exactly, `restored['weight']` matches `expected` within 1e-06 and `restored['position'] == 3`.

5. **Expose a weights-only restart.** Restore only the saved model into fresh Adam and take the same third batch update.
   **Expected:** next weight differs from full-state continuation.
   **Verify:** In a fresh process, the exercise checks confirm `abs(weights_only.weight.item() - expected) > 1e-06`.

6. **Verify cleanup and bounded claims.** Remove the owned checkpoint directory and report that the literal CPU batch contract was tested.
   **Expected:** directory absent; no distributed-loader claim.
   **Verify:** In a fresh process, the exercise checks confirm `not folder.exists()`, `receipt['cpu_next_step_checked']` and `not receipt['distributed_restart_verified']`.

## Common pitfalls and diagnosis

If immediate predictions match but the next weight diverges, compare Adam step/moments, group options and the exact next input before changing tolerances. If the random probe differs, inspect restore order and every intervening draw, including model construction. If the probe matches but the update does not, inspect optimizer reconstruction and loss configuration.

If a supposed saved snapshot changes in memory, check state_dict aliasing. If the data-position marker is correct but a real pipeline repeats or skips records, the marker did not restore its loader/sampler contract. Treat child timeout, nonzero exit or incompatible tensor shapes as a failed continuation with retained diagnostics. Do not describe a completed-file test as crash-safe publication or a one-CPU-generator test as distributed reproducibility.

## Progressive hints

Hint 1: Example B (Save the complete local contract) alters one assumption of Example A (Create nontrivial training state). Hint 2: exercise 4, Restore in a fresh interpreter, should end at probe matches and next weight agrees within 1e-6; position 3. Work backward from it. Hint 3: exercise 5, Expose a weights-only restart, changes one input; predict which value moves first.

## Self-check and retrieval

Close the worked examples and rebuild Example C, Record uninterrupted continuation, from its inputs alone. Predict whether exercise 3, Replay a saved random state, survives one changed input. Then explain Training checkpoint, RNG state, Data position in terms of that fixture; say which claims the code guarantees and which need new observations.

## Next step

If Example A (Create nontrivial training state) cannot be rebuilt without help, revisit `torch-027` first. `torch-029` (Stable objectives, precision and mixed-precision boundaries) builds directly on this lesson.

## Sources and verification status

API and mechanism reference: [PyTorch 2.9 serialization](https://docs.pytorch.org/docs/2.9/notes/serialization.html), reviewed 2026-10-22 for the Training checkpoint, RNG state, Data position behavior these fixtures check ([verification status](../STUDY-GUIDE.md#sources-and-verification-status)).

## Interview reasoning with worked answers

**Why restore RNG after constructing the model?**

Construction may consume random draws for initialization. Restoring afterward returns the generator to the saved point instead of advancing it before the tested continuation.

**Is a seed equivalent to generator state?**

No. A seed identifies an initial stream; state identifies the current position after prior draws. A restart needs the state or an exact replay of every earlier draw.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-028, Restartable training, optimizer state and RNG evidence.
Read courses/deep-learning-pytorch/guides/torch-028.md and courses/deep-learning-pytorch/lessons/torch-028.py. Direct prerequisites: `torch-027`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
