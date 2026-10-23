# torch-003: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A linear layer computes an affine transformation from input features to output features. For a batch X shaped(B, I), PyTorch nn.Linear(I, O) stores weight shaped(O, I) and computes X@weight.T+bias. This storage orientation differs from the common mathematical W shaped(I, O) and from a Keras Dense kernel. The batch axis is not part of the parameter shape. Bias has one value per output feature and is shared across observations.

An nn.Parameter assigned to an nn.Module is registered as trainable state. A plain tensor attribute is not automatically an optimizer parameter, even if it participates in arithmetic. Registration lets model.parameters(), state_dict and device/dtype conversion find the intended state. Shape inspection and a hand-calculated first row provide an independent check before any training occurs.

**Affine map:** A matrix transformation plus an additive bias.

**Parameter registration:** Tracking model state for optimization and serialization.

**Weight layout:** The semantic orientation of stored input/output feature axes.

## Reading the implementation

Construct nn.Linear(3, 1, bias=True, dtype=torch.float64). Assign known values under no_grad so initialization does not become part of an autograd graph. copy_ requires the stored layout(1, 3). Calling the module performs the forward computation; it does not update weights. parameters enumerates both weight and bias when enabled. Count scalar entries with numel, not the number of Parameter objects.

## Derive the forward map and parameter contracts

Let a batch have B observations, I input features and O outputs. The mathematical row-vector expression uses X shaped(B, I), W shaped(I, O) and b shaped(O), producing Y shaped(B, O). PyTorch stores the corresponding Linear weight as(O, I), so its forward expression is X@weight.T+b. The transpose translates the storage convention; it is not a proposal to exchange the observation and feature axes. [PyTorch 2.9 Linear](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Linear.html).

| Object | This fixture | General contract |
| --- | --- | --- |
| Input X | (2, 3) | (B, I) |
| Stored weight | (1, 3) | (O, I) |
| Mathematical W | (3, 1) | (I, O) |
| Bias | (1, ) | (O, ) |
| Output | (2, 1) | (B, O) |

For the first row[1, 2, 3], the products are 1, 0, -3. Adding bias 2 gives zero. The second row[0, 1, 0] contributes zero before the same shared bias, giving two. The bias is not a separate fitted offset for each observation. WithO outputs there areI×O weight scalars and O bias scalars, orO(I+1) total. ChangingB changes the number of evaluated rows, not the parameter count.

Suppose an upstream loss supplies derivatives g1 and g2 for these two scalar outputs. The stored weight gradient is[g1, 2g1+g2, 3g1], and the bias gradient isg 1+g2. The bias gradient sums over the batch because one bias participates in both outputs. Each input-row gradient is its upstream scalar multiplied by[1, 0, -1]. These shapes can be predicted before using autograd: weight.grad must match(1, 3), bias.grad must match(1, ), and input derivatives match(2, 3).

A feature-order mistake can remain invisible to every dimension check. If the first input is accidentally exported as[3, 2, 1], its output becomes 3-1+2=4 instead of zero while all shapes remain valid. Likewise, a centimeter-to-meter conversion requires a corresponding weight interpretation if the represented function is to stay the same. The data schema must therefore preserve names, order and units beside the width.

Autograd and module registration answer different questions. A plain tensor with requires_grad=True can participate in a differentiable computation, but model.parameters() will not discover it merely because it is an attribute. Assigning nn.Parameter registers it. Registration does not require that gradients currently be enabled: freezing can turn requires_grad off while retaining the parameter in the module's state. Buffers form another category of registered state introduced later.

The known-value initialization runs under no_grad so assignment is not recorded as part of the differentiation graph. It does not make the layer permanently nontrainable. Calling the layer computes outputs but does not update parameters; an optimizer update is a separate later operation. These distinctions let the reader locate whether a failure concerns the forward function, the differentiation graph, the state inventory or the update mechanism.

## Exercise 1: Calculate a known affine layer

The question is: UseX[[1, 2, 3], [0, 1, 0]], weight[[1, 0, -1]], bias 2.

The first output is 1-3+2=0, and the second is 0+2=2. This calculation checks orientation and bias independently of random initialization.

```python
layer=nn.Linear(3,1,bias=True,dtype=torch.float64)
with torch.no_grad(): layer.weight.copy_(torch.tensor([[1.,0.,-1.]],dtype=torch.float64)); layer.bias.fill_(2.)
x=torch.tensor([[1.,2.,3.],[0.,1.,0.]],dtype=torch.float64); out=layer(x)
torch.testing.assert_close(out,torch.tensor([[0.],[2.]],dtype=torch.float64),atol=1e-12,rtol=0)
```

**Expected:** outputs[[0], [2]], shape(2, 1).

**Verify:** Compare the computed values or written argument with outputs[[0], [2]], shape(2, 1).

## Exercise 2: Inspect registered state

The question is: Count weight and bias scalar entries and inspect state_dict keys.

There are two Parameter objects but four trainable scalar values. Parameter count and tensor count answer different questions.

```python
assert sum(p.numel() for p in layer.parameters())==4
assert set(layer.state_dict())=={'weight','bias'}
```

**Expected:** 4 scalars; keys weight, bias.

**Verify:** Compare the computed values or written argument with 4 scalars; keys weight, bias.

## Exercise 3: Compare with a mathematical matrix

The question is: Transpose the stored weight and calculate X@W+b directly.

The transpose is a layout translation, not a change in the modeled function. A non symmetric rectangular fixture makes an accidental orientation error visible.

```python
mathematical_w=layer.weight.T
assert tuple(mathematical_w.shape)==(3,1)
torch.testing.assert_close(x@mathematical_w+layer.bias,out,atol=1e-12,rtol=0)
```

**Expected:** direct result equals module output.

**Verify:** Compare the computed values or written argument with direct result equals module output.

## Exercise 4: Remove the intercept explicitly

The question is: Create a bias-free layer with the same stored weights.

A zero-initialized bias would still be trainable. Omitting the bias removes that parameter and its gradient entirely.

```python
no_bias=nn.Linear(3,1,bias=False,dtype=torch.float64)
with torch.no_grad(): no_bias.weight.copy_(layer.weight)
assert sum(p.numel() for p in no_bias.parameters())==3
torch.testing.assert_close(no_bias(x),torch.tensor([[-2.],[0.]],dtype=torch.float64),atol=1e-12,rtol=0)
```

**Expected:** 3 parameters; outputs-2 and 0.

**Verify:** Compare the computed values or written argument with 3 parameters; outputs-2 and 0.

## Exercise 5: Expose an unregistered tensor

The question is: Compare a Module holding a plain requires_grad tensor with one holding Parameter.

Autograd can track a plain tensor without the module registering it. An optimizer built from model.parameters would miss that state.

```python
plain=nn.Module(); plain.weight=torch.tensor([1.],requires_grad=True)
proper=nn.Module(); proper.weight=nn.Parameter(torch.tensor([1.]))
assert len(list(plain.parameters()))==0 and len(list(proper.parameters()))==1
```

**Expected:** plain module has 0 registered parameters; proper module has 1.

**Verify:** Compare the computed values or written argument with plain module has 0 registered parameters; proper module has 1.

## Exercise 6: Reject wrong feature width

The question is: Pass a2-feature row to the 3-input layer.

A variable batch length is allowed, but the declared feature width remains fixed. The model contract should name that distinction.

```python
try: layer(torch.ones((1,2),dtype=torch.float64))
except RuntimeError: pass
else: raise AssertionError('wrong feature width accepted')
```

**Expected:** RuntimeError from incompatible matrix dimensions.

**Verify:** Compare the computed values or written argument with RuntimeError from incompatible matrix dimensions.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
