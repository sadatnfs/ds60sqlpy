# torch-022: Attention, transformer masks and information boundaries

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-021`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Attention forms weighted combinations of value vectors using query-key comparisons. The central investigation is concrete: Use zero3x2queries/keys and values2, 0; 0, 2; 6, 6. The finish condition is outputs2, 0; 1, 1; 8/3, 8/3. repeated evaluation matches. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Attention forms weighted combinations of value vectors using query-key comparisons. A causal decoder restricts each query to current and earlier positions. PyTorch's functional scaled_dot_product_attention uses boolean True for allowed positions, while other attention APIs such as Multihead Attention key_padding_mask use True for ignored keys. Mask polarity belongs to the exact parameter contract, not to the framework name.

The functional API also applies dropout according to its dropout_p argument; calling an enclosing module.eval does not automatically change an explicit nonzero probability. For an evaluation oracle, pass dropout_p0. Equal queries and keys make legal scores uniform, so the expected outputs are prefix means. Nonuniform scores and future-only perturbations add stronger checks than causal-looking triangles alone.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-022](../../deep-learning-tensorflow/guides/tf-022.md) after deriving the shared numerical contract.

Keras MultiHead Attention attention_mask uses True/1for allowed positions, matching the course allowed convention. PyTorch functional SDPA also uses True allowed, but Multihead Attention key_padding_mask uses True ignored. Functional PyTorch dropout must be set explicitly for inference.

## Vocabulary and concepts

**SDPA:** Scaled dot-product attention implemented by a functional API.

**Mask polarity:** Whether True means allowed or excluded for this parameter.

**Prefix invariance:** Agreement between a full sequence prefix and independent prefix execution.

**Dropout argument:** An explicit stochastic policy in the functional attention call.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-022/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-022.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-022.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

The checked helper accepts nonempty2D self-attention matrices and a boolean square allowed mask. Reject fully masked rows before normalization. F.scaled_dot_product_attention supplies the1/sqrt(key_width) scaling and normalizes over the key axis. A causal lower triangle includes its diagonal for shifted next-token targets. Independently recompute each prefix rather than slicing full weights.

## Worked example / walkthrough

### Example A: Compute uniform causal mixtures

Each query averages its allowed values. The fixture exposes the meaning of both axes and the included diagonal.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
def attention(q,k,v,allowed):
    if any(value.ndim!=2 for value in (q,k,v)) or q.shape[0]==0 or q.shape[1]==0: raise ValueError('nonempty matrices required')
    if k.shape!=q.shape or v.shape[0]!=q.shape[0] or allowed.shape!=(q.shape[0],q.shape[0]): raise ValueError('shape mismatch')
    if allowed.dtype!=torch.bool: raise TypeError('boolean allowed mask required')
    if not bool(allowed.any(-1).all()) or not all(bool(torch.isfinite(value).all()) for value in (q,k,v)): raise ValueError('legal finite attention rows required')
    return F.scaled_dot_product_attention(q,k,v,attn_mask=allowed,dropout_p=0.)
q=torch.zeros((3,2),dtype=torch.float64); v=torch.tensor([[2.,0.],[0.,2.],[6.,6.]],dtype=torch.float64); allowed=torch.ones((3,3),dtype=torch.bool).tril()
out=attention(q,q,v,allowed)
torch.testing.assert_close(out,torch.tensor([[2.,0.],[1.,1.],[8/3,8/3]],dtype=torch.float64),atol=1e-12,rtol=0)
```

**Expected:** outputs2, 0; 1, 1; 8/3, 8/3.

### Example B: Perturb only the future

The causal boundary is verified through behavior. A zeroed future weight plot would not detect every wrong normalization or upstream leak.

```python
future=v.clone(); future[2]=torch.tensor([100.,200.]); changed=attention(q,q,future,allowed)
torch.testing.assert_close(changed[:2],out[:2],atol=1e-12,rtol=0)
torch.testing.assert_close(changed[2],torch.tensor([34.,202/3],dtype=torch.float64),atol=1e-12,rtol=0)
```

**Expected:** first two rows unchanged; last34, 202/3.

### Example C: Recompute nonuniform prefixes

Nonuniform scores exercise query-key arithmetic and scaling. The checker rebuild s the computation on the shorter inputs.

```python
non=torch.tensor([[1.,0.],[0.,1.],[1.,1.]],dtype=torch.float64); full=attention(non,non,v,allowed)
for cut in range(1,4): torch.testing.assert_close(attention(non[:cut],non[:cut],v[:cut],allowed[:cut,:cut]),full[:cut],atol=1e-12,rtol=0)
```

**Expected:** all prefix outputs match within1e-12.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: outputs2, 0; 1, 1; 8/3, 8/3. repeated evaluation matches. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Compute uniform causal mixtures.** Use zero3x2queries/keys and values2, 0; 0, 2; 6, 6.
   **Expected:** outputs2, 0; 1, 1; 8/3, 8/3.
   **Verify:** Save the assertion results for exercise 1, including outputs2, 0; 1, 1; 8/3, 8/3.

2. **Perturb only the future.** Change only the third value to100, 200.
   **Expected:** first two rows unchanged; last34, 202/3.
   **Verify:** Save the assertion results for exercise 2, including first two rows unchanged; last34, 202/3.

3. **Recompute nonuniform prefixes.** UseQ=K rows1, 0; 0, 1; 1, 1 and compare cuts1..3.
   **Expected:** all prefix outputs match within1e-12.
   **Verify:** Save the assertion results for exercise 3, including all prefix outputs match within1e-12.

4. **Reject an all-masked row.** Set the second allowed row to False.
   **Expected:** ValueError before the attention call.
   **Verify:** Save the assertion results for exercise 4, including ValueError before the attention call.

5. **Translate mask polarity explicitly.** Invert the allowed matrix to obtain a forbidden mask for APIs using True as blocked.
   **Expected:** first forbidden row False, True, True.
   **Verify:** Save the assertion results for exercise 5, including first forbidden row False, True, True.

6. **Keep inference dropout disabled.** Repeat functional attention with dropout_p0 and compare exact outputs.
   **Expected:** repeated evaluation matches.
   **Verify:** Save the assertion results for exercise 6, including repeated evaluation matches.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain SDPA, Mask polarity, Prefix invariance using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-021` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 scaled dot product attention](https://docs.pytorch.org/docs/2.9/generated/torch.nn.functional.scaled_dot_product_attention.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Can a mask be copied unchanged between all attention APIs?**

No. Check shape, polarity, causal offset and padding semantics for each parameter. A triangular matrix alone is not a contract.

**Why test nonuniform scores as well as prefix means?**

Uniform scores can hide a missing scale factor or incorrect query-key arithmetic. Independent nonuniform fixtures exercise those mechanisms.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-022, Attention, transformer masks and information boundaries.
Read courses/deep-learning-pytorch/guides/torch-022.md and courses/deep-learning-pytorch/lessons/torch-022.py. Direct prerequisites: `torch-021`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
