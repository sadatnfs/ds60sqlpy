# torch-022: Attention, transformer masks and information boundaries

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-021`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Attention forms weighted combinations of value vectors using query-key comparisons. The central investigation is concrete: Use zero 3-by-2 queries/keys and values 2, 0; 0, 2; 6, 6. The finish condition is outputs 2, 0; 1, 1; \(\frac{8}{3}\), \(\frac{8}{3}\). repeated evaluation matches. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Attention forms weighted combinations of value vectors using query-key comparisons. A causal decoder restricts each query to current and earlier positions. PyTorch's functional scaled_dot_product_attention uses boolean True for allowed positions, while other attention APIs such as Multihead Attention key_padding_mask use True for ignored keys. Mask polarity belongs to the exact parameter contract, not to the framework name.

The functional API also applies dropout according to its dropout_p argument; calling an enclosing module.eval does not automatically change an explicit nonzero probability. For an evaluation oracle, pass dropout_p=0. Equal queries and keys make legal scores uniform, so the expected outputs are prefix means. Nonuniform scores and future-only perturbations add stronger checks than causal-looking triangles alone.

## Design decisions and when to use this method

Use attention when an output needs a content-dependent mixture of source representations. Decide first which information exists at each query position. Encoder self-attention, causal decoder attention and cross-attention have different allowed source sets even when they use the same matrix formula.

Choose masks from absolute query/key positions and padding policy, then translate them to the exact API parameter convention. Keep the small CPU SDPA helper as a deliberately restricted square self-attention contract. A cache with unequal query/key lengths or a multihead module needs a new shape/alignment review rather than an unexamined copy of this triangle.

## Paired TensorFlow comparison

Compare [tf-022](../../deep-learning-tensorflow/guides/tf-022.md) after deriving the shared numerical contract.

Keras MultiHead Attention attention_mask uses True/1for allowed positions, matching the course allowed convention. PyTorch functional SDPA also uses True allowed, but Multihead Attention key_padding_mask uses True ignored. Functional PyTorch dropout must be set explicitly for inference.

## Vocabulary and concepts

**SDPA:** Scaled dot-product attention implemented by a functional API.

**Mask polarity:** Whether True means allowed or excluded for this parameter.

**Prefix invariance:** Agreement between a full sequence prefix and independent prefix execution.

**Dropout argument:** An explicit stochastic policy in the functional attention call.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-022/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-022.py`. For macOS/Linux, use the interpreter explicitly selected for a separately prepared native PyTorch environment, and invoke that interpreter on `courses/deep-learning-pytorch/lessons/torch-022.py` from the repository root. The repository's general `.venv` is not assumed to contain PyTorch; the prepared classroom profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

The checked helper accepts nonempty 2 D self-attention matrices and a boolean square allowed mask. Reject fully masked rows before normalization. F.scaled_dot_product_attention supplies the \(\frac{1}{\sqrt{\mathrm{key}_{\mathrm{width}}}}\) scaling and normalizes over the key axis. A causal lower triangle includes its diagonal for shifted next-token targets. Independently recompute each prefix rather than slicing full weights.

## Derive attention values and information boundaries

Let Q have shape(L, d_k), K shape(S, d_k) and V shape(S, d_v). Scores \(S_{\mathrm{score}}=\frac{{QK}^{T}}{\sqrt{d_{k}}}\) have shape(L, S): each row belongs to one query and each column to one key. Softmax runs across the key axis, and P@V produces(L, d_v). The lesson restricts L=S and matching query/key widths to make this map inspectable. Batched multihead code adds batch/head axes; those do not replace the query and key meanings.

When every score is zero, a legal row containing m keys assigns each probability \(\frac{1}{m}\). The causal rows here permit one, two and three keys, giving[2, 0], [1, 1] and[\(\frac{8}{3}\), \(\frac{8}{3}\)]. Multiplying an unrestricted uniform \(\frac{1}{3}\) distribution by the triangle afterward would instead leave row sums \(\frac{1}{3}\), \(\frac{2}{3}\), 1. Forbidden keys already participated in normalization, so masking must define the legal score set before softmax or be followed by a correctly specified renormalization.

The zero-score example cannot verify the scale factor: zero divided by any finite positive width factor remains zero. For the nonuniform second query[0, 1], the two legal keys[1, 0] and[0, 1] produce scores 0 and \(a=\frac{1}{\sqrt{2}}\). Let \(p=\frac{\exp(a)}{1+\exp(a)}\), approximately 0.669762. The correct mixture is[2(1-p), 2p], approximately[0.660477, 1.339523]. Omitting the scale changes p to \(\frac{\exp(1)}{1+\exp(1)}\), approximately 0.731059, while a causal prefix test can still pass. Thus nonuniform prefix agreement checks an information boundary but is not an independent numerical oracle for every score operation.

A backward trace separates the roles of Q, K and V. If upstream derivatives are \(G=\frac{\partial L}{\partial Y}\), then \(\frac{\partial L}{\partial V}={P}^{T}\) G and \(\frac{\partial L}{\partial P}=G\) \({V}^{T}\). For one softmax row p with incoming derivative u, the score derivative is p elementwise-multiplied by(u-sum(p*u)). This subtracts the probability-weighted mean because changing one score changes every normalized weight in that row. Then \(\frac{\partial L}{\partial Q}=\frac{(\partial L/\partial S_{\mathrm{score}})K}{\sqrt{d_k}}\), and \(\frac{\partial L}{\partial K}=\frac{(\partial L/\partial S_{\mathrm{score}})^{\mathsf T}Q}{\sqrt{d_k}}\). Shapes must match the corresponding inputs. At \(Q=K=0\), both query/key derivative paths can evaluate to zero even though the output still depends on V; that is another reason to use a nonuniform diagnostic.

Boolean mask meaning belongs to the parameter, not the word PyTorch:

| API parameter | Boolean True means | Typical role |
| --- | --- | --- |
| functional SDPA attn_mask | position participates | allowed query-key relation |
| nn.MultiheadAttention attn_mask | position is forbidden | blocked query-key relation |
| nn.MultiheadAttention key_padding_mask | key is ignored | padding keys per batch |
| paired manual TensorFlow where-mask | score is retained | allowed query-key relation |

The functional and module contracts are documented separately. [PyTorch 2.9 SDPA](https://docs.pytorch.org/docs/2.9/generated/torch.nn.functional.scaled_dot_product_attention.html), [PyTorch 2.9 MultiheadAttention](https://docs.pytorch.org/docs/2.9/generated/torch.nn.MultiheadAttention.html). Inverting polarity does not by itself translate shape: a square query-key mask and a batch-by-key padding mask are different objects. Ignoring padded keys also does not automatically remove padded query outputs from a later loss.

A float mask is an additive score bias, not a Boolean mask expressed as \(\frac{0.0}{1.0}\). Adding one to an allowed score and zero to a forbidden score leaves the latter eligible for softmax. For a hard exclusion convention, the additive representation uses zero for allowed entries and negative infinity for excluded entries. The helper rejects rows with no legal key before calling the kernel so the lesson does not depend on backend-specific all-masked output behavior.

Causality also depends on position alignment. In the square shifted-target fixture, query i may attend to input positions j<=i because its target is the next token. If the target token itself was fed at the same input position without shifting, the diagonal would leak the answer even though the mask looks causal. With a cached prefix and one new query, query position is an offset into the full key history; a freshly constructed 1-by-S upper-left triangle is not automatically the desired cached-decoding mask. State the absolute position relation first.

Prefix invariance should recompute the shorter input, not slice a full attention matrix that already used future data. It is still only a test of the components exercised. Upstream bidirectional features, position-mixing normalization, target construction or contaminated retrieval can leak future information before a correct attention mask sees it. A full decoder needs a corresponding end-to-end boundary test.

Functional SDPA applies dropout according to dropout_p, including when an enclosing module is in evaluation mode. The unchanged helper passes 0 explicitly. A training wrapper must derive the argument from its mode deliberately. This CPU arithmetic fixture does not qualify a fused accelerator backend, memory scaling or generation quality; it establishes the stated finite values and mask behavior.

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

**Expected:** outputs 2, 0; 1, 1; \(\frac{8}{3}\), \(\frac{8}{3}\).

### Example B: Perturb only the future

The causal boundary is verified through behavior. A zeroed future weight plot would not detect every wrong normalization or upstream leak.

```python
future=v.clone(); future[2]=torch.tensor([100.,200.]); changed=attention(q,q,future,allowed)
torch.testing.assert_close(changed[:2],out[:2],atol=1e-12,rtol=0)
torch.testing.assert_close(changed[2],torch.tensor([34.,202/3],dtype=torch.float64),atol=1e-12,rtol=0)
```

**Expected:** first two rows unchanged; last 34, \(\frac{202}{3}\).

### Example C: Recompute nonuniform prefixes

Nonuniform scores exercise query-key arithmetic and scaling. The checker rebuilds the computation on the shorter inputs.

```python
non=torch.tensor([[1.,0.],[0.,1.],[1.,1.]],dtype=torch.float64); full=attention(non,non,v,allowed)
for cut in range(1,4): torch.testing.assert_close(attention(non[:cut],non[:cut],v[:cut],allowed[:cut,:cut]),full[:cut],atol=1e-12,rtol=0)
```

**Expected:** all prefix outputs match within 1e-12.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: outputs 2, 0; 1, 1; \(\frac{8}{3}\), \(\frac{8}{3}\). repeated evaluation matches. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Compute uniform causal mixtures.** Use zero 3-by-2 queries/keys and values 2, 0; 0, 2; 6, 6.
   **Expected:** outputs 2, 0; 1, 1; \(\frac{8}{3}\), \(\frac{8}{3}\).
   **Verify:** Save the assertion results for exercise 1, including outputs 2, 0; 1, 1; \(\frac{8}{3}\), \(\frac{8}{3}\).

2. **Perturb only the future.** Change only the third value to 100, 200.
   **Expected:** first two rows unchanged; last 34, \(\frac{202}{3}\).
   **Verify:** Save the assertion results for exercise 2, including first two rows unchanged; last 34, \(\frac{202}{3}\).

3. **Recompute nonuniform prefixes.** Use \(Q=K\) rows 1, 0; 0, 1; 1, 1 and compare cuts 1..3.
   **Expected:** all prefix outputs match within 1e-12.
   **Verify:** Save the assertion results for exercise 3, including all prefix outputs match within 1e-12.

4. **Reject an all-masked row.** Set the second allowed row to False.
   **Expected:** ValueError before the attention call.
   **Verify:** Save the assertion results for exercise 4, including ValueError before the attention call.

5. **Translate mask polarity explicitly.** Invert the allowed matrix to obtain a forbidden mask for APIs using True as blocked.
   **Expected:** first forbidden row False, True, True.
   **Verify:** Save the assertion results for exercise 5, including first forbidden row False, True, True.

6. **Keep inference dropout disabled.** Repeat functional attention with dropout_p=0 and compare exact outputs.
   **Expected:** repeated evaluation matches.
   **Verify:** Save the assertion results for exercise 6, including repeated evaluation matches.

## Common pitfalls and diagnosis

If values are wrong but prefixes still agree, calculate the nonuniform second-row probabilities and inspect scaling, transpose and softmax axis. If a future perturbation changes earlier rows, check mask polarity, position offsets and any upstream features that already mixed positions. A triangular display cannot establish those contracts.

If padded query outputs affect the objective, inspect the loss participation mask separately from the key mask. If evaluation changes between calls, inspect the functional dropout argument as well as module mode and RNG. If gradients are zero on the uniform fixture, replace zero Q/K with the declared nonuniform case before diagnosing a disconnected graph. Keep the helper's all-masked rejection and finite-input checks instead of widening tolerances around undefined or unreviewed cases.

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



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-022, Attention, transformer masks and information boundaries.
Read courses/deep-learning-pytorch/guides/torch-022.md and courses/deep-learning-pytorch/lessons/torch-022.py. Direct prerequisites: `torch-021`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
