# torch-010: Datasets, held-out families and leakage controls

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-009`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A Dataset is an interface for retrieving observations, not a guarantee that the experiment is leakage-free. The central investigation is concrete: Create eight records with groups A, A, B, B, C, C, D, D and values 1, 3, 5, 7, 20, 22, 30, 32. The finish condition is length 8; item 0 has ID 0, group A, value 1. 16, 18, 26, 28. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A Dataset is an interface for retrieving observations, not a guarantee that the experiment is leakage-free. Related records need a shared split unit, such as account or source document. Subset selects indices from a dataset, but choosing those indices is a statistical-design responsibility. Fit preprocessing only on the training subset and freeze it before transforming validation or holdout records. A validation-only extreme should not change a training mean.

This lesson implements a tiny map-style Dataset over eight literal account records. Each item includes identity, group and numeric value so split and pairing checks remain possible. The dataset is deterministic and contains no file or network reads. Grouped splitting, training-only normalization and an explicit held-out perturbation distinguish data-interface correctness from evaluation validity.

## Design decisions and when to use this method

Choose the split unit from the intended deployment claim. For new-account prediction, keep all records from each account on one side of the split. For a future-time claim, also respect when inputs and labels become available. A random row split is appropriate only when its independence and information assumptions match the task.

Use Dataset and Subset to implement access after that design has been chosen. Fit normalization or other learned preprocessing from the training population and freeze it for the declared inductive assessment. A deliberately transductive method using target-population covariates is a different protocol and must be evaluated and reported as such, rather than quietly changing this training-only contract.

## Paired TensorFlow comparison

Compare [tf-010](../../deep-learning-tensorflow/guides/tf-010.md) after deriving the shared numerical contract.

TensorFlow tf.data and PyTorch Dataset/Subset organize access to records, but neither chooses a valid statistical split automatically. The same held-out perturbation oracle applies. PyTorch Dataset commonly separates item retrieval from DataLoader batching, which is taught in lesson 015.

## Vocabulary and concepts

**Map-style Dataset:** A dataset providing indexed item retrieval and a length.

**Subset:** An index selection over an existing dataset.

**Split unit:** The entity assigned wholly to one partition.

**Training-only fit:** Estimating preprocessing state without assessment inputs.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-010/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-010.py`. For macOS/Linux, use the interpreter explicitly selected for a separately prepared native PyTorch environment, and invoke that interpreter on `courses/deep-learning-pytorch/lessons/torch-010.py` from the repository root. The repository's general `.venv` is not assumed to contain PyTorch; the prepared classroom profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Subclass Dataset and implement __len__ and__getitem__. A Subset stores a sequence of indices and delegates item retrieval to the original dataset. Build training indices from whole account groups before calculating any statistic. Stack only selected training values to estimate the mean. Use sets of group IDs to check isolation; disjoint row indices alone are insufficient.

## Trace selection, fitted state and delegated access

The eight literal records form four account groups. Training selects original indices 0, 1, 2, 3 fromA and B; assessment selects 4, 5, 6, 7 fromC and D. The two Subset objects do not copy or redefine those records. They map their local index into the original dataset. Thus assessment[0] returns original identity 4, accountC, value 20. A local batch position zero is not a replacement for the source identity.

| Population | Original identities | Values | Mean |
| --- | --- | --- | --- |
| Training accountsA, B | 0, 1, 2, 3 | 1, 3, 5, 7 | 4 |
| Assessment accountsC, D | 4, 5, 6, 7 | 20, 22, 30, 32 | 26 |
| All records | 0..7 | All eight values | 15 |

Each item returns a scalar tensor plus identity and group metadata. Stacking the four selected training scalars creates a tensor shaped(4, ), whose mean is the fitted normalization state. Applying that scalar to four assessment values yields[16, 18, 26, 28]. Those transformed assessment values do not have mean zero, and they should not be forced to. Their nonzero mean is information about the assessment population relative to the training baseline.

The held-out perturbation is a direct test of the information boundary. Replacing only the final assessment value 32 with 3200 leaves the training values and mean four unchanged. The global mean changes from 15 to 411 because the total becomes 3288 over eight records. A preprocessing path whose fitted training mean changes under this perturbation has consumed assessment information, even if no target label was read.

Alternating row indices produces superficially balanced four-row sets but puts one row from every account on each side. Row-ID intersections are empty while the account-group intersection isA, B, C, D. If the claim concerns new accounts, this is a failure before any neural layer is built. A stronger optimizer or more epochs cannot undo that information crossing.

Dataset is an access interface, not an isolation or immutability guarantee. Subset delegates to the underlying dataset, so later mutation of that object's values can change what a subset returns. A retrieved scalar tensor may also share storage with its source. Use out-of-place transformations or an explicit ownership boundary when mutation is intended, and freeze the fitted preprocessing state independently of mutable dataset access. [PyTorch 2.9 Dataset, Subset and data loading](https://docs.pytorch.org/docs/2.9/data.html).

Keeping identity and group fields does not require feeding them into the model as features. They support split checks, duplicate detection, pairing and error analysis. An account identifier used as an embedding feature would require a separate justification about availability and the meaning of unseen account IDs; it should not enter the model accidentally merely because it travels through the loader.

Finally, four assessment rows here represent only two held-out account families. The fixture is too small and too structured to establish reliable population performance. Its useful evidence is that the access interface, group isolation and preprocessing boundary behave as declared. Later evaluation should preserve the relevant independent units when estimating uncertainty rather than treating correlated rows as additional independent accounts.

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

**Expected:** length 8; item 0 has ID 0, group A, value 1.

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

**Expected:** mean 4.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: length 8; item 0 has ID 0, group A, value 1. 16, 18, 26, 28. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Inspect a literal Dataset.** Create eight records with groups A, A, B, B, C, C, D, D and values 1, 3, 5, 7, 20, 22, 30, 32.
   **Expected:** length 8; item 0 has ID 0, group A, value 1.
   **Verify:** Save the assertion results for exercise 1, including length 8; item 0 has ID 0, group A, value 1.

2. **Select whole groups.** Train on accounts A, B and holdout C, D using Subset.
   **Expected:** four records each; group intersection empty.
   **Verify:** Save the assertion results for exercise 2, including four records each; group intersection empty.

3. **Fit only training values.** Calculate the mean from the four training tensors.
   **Expected:** mean 4.
   **Verify:** Save the assertion results for exercise 3, including mean 4.

4. **Perturb only assessment values.** Replace the final held-out value with 3200 in a copied dataset and recompute the training mean.
   **Expected:** training mean unchanged 4; global mean changes.
   **Verify:** Save the assertion results for exercise 4, including training mean unchanged 4; global mean changes.

5. **Expose row-level leakage.** Assign alternating indices to train/test and inspect group intersection.
   **Expected:** allA, B, C, D cross.
   **Verify:** Save the assertion results for exercise 5, including allA, B, C, D cross.

6. **Apply the frozen transform.** Center held-out values with the training mean.
   **Expected:** 16, 18, 26, 28.
   **Verify:** Save the assertion results for exercise 6, including 16, 18, 26, 28.

## Common pitfalls and diagnosis

If a training statistic changes after an assessment-only perturbation, trace which index set was used during fitting and whether a shared preprocessing object was refit. If row IDs are disjoint but quality is suspiciously high, inspect source-family IDs and near-duplicate records rather than renaming rows. If assessment values unexpectedly become centered at zero, check for assessment-specific refitting.

If a Subset returns an unexpected identity, distinguish its local index from the delegated source index. If an augmentation changes later reads, inspect tensor aliases and underlying dataset mutation. If a report calls four correlated assessment rows four independent accounts, repair the unit of inference before calculating uncertainty. Dataset correctness and evaluation validity must both pass; neither implies the other.

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
