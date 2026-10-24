# llm-applied-016: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Low-rank adaptation, or LoRA, freezes a base linear weight and learns an additive update represented by two smaller matrices. It changes the model's function through weight adaptation, while retrieval changes which evidence is supplied at inference time. LoRA is therefore a method for learning task behavior from examples, not a substitute for keeping a changing domain corpus current or enforcing access control on retrieved documents.

Use the row-vector convention \(Y=X(W+sAB)\), where X is [N, Din], W is [Din, Dout], A is [Din, r], B is [r, Dout], and \(s=\frac{\alpha}{r}\). Every product must preserve those contracts: XA is [N, r], (XA)B is [N, Dout], and AB is [Din, Dout]. The update rank is at most r, because its columns lie in the column space of A. At most is a bound, not a guarantee that training uses all r directions. The effective rank can be smaller because factors are rank deficient or because the data and gradient updates preserve a symmetry.

The chapter deliberately chooses \(W=I_{8}\), A filled with \(\frac{1}{8}\), \(B=0\), rank 2 and alpha 4. This preserves the base function initially, allows every first-step derivative to be calculated by hand, and produces a real PyTorch SGD update. The symmetric A columns lead to equal B rows after the first step, so this particular update has rank one even though its parameterization allows rank two. That is a useful limitation to inspect rather than a claim that every rank-two adapter behaves this way.

Only A and B are optimized. The frozen base remains part of the forward computation and can still carry derivatives to earlier trainable operations. Freezing its parameters is not the same as disabling gradient recording for the whole forward pass. The lesson separates parameter ownership, function preservation, gradient flow, rank and inference merging so a successful adapter update is not confused with demonstrated domain-assistant quality.

**Adapter rank:** The inner dimension bounding, but not guaranteeing, the rank of the learned update.

**LoRA scale:** The multiplier \(\frac{\alpha}{r}\) used in this forward function and its gradients.

**Frozen base:** Weights excluded from updates while still participating in the differentiable forward computation.

**Merged inference:** Using a separately constructed effective weight W+sAB under a checked inference contract.

## Reading the implementation

### Orientation and parameter accounting

A base [Din, Dout] matrix contains \(D_{\mathrm{in}}\cdot D_{\mathrm{out}}\) entries. The factors contain \(r\cdot (D_{\mathrm{in}}+D_{\mathrm{out}})\). For this 8-by-8 example and \(r=2\), the base has 64 entries and the adapter has 32. For a square width d the ratio is \(\frac{2r}{d}\), so a width-4096, rank-8 adapter has 65, 536 entries versus 16, 777, 216 base entries, a ratio of \(\frac{1}{256}\). That counts these matrices only; it is not a measured total-memory reduction.

PyTorch Linear stores a weight with shape [Dout, Din] and applies its transpose to row inputs. In that storage convention a typical update is B_pt A_pt, where A_pt is [r, Din] and B_pt is [Dout, r]. The course factors are \(A={A_{\mathrm{pt}}}^{T}\) and \(B={B_{\mathrm{pt}}}^{T}\), making \((B_{\mathrm{pt}}A_{\mathrm{pt}})^{\mathsf T}=AB\). Copying factor names from another implementation without translating the orientation can produce a shape error or, for square matrices, a silently different function.

### Deriving both factor gradients

Let \(G=\frac{\partial L}{\partial Y}\) have shape [N, Dout]. The adapter branch is \(s(XA)B\). Matrix differentiation gives \(\frac{\partial L}{\partial B}=s(XA)^{\mathsf T}G\), with shape [r, Dout]. The gradient for A is \(\frac{\partial L}{\partial A}=sX^{\mathsf T}GB^{\mathsf T}\), with shape [Din, r]. The input derivative is \(G(W+sAB)^{\mathsf T}\), so the frozen W still contributes to gradient propagation toward earlier layers even though W itself is not updated.

At initialization \(B=0\). Therefore the A gradient is a connected tensor of zeros because its formula contains \({B}^{T}\). The B gradient can be nonzero because A is nonzero. If both factors start at zero, both gradients are zero and this ordinary gradient-based update cannot escape that point. A zero gradient and a missing gradient are different diagnoses: PyTorch can return an all-zero tensor for a connected parameter, while None can indicate that no derivative was accumulated for that parameter.

### Calculate the exact first step

The input X is a row of eight ones, so \(XA=[1,1]\). With \(B=0\) and \(W=I_{8}\), Y is a row of eight ones. The loss is the mean of eight squared outputs against zero: \(L=1\). The output derivative is \(G=\frac{2Y}{8}\), so every entry is \(\frac{1}{4}\). With \(s=2\), every B-gradient entry is \(2\cdot 1\cdot \frac{1}{4}=\frac{1}{2}\), and every A-gradient entry is zero.

SGD with learning rate 0.1 changes every B entry to -0.05 and leaves A at 0.125. Each entry of AB is \(2\cdot 0.125\cdot (-0.05)=-0.0125\). Multiplication by s gives an effective update of -0.025 in every base-matrix entry. Multiplying by the eight-one input sums eight such contributions, producing \(Y_{\mathrm{new}}=0.8\) in every output coordinate. The new mean squared loss is therefore \({0.8}^{2}=0.64\). The reference checks these values, not merely that something changed or that a loss happened to decrease.

The gradient denominator is essential. Using summed squared error instead of a mean multiplies G and both factor gradients by eight under this fixture. With the same learning rate, that is a different optimization step. Likewise, changing alpha without compensating elsewhere changes the forward update scale and the gradients; alpha is not just metadata attached to an adapter file.

## Exercise 1: Count and orient parameters

The question is: Construct \(W=I_{8}\), A=ones(8, 2)/8, B=zeros(2, 8), rank 2 and alpha 4, then count stored entries.

The orientation is chosen for row-vector inputs. A framework Linear layer storing(out, in) weights would require a transposed formulation rather than copying these shapes blindly.

```python
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

**Verify:** Compare the computed values or written argument with 64 base entries, 32 trainable adapter entries and scale 2.

## Exercise 2: Prove zero-delta initialization

The question is: Compare the effective output with the frozen base before any update.

The initial adapter does not perturb the base. This is useful for controlled comparisons and explains why one factor starts at zero.

```python
initial = x @ (w + scale * (a @ b))
saved = w.clone()
assert torch.equal(initial, x @ w)
assert torch.equal(a @ b, torch.zeros((8, 8)))
```

**Expected:** Both outputs equal a row of eight ones; the initial update matrix is zero.

**Verify:** Compare the computed values or written argument with Both outputs equal a row of eight ones; the initial update matrix is zero.

## Exercise 3: Inspect the first gradients

The question is: Differentiate the mean squared output against a zero target and inspect both factor gradients.

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

**Verify:** Compare the computed values or written argument with A has a connected zero gradient; every B-gradient entry is 0.5; W has no accumulated gradient.

## Exercise 4: Take an adapter-only step

The question is: Take one SGD step of size 0.1 on A and B and derive the updated output and objective.

The first update changes B from zero to -0.05 and leaves A unchanged. The scaled update matrix has -0.025 in every entry, so an eight-one input loses 0.2 from each output coordinate. The new output is 0.8 and its mean squared loss is 0.64. A summed loss would change this gradient scale and would require a different numerical prediction.

```python
before_b = b.detach().clone()
optimizer = torch.optim.SGD([a, b], lr=0.1)
optimizer.step()
after = x @ (w + scale * (a @ b))
assert not torch.equal(before_b, b)
torch.testing.assert_close(b, torch.full((2, 8), -0.05), atol=1e-6, rtol=0)
torch.testing.assert_close(after, torch.full((1, 8), 0.8), atol=1e-6, rtol=0)
torch.testing.assert_close(after.square().mean(), torch.tensor(0.64), atol=1e-6, rtol=0)
assert torch.equal(w, saved)
```

**Expected:** B entries become -0.05, outputs become 0.8 and mean squared loss becomes 0.64; W stays exactly unchanged.

**Verify:** Compare the computed values or written argument with B entries become -0.05, outputs become 0.8 and mean squared loss becomes 0.64; W stays exactly unchanged.

## Exercise 5: Merge without changing the base

The question is: Create a detached merged matrix without mutating W and compare its predictions.

Merging is an inference representation change. Preserve adapter and base identities so the artifact can be reconstructed or replaced without contaminating shared state.

```python
merged = w.detach().clone() + scale * (a @ b).detach()
torch.testing.assert_close(x @ merged, after.detach(), atol=1e-6, rtol=0)
assert torch.equal(w, saved)
```

**Expected:** Merged/unmerged parity within 1e-6; original W remains exactly unchanged.

**Verify:** Compare the computed values or written argument with Merged/unmerged parity within 1e-6; original W remains exactly unchanged.

## Exercise 6: Inspect rank and scaling consequences

The question is: Measure the update rank after this symmetric first step and compare alpha 4 with alpha 2 using the same factors.

Rank r is an upper bound. Equal A columns and equal B rows make this particular nonzero matrix rank one. The result does not contradict the rank-two parameterization, but it warns against assuming every adapter uses all configured directions. The scale comparison holds factors fixed; independently retraining with another alpha would generally change those factors too.

```python
delta = (a @ b).detach()
assert int(torch.linalg.matrix_rank(delta)) == 1
assert int(torch.linalg.matrix_rank(delta)) <= rank
torch.testing.assert_close((4 / rank) * delta, 2 * ((2 / rank) * delta), atol=1e-6, rtol=0)
```

**Expected:** The actual update has rank 1, within the configured bound 2; alpha 4 gives twice the alpha-2 delta.

**Verify:** Compare the computed values or written argument with The actual update has rank 1, within the configured bound 2; alpha 4 gives twice the alpha-2 delta.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
