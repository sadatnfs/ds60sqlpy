# torch-015: Dataset, DataLoader, collation and reproducible sampling

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-014`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Dataset defines how to retrieve an observation, while DataLoader defines batching, sampling and collation. The central investigation is concrete: Load five paired ID/value records with batch size 2 and no shuffle. The finish condition is sizes2, 2, 1 and IDs0..4 exactly once. ValueError before padding. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Dataset defines how to retrieve an observation, while DataLoader defines batching, sampling and collation. The default collator stacks compatible tensors and groups compatible structures; variable-length records may need a custom collate_fn. A loader's batch count differs from the number of records, and drop_last can omit a tail. Shuffling needs a controlled generator if the ordering itself is part of a reproducible experiment.

This course uses num_workers=0 so all loading occurs in the same process and requires no extra worker startup or shared-memory assumptions. Multiple workers introduce additional random state, serialization, lifetime and platform considerations that need separate testing. A local generator separates sampler randomness from unrelated global random draws. Record IDs remain in each batch so ordering, duplication and pairing can be checked independently of loss.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-015](../../deep-learning-tensorflow/guides/tf-015.md) after deriving the shared numerical contract.

TensorFlow tf.data combines dataset transformations and pre fetching in its pipeline API. PyTorch commonly separates Dataset retrieval from DataLoader sampling/collation. Both need explicit cardinality, ordering and training-only preprocessing checks; num_workers0is this course's bounded default, not a throughput recommendation.

## Vocabulary and concepts

**DataLoader:** An iterator coordinating sampling, batching and collation over a dataset.

**Collation:** Combining individual observations into a batch structure.

**Sampler generator:** An explicit random-state source controlling sample order.

**Worker count:** The number of separate data-loading processes.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-015/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-015.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-015.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

TensorDataset groups tensor components sharing the leading dimension. DataLoader(batch_size=2, shuffle=False, num_workers=0) yields three batches for five records. A seeded torch.Generator supplied to shuffling controls the sampler sequence in this runtime. A custom collator receives a list of items and must return the declared batch structure; it should not perform hidden network or file mutations.

## Worked example / walkthrough

### Example A: Inspect retained batches

The loader preserves the final singleton by default. The ID conservation check catches missing or duplicated records that value-only statistics may hide.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
def collate(sequences):
    if not sequences or any(len(sequence)==0 for sequence in sequences): raise ValueError('nonempty sequences required')
    lengths=torch.tensor([len(sequence) for sequence in sequences]); batch=torch.zeros((len(sequences),int(lengths.max())),dtype=torch.long)
    for row,sequence in enumerate(sequences): batch[row,:len(sequence)]=torch.tensor(sequence)
    return batch,lengths
dataset=torch.utils.data.TensorDataset(torch.arange(5),torch.arange(1,6,dtype=torch.float32))
loader=torch.utils.data.DataLoader(dataset,batch_size=2,shuffle=False,num_workers=0)
batches=list(loader)
assert [len(ids) for ids,values in batches]==[2,2,1]
assert torch.cat([ids for ids,values in batches]).tolist()==[0,1,2,3,4]
```

**Expected:** sizes2, 2, 1 and IDs0..4 exactly once.

### Example B: Make dropping explicit

The policy changes the effective epoch population. It may be useful for fixed shapes, but it must not be described as an identical traversal.

```python
dropped=list(torch.utils.data.DataLoader(dataset,batch_size=2,drop_last=True,num_workers=0))
assert len(dropped)==2 and torch.cat([ids for ids,values in dropped]).tolist()==[0,1,2,3]
```

**Expected:** two batches; ID4 omitted.

### Example C: Reproduce shuffle with a local generator

A new generator recreates the starting state. Reusing one already-consumed generator would produce a later random sequence rather than a replay.

```python
def order(seed):
    generator=torch.Generator().manual_seed(seed)
    batches=torch.utils.data.DataLoader(dataset,batch_size=2,shuffle=True,generator=generator,num_workers=0)
    return torch.cat([ids for ids,values in batches]).tolist()
assert order(7)==order(7) and sorted(order(7))==list(range(5))
```

**Expected:** same permutation; all five IDs retained.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: sizes2, 2, 1 and IDs0..4 exactly once. ValueError before padding. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Inspect retained batches.** Load five paired ID/value records with batch size 2 and no shuffle.
   **Expected:** sizes2, 2, 1 and IDs0..4 exactly once.
   **Verify:** Save the assertion results for exercise 1, including sizes2, 2, 1 and IDs0..4 exactly once.

2. **Make dropping explicit.** Set drop_last True on the same fixture.
   **Expected:** two batches; ID4 omitted.
   **Verify:** Save the assertion results for exercise 2, including two batches; ID4 omitted.

3. **Reproduce shuffle with a local generator.** Construct two loaders with fresh generators both seeded7.
   **Expected:** same permutation; all five IDs retained.
   **Verify:** Save the assertion results for exercise 3, including same permutation; all five IDs retained.

4. **Col late variable-length sequences.** Pad sequences[2, 3] and[4] with zero while keeping lengths.
   **Expected:** batch[[2, 3], [4, 0]] and lengths 2, 1.
   **Verify:** Save the assertion results for exercise 4, including batch[[2, 3], [4, 0]] and lengths 2, 1.

5. **Preserve pairing after shuffle.** Load values=2*IDs with shuffling and check each batch.
   **Expected:** every target equals twice its ID.
   **Verify:** Save the assertion results for exercise 5, including every target equals twice its ID.

6. **Reject an empty sequence in this collator.** Pass[[], [1]] to a collator whose contract requires positive lengths.
   **Expected:** ValueError before padding.
   **Verify:** Save the assertion results for exercise 6, including ValueError before padding.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain DataLoader, Collation, Sampler generator using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-014` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 DataLoader](https://docs.pytorch.org/docs/2.9/data.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why is a seed insufficient by itself?**

Reproducibility also depends on which generator consumes which draws, worker behavior, dataset state and ordering. Record the whole data contract.

**Does drop_last only change tensor shape?**

No. It can remove observations from an epoch and change metric denominators. That statistical effect must be reported.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-015, Dataset, DataLoader, collation and reproducible sampling.
Read courses/deep-learning-pytorch/guides/torch-015.md and courses/deep-learning-pytorch/lessons/torch-015.py. Direct prerequisites: `torch-014`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
