# llm-applied-016: Low-rank adaptation: dimensions, gradients and a real update

## Level and prerequisites

Advanced; approximately 240 minutes. Direct prerequisites: `llm-applied-015`, `llm-032`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

LoRA constrains a model update to a factorized subspace while retaining the frozen base computation. This chapter connects the matrix derivation to a domain-adaptation decision, explains why placement and scaling matter, and follows the adapter from initialization through evaluation and inference merging.

## Purpose and mental model

Low-rank adaptation, or LoRA, freezes a base linear weight and learns an additive update represented by two smaller matrices. It changes the model's function through weight adaptation, while retrieval changes which evidence is supplied at inference time. LoRA is therefore a method for learning task behavior from examples, not a substitute for keeping a changing domain corpus current or enforcing access control on retrieved documents.

Use the row-vector convention \(Y=X(W+sAB)\), where X is [N, Din], W is [Din, Dout], A is [Din, r], B is [r, Dout], and \(s=\frac{\alpha}{r}\). Every product must preserve those contracts: XA is [N, r], (XA)B is [N, Dout], and AB is [Din, Dout]. The update rank is at most r, because its columns lie in the column space of A. At most is a bound, not a guarantee that training uses all r directions. The effective rank can be smaller because factors are rank deficient or because the data and gradient updates preserve a symmetry.

The chapter deliberately chooses \(W=I_{8}\), A filled with \(\frac{1}{8}\), \(B=0\), rank 2 and alpha 4. This preserves the base function initially, allows every first-step derivative to be calculated by hand, and produces a real PyTorch SGD update. The symmetric A columns lead to equal B rows after the first step, so this particular update has rank one even though its parameterization allows rank two. That is a useful limitation to inspect rather than a claim that every rank-two adapter behaves this way.

Only A and B are optimized. The frozen base remains part of the forward computation and can still carry derivatives to earlier trainable operations. Freezing its parameters is not the same as disabling gradient recording for the whole forward pass. The lesson separates parameter ownership, function preservation, gradient flow, rank and inference merging so a successful adapter update is not confused with demonstrated domain-assistant quality.

## Constrain the update without changing the task definition

The Methods Desk team has a stable extraction-format gap and a reviewed dataset. Full SFT makes all model parameters available to the optimizer. LoRA offers another hypothesis: perhaps the required behavior can be learned through a smaller additive update at selected linear transformations. This is a restriction on the adaptation mechanism, not a change in what counts as a correct supported answer.

In the row-vector convention used here, the effective map is \(X(W+sAB)\). W is the frozen base, A maps the input features into r intermediate directions, B maps those directions to the output, and \(s=\frac{\alpha}{r}\) controls their scale. The trainable factors contain \(r\cdot (D_{\mathrm{in}}+D_{\mathrm{out}})\) entries instead of \(D_{\mathrm{in}}\cdot D_{\mathrm{out}}\) entries for a free full matrix update. The product AB has rank at most r.

That bound is a capacity statement about one update matrix. It does not prove that the task needs only r directions, that training uses all of them or that a small rank is universally sufficient. The original LoRA work provides empirical evidence for the method on particular models and tasks; the small fixture below supplies an independently checkable instance of its mechanics. [LoRA](https://arxiv.org/abs/2106.09685).

## Initialization creates a useful controlled starting point

Starting B at zero makes the initial additive update zero, so the adapter preserves the base function before training. A is nonzero so B can receive a useful first gradient. If both factors were zero, the ordinary factor gradients would also be zero in this branch and that update rule would remain stuck at the initial product.

The apparently asymmetric first step is therefore expected. The derivative for A contains B, so A's first gradient can be a connected zero while B's gradient is nonzero. That is different from a missing gradient caused by detach, an absent parameter or an optimizer that does not own the factor. The exact example derives every B-gradient entry as 0.5 and the first updated output as 0.8, giving a concrete anchor for that reasoning.

The example's symmetric factors produce a rank-one update within a rank-two parameterization. This is useful evidence about the realized product. It prevents a common interpretive mistake: treating configured rank as a guarantee that every direction became independently useful. Factor columns also do not have uniquely identified semantic meanings, because multiple factorizations can represent the same product.

## Placement determines what the adapter can change

An output-head adapter changes how existing hidden representations are mapped to vocabulary scores. An adapter in attention projections can affect another part of the computation, while feed-forward or embedding adaptations reach still different transformations. The same rank number at different target modules therefore describes different hypothesis classes and parameter budgets.

For the Methods Desk, a formatting failure and a failure to distinguish two domain concepts may respond differently to those choices. If the hidden representation already separates the relevant cases, a narrow output adaptation might be enough. If the model does not represent the distinction needed by the task, a final projection alone may be limited. Those are testable hypotheses, not guarantees based on module names.

Rank and scale should be considered together. Increasing rank while keeping alpha fixed changes the \(\frac{\alpha}{r}\) multiplier, as well as the number and initialization of the factors. Comparing two configurations without recording those choices can attribute a difference to rank while several parts of the effective update changed. Learning rate, target modules, dropout and data weighting add further conditions to the comparison.

## Frozen weights can still carry gradients

Freezing W means its values are not updated by the optimizer. It does not generally mean that the forward operation involving W should run outside autograd. Suppose an earlier trainable stage produces h=f_phi(x), followed by y=hW. The derivative with respect to phi still depends on propagation through W, even when W is treated as a constant.

Putting the whole hW operation under no_grad would remove that path to the earlier trainable stage. This distinction matters when adapters appear at several depths in a model. The correct freezing policy controls parameter updates while preserving the computation graph needed by the trainable parts. The literal matrix fixture has a simpler dependency structure, but its derivative formulas make the principle visible.

Optimizer membership must match the intended trainable set. A factor with requires_grad=True is not updated unless the optimizer owns it and step is called. Conversely, a mistaken explicit assignment can alter a supposedly frozen base even when its gradient flag is False. Parameter counts, ownership checks and before/after base comparisons provide complementary evidence.

## Merge only under a declared inference contract

In exact arithmetic, the factorized expression XW+\(s(XA)B\) equals \(X(W+sAB)\). A merged matrix can therefore represent the same linear function for inference. In floating-point arithmetic, reassociation and quantization can change the result, so compare outputs in the intended dtype and model mode under a justified tolerance.

Keep the original base separate when it is shared among adapters. An in-place merge can change the starting point for another adapter and make the artifact identity misleading. The saved configuration should identify the base revision, factor shapes, rank, scale, target modules, tokenizer and relevant runtime conditions. Matching tensor shapes alone does not prove that an adapter belongs to a particular base checkpoint.

Trainable-parameter savings also need a precise interpretation. The frozen base still occupies storage and participates in forward computation. Activations and attention intermediates may dominate memory for long contexts. The factor-count ratio is useful arithmetic, while peak memory and latency require measurements on the actual backend. The next chapter examines how quantizing the frozen base changes those accounting and numerical questions without changing the need for independent task evaluation.

## Design decisions and when to use this method

Use LoRA when the task requires learning a repeatable behavior or representation change and a constrained update is a useful tradeoff. Examples include a stable output format, domain-specific extraction conventions or a measured task requiring adaptation beyond available prompts. For frequently changing factual content, start by improving retrieval and evidence handling. For sensitive subject matter, evaluate supported answers, refusal and abstention behavior, not only training loss.

Choose target modules deliberately. Adapting query and value projections, all attention projections, feed-forward matrices or embeddings gives different parameter counts and different places to change the computation. The same rank value does not imply the same capacity across these choices. Compare rank and target-module choices under a fixed data split and scoring rule. A single toy objective cannot establish a universally best rank or learning rate.

Parameter savings affect optimizer state and trainable gradients, but the frozen base must still be stored and used. Forward activations, intermediate adapter activations, attention buffers and checkpointing strategy also contribute to memory. For the width-4096 arithmetic example, float32 base weights alone occupy 64 MiB and the two adapter factors occupy 0.25 MiB. Those are storage calculations for one pair of matrices, not GPU peak-memory measurements. Adam-like optimization can add moments for trainable parameters, and mixed-precision or quantized implementations add their own state and kernels.

Merging computes a new effective weight W+sAB for inference. Do it into a separate artifact when the original base is shared by other adapters. Test the merged and unmerged computations in the intended dtype and model mode. In finite precision, changing multiplication order or quantizing the merged result can change outputs within or beyond an allowed tolerance. Adapter dropout, if used during training, should follow the model's evaluation contract before comparing inference parity. Store base revision, tokenizer identity, rank, scale, target modules, training-data identity and relevant software versions with the adapter.

## Vocabulary and concepts

**Adapter rank:** The inner dimension bounding, but not guaranteeing, the rank of the learned update.

**LoRA scale:** The multiplier \(\frac{\alpha}{r}\) used in this forward function and its gradients.

**Frozen base:** Weights excluded from updates while still participating in the differentiable forward computation.

**Merged inference:** Using a separately constructed effective weight W+sAB under a checked inference contract.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-016/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. Use the Docker classroom as the default route and select the declared `llm-torch-cpu` profile. For a separately prepared native environment, invoke its explicitly selected interpreter on `courses/llm-applied/lessons/llm-applied-016.py` from the repository root. The general repository `.venv` is not assumed to include the heavy model dependencies.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the tolerance stated in each assertion. Many analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone does not determine a universal error bound. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

### Orientation and parameter accounting

A base [Din, Dout] matrix contains \(D_{\mathrm{in}}\cdot D_{\mathrm{out}}\) entries. The factors contain \(r\cdot (D_{\mathrm{in}}+D_{\mathrm{out}})\). For this 8-by-8 example and \(r=2\), the base has 64 entries and the adapter has 32. For a square width d the ratio is \(\frac{2r}{d}\), so a width-4096, rank-8 adapter has 65,536 entries versus 16,777,216 base entries, a ratio of \(\frac{1}{256}\). That counts these matrices only; it is not a measured total-memory reduction.

PyTorch Linear stores a weight with shape [Dout, Din] and applies its transpose to row inputs. In that storage convention a typical update is B_pt A_pt, where A_pt is [r, Din] and B_pt is [Dout, r]. The course factors are \(A={A_{\mathrm{pt}}}^{T}\) and \(B={B_{\mathrm{pt}}}^{T}\), making \((B_{\mathrm{pt}}A_{\mathrm{pt}})^{\mathsf T}=AB\). Copying factor names from another implementation without translating the orientation can produce a shape error or, for square matrices, a silently different function.

### Deriving both factor gradients

Let \(G=\frac{\partial L}{\partial Y}\) have shape [N, Dout]. The adapter branch is \(s(XA)B\). Matrix differentiation gives \(\frac{\partial L}{\partial B}=s(XA)^{\mathsf T}G\), with shape [r, Dout]. The gradient for A is \(\frac{\partial L}{\partial A}=sX^{\mathsf T}GB^{\mathsf T}\), with shape [Din, r]. The input derivative is \(G(W+sAB)^{\mathsf T}\), so the frozen W still contributes to gradient propagation toward earlier layers even though W itself is not updated.

At initialization \(B=0\). Therefore the A gradient is a connected tensor of zeros because its formula contains \({B}^{T}\). The B gradient can be nonzero because A is nonzero. If both factors start at zero, both gradients are zero and this ordinary gradient-based update cannot escape that point. A zero gradient and a missing gradient are different diagnoses: PyTorch can return an all-zero tensor for a connected parameter, while None can indicate that no derivative was accumulated for that parameter.

### Calculate the exact first step

The input X is a row of eight ones, so \(XA=[1,1]\). With \(B=0\) and \(W=I_{8}\), Y is a row of eight ones. The loss is the mean of eight squared outputs against zero: \(L=1\). The output derivative is \(G=\frac{2Y}{8}\), so every entry is \(\frac{1}{4}\). With \(s=2\), every B-gradient entry is \(2\cdot 1\cdot \frac{1}{4}=\frac{1}{2}\), and every A-gradient entry is zero.

SGD with learning rate 0.1 changes every B entry to -0.05 and leaves A at 0.125. Each entry of AB is \(2\cdot 0.125\cdot (-0.05)=-0.0125\). Multiplication by s gives an effective update of -0.025 in every base-matrix entry. Multiplying by the eight-one input sums eight such contributions, producing \(Y_{\mathrm{new}}=0.8\) in every output coordinate. The new mean squared loss is therefore \({0.8}^{2}=0.64\). The reference checks these values, not merely that something changed or that a loss happened to decrease.

The gradient denominator is essential. Using summed squared error instead of a mean multiplies G and both factor gradients by eight under this fixture. With the same learning rate, that is a different optimization step. Likewise, changing alpha without compensating elsewhere changes the forward update scale and the gradients; alpha is not just metadata attached to an adapter file.

## Worked example / walkthrough

### Example A: Count and orient parameters

The orientation is chosen for row-vector inputs. A framework Linear layer storing(out, in) weights would require a transposed formulation rather than copying these shapes blindly.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

w = torch.eye(8)
a = nn.Parameter(torch.ones((8, 2)) / 8)
b = nn.Parameter(torch.zeros((2, 8)))
rank = 2
alpha = 4
scale = alpha / rank
x = torch.ones((1, 8))
assert w.numel() == 64
assert a.numel() + b.numel() == 32
assert scale == 2
```

**Expected:** 64 base entries, 32 trainable adapter entries and scale 2.

### Example B: Prove zero-delta initialization

The initial adapter does not perturb the base. This is useful for controlled comparisons and explains why one factor starts at zero.

```python
initial = x @ (w + scale * (a @ b))
saved = w.clone()
assert torch.equal(initial, x @ w)
assert torch.equal(a @ b, torch.zeros((8, 8)))
```

**Expected:** Both outputs equal a row of eight ones; the initial update matrix is zero.

### Example C: Inspect the first gradients

The derivative for A contains B transpose, so it is zero at \(B=0\) while remaining connected to the graph. The derivative for B is s(XA) transpose times G. Here \(XA=[1,1]\), G is eight copies of \(\frac{1}{4}\) and \(s=2\), giving 0.5 in every entry. This independent arithmetic is more diagnostic than only checking whether a gradient is nonzero.

```python
loss = initial.square().mean()
loss.backward()
assert a.grad is not None and b.grad is not None
assert torch.count_nonzero(a.grad).item() == 0
torch.testing.assert_close(b.grad, torch.full((2, 8), 0.5), atol=1e-6, rtol=0)
assert w.grad is None
```

**Expected:** A has a connected zero gradient; every B-gradient entry is 0.5; W has no accumulated gradient.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: 64 base entries, 32 trainable adapter entries and scale 2. The actual update has rank 1, within the configured bound 2; alpha 4 gives twice the alpha-2 delta. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Count and orient parameters.** Construct \(W=I_{8}\), A=ones(8, 2)/8, B=zeros(2, 8), rank 2 and alpha 4, then count stored entries.
   **Expected:** 64 base entries, 32 trainable adapter entries and scale 2.
   **Verify:** Save the assertion results for exercise 1, including 64 base entries, 32 trainable adapter entries and scale 2.

2. **Prove zero-delta initialization.** Compare the effective output with the frozen base before any update.
   **Expected:** Both outputs equal a row of eight ones; the initial update matrix is zero.
   **Verify:** Save the assertion results for exercise 2, including Both outputs equal a row of eight ones; the initial update matrix is zero.

3. **Inspect the first gradients.** Differentiate the mean squared output against a zero target and inspect both factor gradients.
   **Expected:** A has a connected zero gradient; every B-gradient entry is 0.5; W has no accumulated gradient.
   **Verify:** Save the assertion results for exercise 3, including A has a connected zero gradient; every B-gradient entry is 0.5; W has no accumulated gradient.

4. **Take an adapter-only step.** Take one SGD step of size 0.1 on A and B and derive the updated output and objective.
   **Expected:** B entries become -0.05, outputs become 0.8 and mean squared loss becomes 0.64; W stays exactly unchanged.
   **Verify:** Save the assertion results for exercise 4, including B entries become -0.05, outputs become 0.8 and mean squared loss becomes 0.64; W stays exactly unchanged.

5. **Merge without changing the base.** Create a detached merged matrix without mutating W and compare its predictions.
   **Expected:** Merged/unmerged parity within 1e-6; original W remains exactly unchanged.
   **Verify:** Save the assertion results for exercise 5, including Merged/unmerged parity within 1e-6; original W remains exactly unchanged.

6. **Inspect rank and scaling consequences.** Measure the update rank after this symmetric first step and compare alpha 4 with alpha 2 using the same factors.
   **Expected:** The actual update has rank 1, within the configured bound 2; alpha 4 gives twice the alpha-2 delta.
   **Verify:** Save the assertion results for exercise 6, including The actual update has rank 1, within the configured bound 2; alpha 4 gives twice the alpha-2 delta.

## Common pitfalls and diagnosis

If the initial adapter changes the base output unexpectedly, inspect whether one factor is actually zero and whether an extra bias or dropout is active. If A has a zero first gradient but B has a nonzero gradient, that matches the derived initialization. If both gradients are zero, inspect the factor initialization, the objective and whether the output derivative is zero. If a gradient is None, inspect requires_grad, detach and the recorded graph before blaming the low-rank parameterization.

If the base changes, check optimizer membership and any in-place merge. If earlier adapters stop receiving gradients through a frozen layer, check whether an over-broad no_grad context removed the required input derivative path. Frozen weights can remain constants in a differentiable computation; disabling every operation is a stronger change.

If the rank is lower than configured, inspect factor singular values and initialization symmetry. This fixture intentionally produces rank one after its first update. If merged predictions differ, verify factor orientation, \(\frac{\alpha}{r}\), base revision, dtype and evaluation mode before increasing tolerances. Finally, if training metrics improve but supported-answer quality does not, inspect the data, masking and held-out task design. The repository's optional pretrained generation probe demonstrates that mechanically successful adaptation can still produce an incorrect formula despite supplied evidence.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Revisit the worked examples, then close them. Explain Adapter rank, LoRA scale, Frozen base using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-015`, `llm-032` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [LoRA](https://arxiv.org/abs/2106.09685), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.

## Independent NumPy audit of the first gradient

This additional calculation is standalone. It uses float64 algebra and a central finite difference to check the derivative independently of autograd. It does not train a second language model or replace the actual PyTorch update above.

```python
import numpy as np

x = np.ones((1, 8), dtype=np.float64)
w = np.eye(8, dtype=np.float64)
a = np.full((8, 2), 1 / 8, dtype=np.float64)
b = np.zeros((2, 8), dtype=np.float64)
scale = 2.0


def objective(first, second):
    prediction = x @ (w + scale * first @ second)
    return np.mean(prediction ** 2)


prediction = x @ (w + scale * a @ b)
grad_output = 2 * prediction / prediction.size
grad_b = scale * (x @ a).T @ grad_output
grad_a = scale * x.T @ grad_output @ b.T
np.testing.assert_array_equal(grad_a, np.zeros_like(a))
np.testing.assert_allclose(grad_b, 0.5, atol=1e-12, rtol=0)

step = 1e-6
positive = b.copy()
negative = b.copy()
positive[0, 0] += step
negative[0, 0] -= step
finite_difference = (objective(a, positive) - objective(a, negative)) / (2 * step)
np.testing.assert_allclose(finite_difference, grad_b[0, 0], atol=1e-9, rtol=0)

updated_b = b - 0.1 * grad_b
updated_output = x @ (w + scale * a @ updated_b)
np.testing.assert_allclose(updated_output, 0.8, atol=1e-12, rtol=0)
np.testing.assert_allclose(objective(a, updated_b), 0.64, atol=1e-12, rtol=0)
assert np.linalg.matrix_rank(a @ updated_b) == 1

zero_a = np.zeros_like(a)
zero_b = np.zeros_like(b)
zero_grad_b = scale * (x @ zero_a).T @ grad_output
zero_grad_a = scale * x.T @ grad_output @ zero_b.T
np.testing.assert_array_equal(zero_grad_a, zero_a)
np.testing.assert_array_equal(zero_grad_b, zero_b)
```

**Expected:** the analytic and finite-difference B derivative agree at 0.5; the first update gives output 0.8 and loss 0.64; setting both factors to zero leaves both factor derivatives zero.

The distinction between rank bound and realized rank also has a geometric interpretation. For any invertible r-by-r matrix R, the factors AR and R-inverse B represent the same product AB. The factorization is not unique, so interpreting one column of A as a uniquely identified semantic concept is generally unjustified. Different initialization, regularization and optimization paths can select different equivalent or approximately equivalent factors.

The [original LoRA paper](https://arxiv.org/abs/2106.09685) supplies the adaptation method and scaling convention used here. [QLoRA](https://arxiv.org/abs/2305.14314) adds a quantized frozen base and specific storage/training techniques; it is not equivalent to this unquantized matrix example. The next chapter distinguishes storage codes, dequantized computation, adapter gradients and actual GPU implementation claims. Neither a rank count nor the successful one-step fixture establishes that an adapted assistant follows domain evidence reliably.


## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-016, Low-rank adaptation: dimensions, gradients and a real update.
Read courses/llm-applied/guides/llm-applied-016.md and courses/llm-applied/lessons/llm-applied-016.py. Direct prerequisites: `llm-applied-015`, `llm-032`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
