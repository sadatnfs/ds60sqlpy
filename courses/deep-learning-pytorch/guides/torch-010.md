# torch-010: Datasets, held-out families and leakage controls

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-009`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A Dataset is an interface for retrieving observations, not a guarantee that the experiment is leakage-free. The central investigation is concrete: Create eight records with groups A, A, B, B, C, C, D, D and values1, 3, 5, 7, 20, 22, 30, 32. The finish condition is length8; item0 has ID0, group A, value 1. 16, 18, 26, 28. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A Dataset is an interface for retrieving observations, not a guarantee that the experiment is leakage-free. Related records need a shared split unit, such as account or source document. Subset selects indices from a dataset, but choosing those indices is a statistical-design responsibility. Fit preprocessing only on the training subset and freeze it before transforming validation or holdout records. A validation-only extreme should not change a training mean.

This lesson implements a tiny map-style Dataset over eight literal account records. Each item includes identity, group and numeric value so split and pairing checks remain possible. The dataset is deterministic and contains no file or network reads. Grouped splitting, training-only normalization and an explicit held-out perturbation distinguish data-interface correctness from evaluation validity.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-010](../../deep-learning-tensorflow/guides/tf-010.md) after deriving the shared numerical contract.

TensorFlow tf.data and PyTorch Dataset/Subset organize access to records, but neither chooses a valid statistical split automatically. The same held-out perturbation oracle applies. PyTorch Dataset commonly separates item retrieval from DataLoader batching, which is taught in lesson015.

## Vocabulary and concepts

**Map-style Dataset:** A dataset providing indexed item retrieval and a length.

**Subset:** An index selection over an existing dataset.

**Split unit:** The entity assigned who ll y to one partition.

**Training-only fit:** Estimating preprocessing state without assessment inputs.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-010/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-010.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-010.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Subclass Dataset and implement__len__ and__get item__. A Subset stores a sequence of indices and delegates item retrieval to the original dataset. Build training indices from whole account groups before calculating any statistic. Stack only selected training values to estimate the mean. Use sets of group IDs to check isolation; disjoint row indices alone are insufficient.

## Worked example / walkthrough

### Example A: Inspect a literal Dataset

The dataset returns metadata beside the tensor. A value-only interface would make it harder to audit group membership and record conservation.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
class Accounts(torch.utils.data.Dataset):
    def __init__(self):
        self.groups=list('AABBCCDD'); self.values=torch.tensor([1.,3.,5.,7.,20.,22.,30.,32.],dtype=torch.float64)
    def __len__(self): return len(self.groups)
    def __getitem__(self,index): return index,self.groups[index],self.values[index]
dataset=Accounts(); assert len(dataset)==8
identity,group,value=dataset[0]; assert identity==0 and group=='A' and value.item()==1
```

**Expected:** length8; item0 has ID0, group A, value 1.

### Example B: Select whole groups

The grouping policy precedes the subset construction. Subset itself would happily accept a leaking row-level split.

```python
train_ids=[i for i in range(len(dataset)) if dataset[i][1] in {'A','B'}]; test_ids=[i for i in range(len(dataset)) if i not in train_ids]
train=torch.utils.data.Subset(dataset,train_ids); test=torch.utils.data.Subset(dataset,test_ids)
assert len(train)==len(test)==4 and not {row[1] for row in train}&{row[1] for row in test}
```

**Expected:** four records each; group intersection empty.

### Example C: Fit only training values

The statistic is fitted state. Even without labels, it would leak assessment information if computed over the entire dataset.

```python
mean=torch.stack([row[2] for row in train]).mean(); assert mean.item()==4
```

**Expected:** mean4.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: length8; item0 has ID0, group A, value 1. 16, 18, 26, 28. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Inspect a literal Dataset.** Create eight records with groups A, A, B, B, C, C, D, D and values1, 3, 5, 7, 20, 22, 30, 32.
   **Expected:** length8; item0 has ID0, group A, value 1.
   **Verify:** Save the assertion results for exercise 1, including length8; item0 has ID0, group A, value 1.

2. **Select whole groups.** Train on accounts A, B and holdout C, D using Subset.
   **Expected:** four records each; group intersection empty.
   **Verify:** Save the assertion results for exercise 2, including four records each; group intersection empty.

3. **Fit only training values.** Calculate the mean from the four training tensors.
   **Expected:** mean4.
   **Verify:** Save the assertion results for exercise 3, including mean4.

4. **Perturb only assessment values.** Replace the final held-out value with 3200 in a copied dataset and recompute the training mean.
   **Expected:** training mean unchanged4; global mean changes.
   **Verify:** Save the assertion results for exercise 4, including training mean unchanged4; global mean changes.

5. **Expose row-level leakage.** Assign alter nat in g indices to train/test and inspect group intersection.
   **Expected:** allA, B, C, D cross.
   **Verify:** Save the assertion results for exercise 5, including allA, B, C, D cross.

6. **Apply the frozen transform.** Center held-out values with the training mean.
   **Expected:** 16, 18, 26, 28.
   **Verify:** Save the assertion results for exercise 6, including 16, 18, 26, 28.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Map-style Dataset, Subset, Split unit using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-009` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 data utilities](https://docs.pytorch.org/docs/2.9/data.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Does using Subset prevent leakage?**

No. It only selects indices. The author must ensure related entities and fitted preprocessing remain on the correct side of the information boundary.

**Why keep IDs when the model only consumes tensors?**

IDs support pairing, split isolation, duplicate detection and error analysis. They can travel through the data pipeline without being model features.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-010, Datasets, held-out families and leakage controls.
Read courses/deep-learning-pytorch/guides/torch-010.md and courses/deep-learning-pytorch/lessons/torch-010.py. Direct prerequisites: `torch-009`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
