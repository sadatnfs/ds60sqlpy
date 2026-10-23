# torch-036: Capstone: release a small reproducible PyTorch model

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Advanced; approximately 240 minutes. Direct prerequisites: `torch-035`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A reproducible model release is a bundle of state, schema, data identity, execution evidence and limitations. The central investigation is concrete: Use train x1, 2, 3 and holdout4, 5 with target2 x and disjoint IDs. The finish condition is 3 training and2 holdout records. local checks True; production no-go; directory absent. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A reproducible model release is a bundle of state, schema, data identity, execution evidence and limitations. A valid artifact must reconstruct the intended model and produce checked predictions in a fresh process. A hash detects changed bytes but does not prove that the bytes contain a useful or honestly evaluated model. Release gates should fail on missing or incorrect evidence rather than silently treat unknown checks as passed.

This capstone trains a small scalar regressor under a fixed budget, saves its state with a feature/dtype schema and split manifest, and executes a fresh-process inference check. It then deliberately corrupts the declared state hash and proves that the loader rejects the bundle before using it. The temporary release is a local teaching artifact, not a deployment. The final record distinguishes local contract acceptance from unestablished production reliability and retains a rollback identity.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-036](../../deep-learning-tensorflow/guides/tf-036.md) after deriving the shared numerical contract.

The paired TensorFlow release uses the same evidence categories but different artifact formats. PyTorch state_dict requires explicit architecture reconstruction, and exported programs add their own constraints. Both need integrity, schema, fresh-process and negative-gate checks; neither framework makes a small holdout a production guarantee.

## Vocabulary and concepts

**Release bundle:** The model state, semantic schema, lineage and evidence needed for reconstruction.

**Integrity gate:** A check that artifact bytes match their recorded identity.

**Fresh-process inference:** Prediction after reconstruction without live parent objects.

**Rollback identity:** A retained previous artifact reference used in a recovery decision.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-036/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-036.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-036.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Train ann.Linear(1, 1, bias=False) on literal float64 points using fixed SGD updates. Serialize state_dict, canonical JSON schema and split IDs into an owned Temporary Directory. Record SHA256 of the weight file. The child verifies the hash and schema before constructing the module and loading weights_only=True. Bound the subprocess, include stderr on unexpected failure, and remove only the owned temporary directory.

## Worked example / walkthrough

### Example A: Freeze the scalar experiment

The data identity is fixed before training. The tiny holdout is useful for local mechanics but not sufficient for a broad quality claim.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
import tempfile,json,subprocess,sys,textwrap,hashlib
from pathlib import Path

x=torch.tensor([[1.],[2.],[3.]],dtype=torch.float64); y=2*x; held=torch.tensor([[4.],[5.]],dtype=torch.float64)
split={'train':['a','b','c'],'test':['d','e']}; assert not set(split['train'])&set(split['test']) and len(split['test'])==2
```

**Expected:** 3 training and2 holdout records.

### Example B: Train within a declared budget

The budget is not extended after seeing the holdout. The baseline predicts training mean target4, so gives errors16 and36 on the two test rows.

```python
model=nn.Linear(1,1,bias=False,dtype=torch.float64)
with torch.no_grad(): model.weight.zero_()
optimizer=torch.optim.SGD(model.parameters(),lr=.01)
for _ in range(30):
    optimizer.zero_grad(set_to_none=True); (model(x)-y).square().mean().backward(); optimizer.step()
model.eval()
with torch.no_grad(): expected=model(held); error=(expected-2*held).square().mean().item()
assert torch.isfinite(model.weight).all() and error<26
```

**Expected:** finite weights; holdout error below constant training-mean baseline26.

### Example C: Build the owned release bundle

The hash binds the manifest to the saved bytes. The feature order and dtype provide semantic information that a state dictionary alone cannot explain.

```python
temporary=tempfile.TemporaryDirectory(); folder=Path(temporary.name); weights=folder/'weights.pt'; torch.save(model.state_dict(),weights)
manifest={'schema':{'features':['x'],'dtype':'float64','width':1},'split':split,'weight_sha256':hashlib.sha256(weights.read_bytes()).hexdigest(),'steps':30}
manifest_path=folder/'manifest.json'; manifest_path.write_text(json.dumps(manifest,sort_keys=True))
assert len(manifest['weight_sha256'])==64 and manifest['schema']['width']==1
```

**Expected:** manifest has feature x, float64, width1 and matching hash.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: 3 training and2 holdout records. local checks True; production no-go; directory absent. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Freeze the scalar experiment.** Use train x1, 2, 3 and holdout4, 5 with target2 x and disjoint IDs.
   **Expected:** 3 training and2 holdout records.
   **Verify:** Save the assertion results for exercise 1, including 3 training and2 holdout records.

2. **Train within a declared budget.** Zero-initialize float64 Linear and run30 SGD.01 updates.
   **Expected:** finite weights; holdout error below constant training-mean baseline26.
   **Verify:** Save the assertion results for exercise 2, including finite weights; holdout error below constant training-mean baseline26.

3. **Build the owned release bundle.** Save weights, schema and split manifest with a weight SHA256.
   **Expected:** manifest has feature x, float64, width1 and matching hash.
   **Verify:** Save the assertion results for exercise 3, including manifest has feature x, float64, width1 and matching hash.

4. **Verify fresh-process prediction parity.** Run the checked loader in a fresh interpreter and compare holdout predictions.
   **Expected:** predictions match within1e-12.
   **Verify:** Save the assertion results for exercise 4, including predictions match within1e-12.

5. **Make a corrupted artifact fail.** Replace the declared weight hash with 64 zeros and rerun the loader.
   **Expected:** nonzero child exit and weight hash mismatch diagnostic.
   **Verify:** Save the assertion results for exercise 5, including nonzero child exit and weight hash mismatch diagnostic.

6. **Record a bounded decision and cleanup.** Record local parity pass, holdout count 2, previous artifact v1 and production no-go, then remove owned files.
   **Expected:** local checks True; production no-go; directory absent.
   **Verify:** Save the assertion results for exercise 6, including local checks True; production no-go; directory absent.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Release bundle, Integrity gate, Fresh-process inference using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-035` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why is a valid hash insufficient for acceptance?**

It proves only that bytes match a recorded identity. The model may still be incorrect, stale, leaky or unsuitable for the intended population.

**Why include a deliberate failing release check?**

It shows that the gate is connected to the decision rather than merely printing a pass label. A useful acceptance suite detects both valid and invalid artifacts.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-036, Capstone: release a small reproducible PyTorch model.
Read courses/deep-learning-pytorch/guides/torch-036.md and courses/deep-learning-pytorch/lessons/torch-036.py. Direct prerequisites: `torch-035`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
