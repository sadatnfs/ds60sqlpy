# torch-003: explanatory solutions

Open these answers only after attempting Linear modules, parameters and matrix contracts yourself. They reuse the guide's literal inputs, starting from Example A, Calculate a known affine layer, so a discrepancy points at one step. The executable companion runs the assertions; this page explains why each one tests Affine map, Parameter registration, Weight layout. After a pass, choose a new input for exercise 6, Reject wrong feature width, without looking.

## Mechanism review

A linear layer computes an affine transformation from input features to output features. For a batch X shaped (B, I), PyTorch nn.Linear(I, O) stores weight shaped (O, I) and computes X@weight.T+bias. This storage orientation differs from the common mathematical W shaped (I, O) and from a Keras Dense kernel. The batch axis is not part of the parameter shape. Bias has one value per output feature and is shared across observations.

An nn.Parameter assigned to an nn.Module is registered as trainable state. A plain tensor attribute is not automatically an optimizer parameter, even if it participates in arithmetic. Registration lets model.parameters(), state_dict and device/dtype conversion find the intended state. Shape inspection and a hand-calculated first row provide an independent check before any training occurs.

**Affine map:** A matrix transformation plus an additive bias.

**Parameter registration:** Tracking model state for optimization and serialization.

**Weight layout:** The semantic orientation of stored input/output feature axes.

## Reading the implementation

Construct nn.Linear(3, 1, bias=True, dtype=torch.float64). Assign known values under no_grad so initialization does not become part of an autograd graph. copy_ requires the stored layout (1, 3). Calling the module performs the forward computation; it does not update weights. parameters enumerates both weight and bias when enabled. Count scalar entries with numel, not the number of Parameter objects.

## Derive the forward map and parameter contracts

Let a batch have B observations, I input features and O outputs. The mathematical row-vector expression uses X shaped (B, I), W shaped (I, O) and b shaped (O), producing Y shaped (B, O). PyTorch stores the corresponding Linear weight as (O, I), so its forward expression is X@weight.T+b. The transpose translates the storage convention; it is not a proposal to exchange the observation and feature axes. [PyTorch 2.9 Linear](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Linear.html).

| Object | This fixture | General contract |
| --- | --- | --- |
| Input X | (2, 3) | (B, I) |
| Stored weight | (1, 3) | (O, I) |
| Mathematical W | (3, 1) | (I, O) |
| Bias | (1, ) | (O, ) |
| Output | (2, 1) | (B, O) |

For the first row [1, 2, 3], the products are 1, 0, -3. Adding bias 2 gives zero. The second row [0, 1, 0] contributes zero before the same shared bias, giving two. The bias is not a separate fitted offset for each observation. With O outputs there are I×O weight scalars and O bias scalars, or O(I+1) total. Changing B changes the number of evaluated rows, not the parameter count.

Suppose an upstream loss supplies derivatives g1 and g2 for these two scalar outputs. The stored weight gradient is [g1, 2g1+g2, 3g1], and the bias gradient is g1+g2. The bias gradient sums over the batch because one bias participates in both outputs. Each input-row gradient is its upstream scalar multiplied by [1, 0, -1]. These shapes can be predicted before using autograd: weight.grad must match (1, 3), bias.grad must match (1, ), and input derivatives match (2, 3).

A feature-order mistake can remain invisible to every dimension check. If the first input is accidentally exported as [3, 2, 1], its output becomes \(3-1+2=4\) instead of zero while all shapes remain valid. Likewise, a centimeter-to-meter conversion requires a corresponding weight interpretation if the represented function is to stay the same. The data schema must therefore preserve names, order and units beside the width.

Autograd and module registration answer different questions. A plain tensor with requires_grad=True can participate in a differentiable computation, but model.parameters() will not discover it merely because it is an attribute. Assigning nn.Parameter registers it. Registration does not require that gradients currently be enabled: freezing can turn requires_grad off while retaining the parameter in the module's state. Buffers form another category of registered state introduced later.

The known-value initialization runs under no_grad so assignment is not recorded as part of the differentiation graph. It does not make the layer permanently nontrainable. Calling the layer computes outputs but does not update parameters; an optimizer update is a separate later operation. These distinctions let the reader locate whether a failure concerns the forward function, the differentiation graph, the state inventory or the update mechanism.

## Exercise 1: Compute a new affine output

The question is: Set a 2-to-1 Linear layer's weight to [[2, -1]] and its bias to 0.5 in float64, then evaluate the rows [1, 1] and [0, 2].

Each row is a dot product with the stored weight row plus the bias: 2-1+0.5 and 0-2+0.5.

```python
small = nn.Linear(2, 1, dtype=torch.float64)
with torch.no_grad():
    small.weight.copy_(torch.tensor([[2.0, -1.0]], dtype=torch.float64))
    small.bias.fill_(0.5)
inputs = torch.tensor([[1.0, 1.0], [0.0, 2.0]], dtype=torch.float64)
scored = small(inputs)
torch.testing.assert_close(
    scored, torch.tensor([[1.5], [-1.5]], dtype=torch.float64), atol=1e-12, rtol=0
)
```

**Expected:** outputs [[1.5], [-1.5]] with shape (2, 1).

**Verify:** In a fresh process, the exercise checks confirm `scored` matches `torch.tensor([[1.5], [-1.5]], dtype=torch.float64)` within 1e-12.

## Exercise 2: Predict a parameter count

The question is: Before creating it, predict the registered scalar count and the state_dict shapes of nn.Linear(4, 3), then check them.

The stored weight is (out, in), so 3 rows of 4 coefficients, plus one bias per output.

```python
wide = nn.Linear(4, 3)
assert (
    sum(p.numel() for p in wide.parameters()) == 15
    and tuple(wide.weight.shape) == (3, 4)
    and tuple(wide.bias.shape) == (3,)
)
```

**Expected:** 15 scalars: weight (3, 4) and bias (3,).

**Verify:** In a fresh process, the exercise checks confirm `sum((p.numel() for p in wide.parameters())) == 15`; `tuple(wide.weight.shape) == (3, 4)` and `tuple(wide.bias.shape) == (3,)`.

## Exercise 3: Rebuild the output by hand

The question is: For the 2-to-1 layer, compute inputs @ weight.T + bias without calling the module and compare it with the module output.

Transposing the stored (out, in) weight gives the (in, out) matrix used in the mathematical form XW+b.

```python
manual = inputs @ small.weight.T + small.bias
torch.testing.assert_close(manual, scored, atol=1e-12, rtol=0)
```

**Expected:** the manual result equals [[1.5], [-1.5]] within 1e-12.

**Verify:** In a fresh process, the exercise checks confirm `manual` matches `scored` within 1e-12.

## Exercise 4: Remove the intercept explicitly

The question is: Create a bias-free layer with the same stored weights.

A zero-initialized bias would still be trainable. Omitting the bias removes that parameter and its gradient entirely.

```python
no_bias = nn.Linear(3, 1, bias=False, dtype=torch.float64)
with torch.no_grad():
    no_bias.weight.copy_(layer.weight)
assert sum(p.numel() for p in no_bias.parameters()) == 3
torch.testing.assert_close(
    no_bias(x), torch.tensor([[-2.0], [0.0]], dtype=torch.float64), atol=1e-12, rtol=0
)
```

**Expected:** 3 parameters; outputs -2 and 0.

**Verify:** In a fresh process, the exercise checks confirm `sum((p.numel() for p in no_bias.parameters())) == 3` and `no_bias(x)` matches `torch.tensor([[-2.0], [0.0]], dtype=torch.float64)` within 1e-12.

## Exercise 5: Expose an unregistered tensor

The question is: Compare a Module holding a plain requires_grad tensor with one holding Parameter.

Autograd can track a plain tensor without the module registering it. An optimizer built from model.parameters would miss that state.

```python
plain = nn.Module()
plain.weight = torch.tensor([1.0], requires_grad=True)
proper = nn.Module()
proper.weight = nn.Parameter(torch.tensor([1.0]))
assert len(list(plain.parameters())) == 0 and len(list(proper.parameters())) == 1
```

**Expected:** plain module has 0 registered parameters; proper module has 1.

**Verify:** In a fresh process, the exercise checks confirm `len(list(plain.parameters())) == 0` and `len(list(proper.parameters())) == 1`.

## Exercise 6: Reject wrong feature width

The question is: Pass a 2-feature row to the 3-input layer.

A variable batch length is allowed, but the declared feature width remains fixed. The model contract should name that distinction.

```python
try:
    layer(torch.ones((1, 2), dtype=torch.float64))
except RuntimeError:
    pass
else:
    raise AssertionError("wrong feature width accepted")
```

**Expected:** RuntimeError from incompatible matrix dimensions.

**Verify:** In a fresh process, the exercise checks confirm `layer(torch.ones((1, 2), dtype=torch.float64))` raises `RuntimeError`.

## Review after comparison

Repeat exercise 4, Remove the intercept explicitly, with one changed fixture value and predict the difference before running it. Keep your failing attempt at exercise 5, Expose an unregistered tensor, beside the repaired result. A missing framework is not a failing assertion. These solutions use only local fixtures.
