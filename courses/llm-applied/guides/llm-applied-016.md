# llm-applied-016: Low-rank adaptation: dimensions, gradients and a real update

Status: authored applied LLM content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Advanced; approximately 240 minutes. Direct prerequisites: `llm-applied-015`, `llm-032`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Low-rank adaptation freezes a base weight matrix and learns a smaller additive update. The central investigation is concrete: ConstructW=I8, A=ones(8, 2)/8, B=zeros(2, 8), rank 2, alpha 4. The finish condition is base64 entries; adapter32; scale2. rank at most2; delta atalpha4 is twice delta atalpha2. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Low-rank adaptation freezes a base weight matrix and learns a smaller additive update. Under the row-vector convention used here, the effective matrix isW+(alpha/r)A@B, withW8x8, A8x2 andB2x8. Rankr2 gives32 trainable adapter entries compared with 64 base entries. The scaling factoralpha/r is part of the function and changes gradients. Some libraries store Linear weights transposed relative to this equation, so shapes must be translated explicitly.

InitializeA to small nonzero values andB to zero. The initial delta is zero, preserving the base function. On the first step, the gradient ofA is zero because it containsB, whileB receives a gradient throughA. This is a connected zero gradient, not a missing path. AfterB changes, later updates can changeA too. The chapter performs actual PyTorch SGD updates and checks frozen-base identity, parameter counts and merged inference parity. It demonstrates LoRA mechanics on a small matrix, not the quality of adapting a pretrained assistant.

## Design decisions and when to use this method

Use LoRA when a measured adaptation task can be addressed with a constrained update and when storing or switching small adapters is useful. Parameter savings do not translate directly into total training-memory savings: activations, gradients, optimizer state and the frozen base still occupy resources. Measure the actual prepared runtime rather than quoting a ratio of trainable parameters as peak-memory reduction.

Do not assume one rank or target-module list works for every domain. Compare against a prompt baseline and, when feasible, a full-SFT control. Evaluate held-out task families, support failures and retention of baseline behavior. Adapter composition and merging can change the effective function, so test inference parity and keep base revision, tokenizer revision, rank, alpha, target modules and training-data identity with every adapter artifact.

## Vocabulary and concepts

**Adapter rank:** The inner dimension limiting the rank of the update matrix.

**LoRA scale:** The multiplieralpha/r applied to the low-rank product.

**Frozen base:** Weights excluded from gradient updates during adaptation.

**Merged inference:** An equivalent matrix with the adapter delta added for serving.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-016/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/llm-applied/lessons/llm-applied-016.py`. For macOS/Linux use `.venv/bin/python courses/llm-applied/lessons/llm-applied-016.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

CreateW as a nontrainable tensor andA/B asParameters. Pass onlyA andB to the optimizer. Compute output=x@(W+scale*A@B). SnapshotW before training and assert exact equality afterward. Merge into a new matrix for inference and compare with the unmerged computation. Do not mutate the original base when creating the merged artifact, because that would change other adapters sharing it.

## Worked example / walkthrough

### Example A: Count and orient parameters

The orientation is chosen for row-vector inputs. A framework Linear layer storing(out, in) weights would require a transposed formulation rather than copying these shapes blindly.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

w=torch.eye(8); a=nn.Parameter(torch.ones((8,2))/8); b=nn.Parameter(torch.zeros((2,8))); rank=2; alpha=4; scale=alpha/rank; x=torch.ones((1,8))
assert w.numel()==64 and a.numel()+b.numel()==32 and scale==2
```

**Expected:** base64 entries; adapter32; scale2.

### Example B: Prove zero-delta initialization

The initial adapter does not perturb the base. This is useful for controlled comparisons and explains why one factor starts at zero.

```python
initial=x@(w+scale*(a@b)); saved=w.clone()
assert torch.equal(initial,x@w) and torch.equal(a@b,torch.zeros((8,8)))
```

**Expected:** outputs exactly equalones(1, 8).

### Example C: Inspect the first gradients

The zero derivative ofA follows algebraically fromB=0. Treating it as a disconnected parameter would be a mistaken diagnosis.

```python
loss=initial.square().mean(); loss.backward()
assert torch.count_nonzero(a.grad).item()==0 and torch.count_nonzero(b.grad).item()>0 and w.grad is None
```

**Expected:** A gradientzero; B gradientnonzero; W has no gradient.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: base64 entries; adapter32; scale2. rank at most2; delta atalpha4 is twice delta atalpha2. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Count and orient parameters.** ConstructW=I8, A=ones(8, 2)/8, B=zeros(2, 8), rank 2, alpha 4.
   **Expected:** base64 entries; adapter32; scale2.
   **Verify:** Save the assertion results for exercise 1, including base64 entries; adapter32; scale2.

2. **Prove zero-delta initialization.** Compare the effective output with the frozen base before updating.
   **Expected:** outputs exactly equalones(1, 8).
   **Verify:** Save the assertion results for exercise 2, including outputs exactly equalones(1, 8).

3. **Inspect the first gradients.** Minimize mean squared output towardzero and backpropagate once.
   **Expected:** A gradientzero; B gradientnonzero; W has no gradient.
   **Verify:** Save the assertion results for exercise 3, including A gradientzero; B gradientnonzero; W has no gradient.

4. **Take an adapter-only step.** UseSGD.1 onA/B and recalculate the objective.
   **Expected:** B changes; loss decreases; W remains byte-identical.
   **Verify:** Save the assertion results for exercise 4, including B changes; loss decreases; W remains byte-identical.

5. **Merge without changing the base.** Create a detached merged matrix and compare predictions with the unmerged expression.
   **Expected:** parity within1e-6; originalW unchanged.
   **Verify:** Save the assertion results for exercise 5, including parity within1e-6; originalW unchanged.

6. **Inspect rank and scaling consequences.** Check the numerical rank of the update and comparealpha4 withalpha2 using the same factors.
   **Expected:** rank at most2; delta atalpha4 is twice delta atalpha2.
   **Verify:** Save the assertion results for exercise 6, including rank at most2; delta atalpha4 is twice delta atalpha2.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Adapter rank, LoRA scale, Frozen base using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-015`, `llm-032` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [LoRA](https://arxiv.org/abs/2106.09685), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-016, Low-rank adaptation: dimensions, gradients and a real update.
Read courses/llm-applied/guides/llm-applied-016.md and courses/llm-applied/lessons/llm-applied-016.py. Direct prerequisites: `llm-applied-015`, `llm-032`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
