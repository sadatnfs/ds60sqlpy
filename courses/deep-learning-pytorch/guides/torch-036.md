# torch-036: Capstone: release a small reproducible PyTorch model

## Level and prerequisites

Advanced; approximately 240 minutes. Direct prerequisites: `torch-035`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A reproducible model release is a bundle of state, schema, data identity, execution evidence and limitations. The central investigation is concrete: Use train x1, 2, 3 and holdout 4, 5 with target 2 x and disjoint IDs. The finish condition is 3training and 2 holdout records. local checks True; production no-go; directory absent. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A reproducible model release is a bundle of state, schema, data identity, execution evidence and limitations. A valid artifact must reconstruct the intended model and produce checked predictions in a fresh process. A hash detects changed bytes but does not prove that the bytes contain a useful or honestly evaluated model. Release gates should fail on missing or incorrect evidence rather than silently treat unknown checks as passed.

This capstone trains a small scalar regressor under a fixed budget, saves its state with a feature/dtype schema and split manifest, and executes a fresh-process inference check. It then deliberately corrupts the declared state hash and proves that the loader rejects the bundle before using it. The temporary release is a local teaching artifact, not a deployment. The final record distinguishes local contract acceptance from unestablished production reliability and retains a rollback identity.

## Design decisions and when to use this method

Treat release as a conjunction of independently reviewable contracts rather than a filename or a score. Decide the predictor's schema, artifact identity, evaluation population and failure behavior before packaging. A required check that is missing is not equivalent to a pass, and an expected negative test passes only when the system rejects the invalid case as intended.

Keep the local teaching acceptance separate from production readiness. The current bundle proves a small trained function can be reconstructed and rejects a mismatched weight digest. A two-row visible holdout, an unexercised rollback name and no operational deployment test support a production no-go, which is a valid capstone conclusion.

## Paired TensorFlow comparison

Compare [tf-036](../../deep-learning-tensorflow/guides/tf-036.md) after deriving the shared numerical contract.

The paired TensorFlow release uses the same evidence categories but different artifact formats. PyTorch state_dict requires explicit architecture reconstruction, and exported programs add their own constraints. Both need integrity, schema, fresh-process and negative-gate checks; neither framework makes a small holdout a production guarantee.

## Vocabulary and concepts

**Release bundle:** The model state, semantic schema, lineage and evidence needed for reconstruction.

**Integrity gate:** A check that artifact bytes match their recorded identity.

**Fresh-process inference:** Prediction after reconstruction without live parent objects.

**Rollback identity:** A retained previous artifact reference used in a recovery decision.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-036/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-036.py`. For macOS/Linux, use the interpreter explicitly selected for a separately prepared native PyTorch environment, and invoke that interpreter on `courses/deep-learning-pytorch/lessons/torch-036.py` from the repository root. The repository's general `.venv` is not assumed to contain PyTorch; the prepared classroom profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Train an nn.Linear(1, 1, bias=False) on literal float64 points using fixed SGD updates. Serialize state_dict, canonical JSON schema and split IDs into an owned Temporary Directory. Record SHA256 of the weight file. The child verifies the hash and schema before constructing the module and loading weights_only=True. Bound the subprocess, include stderr on unexpected failure, and remove only the owned temporary directory.

## Connect the trained function to the released bytes

The training objective is \(L(w)=\frac{14}{3}(w-2)^2\) on x=[1, 2, 3]. With learning rate 0.01, the error \(e_{t}=w_{t}-2\) follows \(e_{t+1}=\frac{68}{75}e_t\). Starting at zero gives \(w_t=2-2\left(\frac{68}{75}\right)^t\). After the fixed thirty updates, the analytic weight is approximately 1.89420638. This derivation supplies an independent check on the training mechanism rather than relying only on the loop's finite-value assertion.

The held-out inputs are 4 and 5, with targets 8 and 10. The training-mean target baseline predicts four, so its squared errors are 16 and 36 and MSE is 26. For the trained scalar model, the holdout MSE is \(\frac{16+25}{2}(w_{30}-2)^2=82\left(\frac{68}{75}\right)^{60}\), approximately 0.229442. The threshold below 26 is therefore interpretable for this visible fixture. It does not establish population quality: the rule y=2x is public, and both assessment inputs extrapolate beyond the training range.

The predictor is more than its state tensor. Its architecture is bias-free Linear(1, 1), its dtype is float64, its feature list is['x'], and its output represents the same scalar target units. The manifest carries that schema, split IDs, step count and a digest of the serialized weight file. A future normalized or categorical model would also need its fitted preprocessing and label mapping. Reconstructing a tensor of the right shape cannot recover omitted semantic metadata.

The digest binds the manifest's expected weight identity to the actual saved bytes. The child recomputes SHA256 before loading and rejects a mismatch. The deliberate all-zero expected digest exercises that rejection path. It is a successful negative test because the invalid bundle fails with the expected diagnostic; it does not mean the corrupted bundle is an accepted release.

Integrity is narrower than authenticity or correctness. A digest does not identify a trusted publisher by itself, and a party able to replace both weights and the expected digest can create a different self-consistent pair. Correctly hashed bytes can also encode a poor model or dishonest split. The lesson's local artifacts are trusted teaching inputs, so it tests byte mismatch detection rather than a signed distribution or supply-chain system.

The child separately checks the exact schema before constructing the model. That catches a changed feature/dtype/width contract even if the weight bytes are unchanged. The current child does not independently revalidate every possible lineage field or reproduce training. The parent established disjoint split IDs earlier, and the manifest records them; those facts should not be inflated into authenticated data lineage or are computed training receipt.

Fresh-process prediction parity removes the possibility of satisfying the test by reusing the original model object. The child loads the saved state with weights_only=True on CPU, sets evaluation mode, and predicts the two fixed rows under inference_mode. The parent compares with its recorded outputs at 1e-12 for this float64 fixture. That is a local inference-reconstruction proof, not an optimizer/RNG continuation proof. The earlier checkpoint and export lessons are separate evidence items rather than booleans to assume here.

A useful gate table keeps these distinctions explicit:

| Gate | Evidence in this capstone | Limit |
| --- | --- | --- |
| training procedure | thirty actual updates and analytic fixture | no unseen-population claim |
| weight integrity | recomputed digest and deliberate mismatch rejection | no publisher authentication |
| schema | exact child-side dictionary comparison | no general semantic-schema validator |
| reconstruction | fresh child predictions agree | not training continuation |
| assessment | two visible held-out rows and baseline | very limited coverage |
| rollback | previous identity v1 recorded | no previous artifact restored here |
| operations | not exercised | production remains no-go |

The previous-artifact string is a decision reference, not proof that a recoverable file exists or that it is compatible with current preprocessing. A real rollback rehearsal would load the identified previous artifact, verify its schema and predictions, and define the effect on any surrounding state. This exercise retains the reference without claiming that rehearsal occurred.

Publication and cleanup also have boundaries. The files are created in one owned TemporaryDirectory and removed after the checks. No server, registry or deployment is started. A completed save/load test does not establish crash-safe publication, concurrent-reader behavior or long-term retention. Those require their own artifact lifecycle and operational tests.

The final record can therefore say local_contracts_pass=True and production_go=False without contradiction. It acknowledges successful mechanics while preserving missing assessment and operational evidence. The paired TensorFlow release uses different formats and some different gates, but follows the same principle: each claim should be supported by the corresponding actual check, and a required unknown or failure must remain visible.

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

**Expected:** 3training and 2 holdout records.

### Example B: Train within a declared budget

The budget is not extended after seeing the holdout. The baseline predicts training mean target 4, so gives errors 16 and 36on the two test rows.

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

**Expected:** finite weights; holdout error below constant training-mean baseline 26.

### Example C: Build the owned release bundle

The hash binds the manifest to the saved bytes. The feature order and dtype provide semantic information that a state dictionary alone cannot explain.

```python
temporary=tempfile.TemporaryDirectory(); folder=Path(temporary.name); weights=folder/'weights.pt'; torch.save(model.state_dict(),weights)
manifest={'schema':{'features':['x'],'dtype':'float64','width':1},'split':split,'weight_sha256':hashlib.sha256(weights.read_bytes()).hexdigest(),'steps':30}
manifest_path=folder/'manifest.json'; manifest_path.write_text(json.dumps(manifest,sort_keys=True))
assert len(manifest['weight_sha256'])==64 and manifest['schema']['width']==1
```

**Expected:** manifest has feature x, float64, width 1 and matching hash.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: 3training and 2 holdout records. local checks True; production no-go; directory absent. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Freeze the scalar experiment.** Use train x1, 2, 3 and holdout 4, 5 with target 2 x and disjoint IDs.
   **Expected:** 3training and 2 holdout records.
   **Verify:** Save the assertion results for exercise 1, including 3training and 2 holdout records.

2. **Train within a declared budget.** Zero-initialize float64 Linear and run 30 SGD.01 updates.
   **Expected:** finite weights; holdout error below constant training-mean baseline 26.
   **Verify:** Save the assertion results for exercise 2, including finite weights; holdout error below constant training-mean baseline 26.

3. **Build the owned release bundle.** Save weights, schema and split manifest with a weight SHA256.
   **Expected:** manifest has feature x, float64, width 1 and matching hash.
   **Verify:** Save the assertion results for exercise 3, including manifest has feature x, float64, width 1 and matching hash.

4. **Verify fresh-process prediction parity.** Run the checked loader in a fresh interpreter and compare holdout predictions.
   **Expected:** predictions match within 1e-12.
   **Verify:** Save the assertion results for exercise 4, including predictions match within 1e-12.

5. **Make a corrupted artifact fail.** Replace the declared weight hash with 64 zeros and rerun the loader.
   **Expected:** nonzero child exit and weight hash mismatch diagnostic.
   **Verify:** Save the assertion results for exercise 5, including nonzero child exit and weight hash mismatch diagnostic.

6. **Record a bounded decision and cleanup.** Record local parity pass, holdout count 2, previous artifact v1 and production no-go, then remove owned files.
   **Expected:** local checks True; production no-go; directory absent.
   **Verify:** Save the assertion results for exercise 6, including local checks True; production no-go; directory absent.

## Common pitfalls and diagnosis

If the trained weight differs, compare the recurrence, step count, learning rate and reduction before investigating serialization. If the child loads but predictions differ, check architecture, dtype, feature semantics and the exact artifact path. If the corrupted digest is accepted, the integrity gate is disconnected from loading and the local acceptance must fail.

If a release record marks an unexecuted checkpoint or rollback test true, replace that assumption with the actual unavailable state and required next evidence. If a hash matches but evaluation is leaky, do not treat integrity as a quality override. If cleanup would target an existing learner directory, stop and restore the owned-artifact boundary. Preserve the production no-go until the named missing gates have independent evidence.

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
