# torch-028: Restartable training, optimizer state and RNG evidence

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Advanced; approximately 135 minutes. Direct prerequisites: `torch-027`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Restartable training requires the state that determines the next update, not merely weights that reproduce the current prediction. The central investigation is concrete: Take two Adam updates of a zero-weight linear model onx1, 2 andy2 x. The finish condition is optimizer step2 and positive weight. directory absent; no distributed-loader claim. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Restartable training requires the state that determines the next update, not merely weights that reproduce the current prediction. Adam stores moment estimates and a step counter. Random draws can affect the next batch or target perturbation. Data position determines which observation comes next. A checkpoint contract must name all of these components and define what is fixed or restored. A weights-only restart can match immediate predictions while taking a different subsequent step.

This lesson saves a small linear model, Adam state, CPU RNG state and an explicit data-position counter after two updates. It compares an uninterrupted next draw and update with a fresh interpreter restoring the trusted local checkpoint. The literal batch is fixed; this does not claim to restore a multiprocessing DataLoader or a distributed sampler. Temporary artifacts are owned and removed by the lesson. Float32 comparisons use a declared tolerance rather than promising cross-platform bitwise identity.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-028](../../deep-learning-tensorflow/guides/tf-028.md) after deriving the shared numerical contract.

TensorFlow Checkpoints track model and optimizer objects; PyTorch commonly saves explicit state dictionaries. Both need optimizer history and any random/data state affecting the next step. The paired TensorFlow example's resource ownership and fresh-process checks serve the same evidence purpose.

## Vocabulary and concepts

**Training checkpoint:** State sufficient for a declared continuation contract.

**RNG state:** The position of a pseudorandom generator used by future operations.

**Data position:** The declared next point in the training input sequence.

**Next-step parity:** Agreement after one identical restored and uninterrupted update.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-028/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-028.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-028.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Save a dictionary of model.state_dict, optimizer.state_dict, torch.get_rng_state and simple metadata. Reconstruct fresh objects before load_state_dict, and restore RNG after object construction so initialization draws do not advance the restored stream. torch.load uses weights_only=True for this trusted tensor-and-primitive checkpoint. The child program is dedented, compiled before launch, bounded by a timeout, and includes stderr in a failure.

## Worked example / walkthrough

### Example A: Create nontrivial training state

Saving before any updates would not test nonzero optimizer moments. Two steps create history that a fresh optimizer lacks.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
import tempfile,json,subprocess,sys,textwrap
from pathlib import Path
def make_state():
    model=nn.Linear(1,1,bias=False)
    with torch.no_grad(): model.weight.zero_()
    return model,torch.optim.Adam(model.parameters(),lr=.05)
def step(model,optimizer,noise):
    x=torch.tensor([[1.],[2.]]); target=2*x+noise
    optimizer.zero_grad(set_to_none=True); (model(x)-target).square().mean().backward(); optimizer.step()
torch.manual_seed(7); model,optimizer=make_state()
for _ in range(2): step(model,optimizer,torch.zeros((2,1)))
parameter=next(model.parameters()); assert optimizer.state[parameter]['step'].item()==2 and parameter.item()>0
```

**Expected:** optimizer step2 and positive weight.

### Example B: Save the complete local contract

The state dictionary values are serialized at this point. The checkpoint is local and trusted; the example does not load arbitrary external pick led objects.

```python
temporary=tempfile.TemporaryDirectory(); folder=Path(temporary.name); path=folder/'checkpoint.pt'
checkpoint={'model':model.state_dict(),'optimizer':optimizer.state_dict(),'rng':torch.get_rng_state(),'data_position':2}
torch.save(checkpoint,path); assert path.is_file() and checkpoint['data_position']==2
```

**Expected:** file exists and metadata position2.

### Example C: Record uninterrupted continuation

The order of random draws is part of the continuation contract. Restoring only the seed without the consumed generator state would not reproduce this point.

```python
probe=torch.rand(3); noise=torch.rand((2,1))*.01; step(model,optimizer,noise); expected=parameter.item()
assert torch.isfinite(probe).all() and optimizer.state[parameter]['step'].item()==3 and np.isfinite(expected)
```

**Expected:** finite weight, step3, and saved three-value random probe.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: optimizer step2 and positive weight. directory absent; no distributed-loader claim. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Create nontrivial training state.** Take two Adam updates of a zero-weight linear model onx1, 2 andy2 x.
   **Expected:** optimizer step2 and positive weight.
   **Verify:** Save the assertion results for exercise 1, including optimizer step2 and positive weight.

2. **Save the complete local contract.** Write model, optimizer, RNG and data_position2 into an owned temporary checkpoint.
   **Expected:** file exists and metadata position2.
   **Verify:** Save the assertion results for exercise 2, including file exists and metadata position2.

3. **Record uninterrupted continuation.** Draw three random values, then a small target perturbation, and perform the third update.
   **Expected:** finite weight, step3, and saved three-value random probe.
   **Verify:** Save the assertion results for exercise 3, including finite weight, step3, and saved three-value random probe.

4. **Restore in a fresh interpreter.** Recreate model and Adam, restore all state, repeat the same draws and update.
   **Expected:** probe matches and next weight agrees within1e-6; position3.
   **Verify:** Save the assertion results for exercise 4, including probe matches and next weight agrees within1e-6; position3.

5. **Expose a weights-only restart.** Restore only the saved model into fresh Adam and take the same third batch update.
   **Expected:** next weight differs from full-state continuation.
   **Verify:** Save the assertion results for exercise 5, including next weight differs from full-state continuation.

6. **Verify cleanup and bounded claims.** Remove the owned checkpoint directory and report that the literal CPU batch contract was tested.
   **Expected:** directory absent; no distributed-loader claim.
   **Verify:** Save the assertion results for exercise 6, including directory absent; no distributed-loader claim.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Training checkpoint, RNG state, Data position using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-027` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 serialization](https://docs.pytorch.org/docs/2.9/notes/serialization.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why restore RNG after constructing the model?**

Construction may consume random draws for initialization. Restoring afterward returns the generator to the saved point instead of advancing it before the tested continuation.

**Is a seed equivalent to generator state?**

No. A seed identifies an initial stream; state identifies the current position after prior draws. A restart needs the state or an exact replay of every earlier draw.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-028, Restartable training, optimizer state and RNG evidence.
Read courses/deep-learning-pytorch/guides/torch-028.md and courses/deep-learning-pytorch/lessons/torch-028.py. Direct prerequisites: `torch-027`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
