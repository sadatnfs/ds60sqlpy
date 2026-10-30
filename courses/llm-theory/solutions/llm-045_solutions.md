# llm-045: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Normalization placement changes the residual network's gradient path. A pre-norm block computes x+F(Norm(x)), leaving an explicit identity path around the transformed branch. A post-norm block computes Norm(x+F(x)), so the normalizer lies on the combined residual path. With a zero branch, pre-norm is exactly the identity while post-norm still changes the input. This local observation helps explain optimization behavior, but it does not establish a universal best architecture or learning-rate schedule.

RMSNorm divides by root-mean-square magnitude without subtracting the feature mean. LayerNorm subtracts the mean and normalizes centered variance. Their invariances differ: adding a constant to every feature leaves LayerNorm's centered values unchanged, but generally changes RMSNorm. Both typically use learned gain and an epsilon whose placement matters numerically.

A gated feed-forward network multiplies two projections. SwiGLU uses SiLU(xWg) elementwise multiplied by xWu, then projects back with Wd. It has three weight matrices rather than the two of a plain feed-forward block. A fair parameter comparison must adjust hidden widths or acknowledge the larger budget. This lesson uses actual PyTorch autograd to inspect normalization Jacobians and gate gradients.

**Pre-norm:** Normalization inside the transformed residual branch.

**Post-norm:** Normalization applied after combining residual and branch.

**RMSNorm:** Normalization by root-mean-square magnitude without mean subtraction.

**SwiGLU:** A gated feed-forward transformation using aSiLU-activated gate.

**Jacobian:** The matrix of output sensitivities to input coordinates.

## Reading the implementation

All examples use float64 and small feature widths. RMSNorm computes \(\frac{x}{\sqrt{\operatorname{mean}({x}^{2})+\epsilon}}\) times gain. LayerNorm computes \(\frac{x-\operatorname{mean}(x)}{\sqrt{\operatorname{mean}((x-\operatorname{mean}(x))^2)+\epsilon}}\). A pre/post comparison uses a zero linear branch so the residual distinction is isolated. SwiGLU uses F.silu for the gate projection and an elementwise product with the up projection. Check the three matrix shapes before counting parameters or requesting gradients.

## Exercise 1: Compare RMSNorm and LayerNorm

The question is: Normalize vector [3, 4] with unit gain and epsilon 1e-8.

The two methods normalize different statistics. Equal output shape does not imply that one is a drop-in numerical replacement for the other.

```python
x = torch.tensor([3.0, 4.0], dtype=torch.float64)
rms = rms_norm(x)
centered = layer_norm(x)
assert abs(rms.mean().item()) > 0.5
np.testing.assert_allclose(centered.mean().item(), 0, atol=1e-12, rtol=0)
np.testing.assert_allclose(
    rms.detach().numpy(), np.array([3.0, 4.0]) / np.sqrt(12.5 + 1e-8), atol=1e-12, rtol=0
)
```

**Expected:** RMSNorm mean nonzero; LayerNorm mean approximately 0.

**Verify:** Compare the computed values or written argument with RMSNorm mean nonzero; LayerNorm mean approximately 0.

## Exercise 2: Trace pre/post residual Jacobians

The question is: Set the transformed branch to zero and compare pre-norm x with post-norm LayerNorm(x).

The zero-branch control isolates placement. LayerNorm removes a common feature shift, so its derivative along the all-ones direction is zero rather than identity.

```python
value = torch.tensor([1.0, 2.0, 4.0], dtype=torch.float64, requires_grad=True)
pre = torch.autograd.functional.jacobian(lambda z: z + 0 * layer_norm(z), value)
post = torch.autograd.functional.jacobian(lambda z: layer_norm(z + 0 * z), value)
torch.testing.assert_close(pre, torch.eye(3, dtype=torch.float64), atol=1e-12, rtol=0)
torch.testing.assert_close(
    post @ torch.ones(3, dtype=torch.float64),
    torch.zeros(3, dtype=torch.float64),
    atol=1e-10,
    rtol=0,
)
```

**Expected:** pre-norm Jacobian is identity; post-norm Jacobian annihilates a constant feature shift.

**Verify:** Compare the computed values or written argument with pre-norm Jacobian is identity; post-norm Jacobian annihilates a constant feature shift.

## Exercise 3: Calculate a SwiGLU gate derivative

The question is: Use scalar \(g=0\), \(u=2\) and output SiLU(g)*u.

At zero, SiLU has derivative one-half. Multiplication by up2 gives gate gradient 1, while the up branch sees the zero gate value. A connected zero gradient is not a missing path.

```python
gate = torch.tensor(0.0, dtype=torch.float64, requires_grad=True)
up = torch.tensor(2.0, dtype=torch.float64, requires_grad=True)
output = F.silu(gate) * up
output.backward()
assert output.item() == 0 and gate.grad.item() == 1 and up.grad.item() == 0
```

**Expected:** output 0; gradient with respect to g is 1; with respect to u is 0.

**Verify:** Compare the computed values or written argument with output 0; gradient with respect to g is 1; with respect to u is 0.

## Exercise 4: Check the RMSNorm Jacobian formula

The question is: Compare autograd with \(J=\frac{I}{r}-\frac{xx^{\mathsf T}}{d\cdot {r}^{3}}\) at x=[1, 2, 3].

The derivative contains a direct coordinate term andacoupling term through the sharedRMSdenominator. Omitting the coupling would treat normalization as constant scaling and produce incorrect gradients.

```python
value = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float64, requires_grad=True)
r = torch.sqrt(value.square().mean() + 1e-8)
width = value.numel()
analytic = torch.eye(width, dtype=torch.float64) / r - torch.outer(value, value) / (width * r**3)
automatic = torch.autograd.functional.jacobian(rms_norm, value)
torch.testing.assert_close(automatic, analytic, atol=1e-10, rtol=0)
```

**Expected:** matrices agree within 1e-10.

**Verify:** Compare the computed values or written argument with matrices agree within 1e-10.

## Exercise 5: Match feed-forward parameter budgets

The question is: Compare plain FFN model width \(d=4\), hidden 6 with SwiGLU hidden width 4, excluding biases; execute a gated block with input and output width 4.

Matching hidden widths would not match parameter counts. The2/3 width relation is a budget arithmetic rule here, not a universal model-quality prescription.

```python
d = 4
plain_hidden = 6
gated_hidden = 4
assert 2 * d * plain_hidden == 3 * d * gated_hidden == 48
inputs = torch.tensor([[1.0, 0.0, -1.0, 2.0], [0.0, 1.0, 2.0, -1.0]], dtype=torch.float64)
wg = torch.eye(4, dtype=torch.float64)
wu = 2 * wg
wd = 0.5 * wg
result = (F.silu(inputs @ wg) * (inputs @ wu)) @ wd
assert tuple(result.shape) == (2, 4) and torch.isfinite(result).all()
```

**Expected:** both 48 weight entries; output shape(2, 4).

**Verify:** Compare the computed values or written argument with both 48 weight entries; output shape(2, 4).

## Exercise 6: Test invariance and zero-vector boundaries

The question is: Shift x=[1, 2, 3] by 5, compare the two normalizers, and normalize zero.

Epsilon handles zero magnitude, but does not create the mean-subtraction invariance thatRMSNorm deliberately omits. These invariants clarify what information each normalizer removes.

```python
base = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float64)
torch.testing.assert_close(layer_norm(base + 5), layer_norm(base), atol=1e-12, rtol=0)
assert not torch.allclose(rms_norm(base + 5), rms_norm(base))
assert torch.isfinite(rms_norm(torch.zeros(3, dtype=torch.float64))).all()
```

**Expected:** LayerNorm shift invariant; RMSNorm changes; both zero cases finite.

**Verify:** Compare the computed values or written argument with LayerNorm shift invariant; RMSNorm changes; both zero cases finite.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
