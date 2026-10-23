# torch-034: Robustness, privacy and evidence beyond a score

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `torch-033`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A reliability report should preserve the conditions and denominators behind a score. The central investigation is concrete: Use groups A, A, B with truth1, 1, 0 and prediction1, 0, 0. The finish condition is A1/2 errors; B0/1. card explicitly has no privacy guarantee. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A reliability report should preserve the conditions and denominators behind a score. Group A with zero errors in one case does not provide the same evidence as zero errors in hundreds of independent cases. Duplicate records can improve an apparent rate without testing new conditions. Perturbation tests need a label policy:crossing a legitimate decision boundary may change the correct target rather than reveal a robustness failure.

Privacy and safety claims require their own mechanisms and evidence. A synthetic fixture containing no personal data does not establish differential privacy. A finite set of successful adversarial checks does not prove all future inputs are safe. This chapter uses Torch tensors for error accounting and controlled perturbations, then writes a bounded model-card record with untested conditions and failure severity.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-034](../../deep-learning-tensorflow/guides/tf-034.md) after deriving the shared numerical contract.

The paired TensorFlow lesson uses the same evidence principles. Framework choice does not change the independence unit, duplicate policy or meaning of a privacy claim. Compare model behavior under identical conditions and keep framework runtime acceptance separate from task reliability.

## Vocabulary and concepts

**Subgroup denominator:** The observation count supporting a group metric.

**Robustness condition:** A specified input change under a declared label policy.

**Finite safety evidence:** Observed results on bounded cases without a universal guarantee.

**Model card:** A record of intended use, evidence and limitations.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-034/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-034.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-034.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Compute boolean error vectors before aggregation. Groupby declared labels and retain integer error/count pairs. Compare row count with unique ID count to expose duplicates. Use None for an untested group rather than a rate of zero. Keep severity categories separate from overall pass rate, and make the decision gate explicit before inspecting results.

## Worked example / walkthrough

### Example A: Count group errors

Counts keep the evidence visible. Equal rates with different denominators do not imply equal uncertainty.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

truth=torch.tensor([1,1,0]); prediction=torch.tensor([1,0,0]); groups=['A','A','B']; errors=prediction!=truth
report={group:(int(errors[torch.tensor([g==group for g in groups])].sum()),groups.count(group)) for group in ['A','B']}
assert report=={'A':(1,2),'B':(0,1)}
```

**Expected:** A1/2 errors; B0/1.

### Example B: Expose repeated identities

Repeated rows can bias a metric without adding independent cases. Identity validation belongs before aggregation.

```python
ids=['a','b','c']+['c']*5
assert len(ids)==8 and len(set(ids))==3
```

**Expected:** 8 rows but3 unique IDs.

### Example C: Trace a controlled perturbation

The last shift crosses the defined boundary. Whether that counts as a robustness failure depends on the intended label semantics.

```python
base=torch.tensor(1.); shifts=torch.tensor([-.1,-.9,-1.1]); changed=(base+shifts>=0).long()
assert changed.tolist()==[1,1,0]
```

**Expected:** labels1, 1, 0.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: A1/2 errors; B0/1. card explicitly has no privacy guarantee. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Count group errors.** Use groups A, A, B with truth1, 1, 0 and prediction1, 0, 0.
   **Expected:** A1/2 errors; B0/1.
   **Verify:** Save the assertion results for exercise 1, including A1/2 errors; B0/1.

2. **Expose repeated identities.** Repeatcorrectrecordc five times and compare row count with unique IDs.
   **Expected:** 8 rows but3 unique IDs.
   **Verify:** Save the assertion results for exercise 2, including 8 rows but3 unique IDs.

3. **Trace a controlled perturbation.** Classify x>=0 at base1 after shifts-.1, -.9, -1.1.
   **Expected:** labels1, 1, 0.
   **Verify:** Save the assertion results for exercise 3, including labels1, 1, 0.

4. **Keep severe failures visible.** Use9 minor passes and1 severe failure.
   **Expected:** overall pass rate.9; severe failure count 1.
   **Verify:** Save the assertion results for exercise 4, including overall pass rate.9; severe failure count 1.

5. **Represent an untested group.** Define a rate helper with count 0.
   **Expected:** None for untested; 0 for zero errors in one case.
   **Verify:** Save the assertion results for exercise 5, including None for untested; 0 for zero errors in one case.

6. **Write a bounded card.** Record3 unique units, synthetic teaching use and untested future conditions.
   **Expected:** card explicitly has no privacy guarantee.
   **Verify:** Save the assertion results for exercise 6, including card explicitly has no privacy guarantee.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Subgroup denominator, Robustness condition, Finite safety evidence using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-033` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Does zero observed failure mean zero risk?**

No. A finite sample can miss rare or unrepresented conditions. Report the tested population, count and coverage.

**Can a model card prove privacy?**

No. It can record a privacy mechanism and its analysis, but documentation does not replace a technical guarantee or empirical evidence.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-034, Robustness, privacy and evidence beyond a score.
Read courses/deep-learning-pytorch/guides/torch-034.md and courses/deep-learning-pytorch/lessons/torch-034.py. Direct prerequisites: `torch-033`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
