# torch-028: Restartable training, optimizer state and RNG evidence

## Level and prerequisites

Advanced; approximately 135 minutes. Direct prerequisites: `torch-027`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Restartable training requires the state that determines the next update, not merely weights that reproduce the current prediction. The central investigation is concrete: Take two Adam updates of a zero-weight linear model onx 1, 2 and y 2 x. The finish condition is optimizer step 2 and positive weight. directory absent; no distributed-loader claim. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

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

Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **Deep Learning with PyTorch: tensors to reliable model releases** subject and select `torch-028`. Use its `llm-torch-cpu` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `courses/deep-learning-pytorch/lessons/torch-028.py` under `.learning/expansion/torch-028/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

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

The RNG timeline has an easily missed construction step. torch.manual_seed(7) sets an initial stream. Creating nn.Linear consumes initialization randomness even though the code subsequently overwrites its weight with zero. The two initial updates use zero noise and no further random draws. The saved RNG state therefore represents a particular position after construction, not simply the number 7. The uninterrupted path next draws a three-value probe, then a2×1 noise tensor, and then updates.

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

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: optimizer step 2 and positive weight. directory absent; no distributed-loader claim. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Create nontrivial training state.** Take two Adam updates of a zero-weight linear model onx 1, 2 and y 2 x.
   **Expected:** optimizer step 2 and positive weight.
   **Verify:** Save the assertion results for exercise 1, including optimizer step 2 and positive weight.

2. **Save the complete local contract.** Write model, optimizer, RNG and data_position2 into an owned temporary checkpoint.
   **Expected:** file exists and metadata position 2.
   **Verify:** Save the assertion results for exercise 2, including file exists and metadata position 2.

3. **Record uninterrupted continuation.** Draw three random values, then a small target perturbation, and perform the third update.
   **Expected:** finite weight, step 3, and saved three-value random probe.
   **Verify:** Save the assertion results for exercise 3, including finite weight, step 3, and saved three-value random probe.

4. **Restore in a fresh interpreter.** Recreate model and Adam, restore all state, repeat the same draws and update.
   **Expected:** probe matches and next weight agrees within 1e-6; position 3.
   **Verify:** Save the assertion results for exercise 4, including probe matches and next weight agrees within 1e-6; position 3.

5. **Expose a weights-only restart.** Restore only the saved model into fresh Adam and take the same third batch update.
   **Expected:** next weight differs from full-state continuation.
   **Verify:** Save the assertion results for exercise 5, including next weight differs from full-state continuation.

6. **Verify cleanup and bounded claims.** Remove the owned checkpoint directory and report that the literal CPU batch contract was tested.
   **Expected:** directory absent; no distributed-loader claim.
   **Verify:** Save the assertion results for exercise 6, including directory absent; no distributed-loader claim.

## Common pitfalls and diagnosis

If immediate predictions match but the next weight diverges, compare Adam step/moments, group options and the exact next input before changing tolerances. If the random probe differs, inspect restore order and every intervening draw, including model construction. If the probe matches but the update does not, inspect optimizer reconstruction and loss configuration.

If a supposed saved snapshot changes in memory, check state_dict aliasing. If the data-position marker is correct but a real pipeline repeats or skips records, the marker did not restore its loader/sampler contract. Treat child timeout, nonzero exit or incompatible tensor shapes as a failed continuation with retained diagnostics. Do not describe a completed-file test as crash-safe publication or a one-CPU-generator test as distributed reproducibility.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Training checkpoint, RNG state, Data position using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-027` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 serialization](https://docs.pytorch.org/docs/2.9/notes/serialization.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

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
