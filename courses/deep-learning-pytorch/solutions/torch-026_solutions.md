# torch-026: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Custom modules should make state ownership and differentiation explicit. Parameters are optimized; buffers are tracked but normally fixed; temporary activations are rebuilt during forward. A residual branch adds a transformed input to the original, so feature dimensions must match or an explicit projection must reconcile them. Creating new parameters in forward would change model identity and invalidate optimizer membership.

A custom differentiable function should be checked against independent derivatives before being trusted in a large network. PyTorch grad check uses finite differences, usually with float64 inputs, to compare a backward formula with the numerical behavior of forward. Passing a few checks is useful evidence under those inputs, not a proof for every branch or nondifferentiable point. This lesson combines a simple residual module with a tiny custom cube function so both registration and derivative contracts remain inspectable.

**Custom module:** A reusable computation with explicitly registered state.

**Buffer:** Tracked tensor state outside the optimizer parameter set.

**Grad check:** A numerical comparison of a backward rule with finite differences.

**Incoming gradient:** The derivative from later operations supplied to a local backward rule.

## Reading the implementation

Assign nn.Parameter in __init__, register a scale buffer, and implement forward without allocating new trainable state. Use named_parameters and named_buffers to inspect ownership. A torch.autograd.Function defines static forward and backward methods; save_for_backward stores inputs needed later. grad check perturbs double-precision inputs and should avoid kinks. The cube derivative is3*x² times the incoming gradient.

## Exercise 1: Build an identity residual

The question is: Create a width2 residual with zero kernel and scale buffer1.

A zero branch makes the initial residual an exact identity. The branch can still receive gradients because its input is nonzero.

```python
module=Residual(2); x=torch.tensor([[1.,2.],[3.,4.]],dtype=torch.float64)
assert torch.equal(module(x),x)
assert set(dict(module.named_parameters()))=={'kernel'} and set(dict(module.named_buffers()))=={'scale'}
```

**Expected:** output equals input; one parameter and one buffer.

**Verify:** Compare the computed values or written argument with output equals input; one parameter and one buffer.

## Exercise 2: Keep state stable across calls

The question is: Call the same module on a second batch with the same width.

Batch length changes transient activations, not the number of learned coefficients. Stable state is necessary for optimizer and checkpoint consistency.

```python
identity=id(module.kernel); module(torch.ones((1,2),dtype=torch.float64))
assert id(module.kernel)==identity and sum(p.numel() for p in module.parameters())==4
```

**Expected:** same kernel object and parameter count 4.

**Verify:** Compare the computed values or written argument with same kernel object and parameter count 4.

## Exercise 3: Check a known residual transform

The question is: Assign an identity kernel and scale.5.

The buffer changes forward behavior while remaining outside the trainable parameter list. It therefore belongs in the serialized state contract.

```python
with torch.no_grad(): module.kernel.copy_(torch.eye(2,dtype=torch.float64)); module.scale.fill_(.5)
torch.testing.assert_close(module(x),1.5*x,atol=1e-12,rtol=0)
```

**Expected:** output1.5*x.

**Verify:** Compare the computed values or written argument with output1.5*x.

## Exercise 4: Reject incompatible feature width

The question is: Pass a width3 row to the width2 module.

A residual addition requires meaningful matching dimensions. Silent broadcasting would represent a different operation and should not repair the contract accidentally.

```python
try: module(torch.ones((1,3),dtype=torch.float64))
except ValueError: pass
else: raise AssertionError('incompatible residual accepted')
```

**Expected:** ValueError naming feature width.

**Verify:** Compare the computed values or written argument with ValueError naming feature width.

## Exercise 5: Validate a custom cube derivative

The question is: Run grad check on Cube.apply at float64 values.2, -.7.

The finite-difference checker is independent of the written backward formula. Double precision reduces numerical noise for the small diagnostic.

```python
probe=torch.tensor([.2,-.7],dtype=torch.float64,requires_grad=True)
assert torch.autograd.gradcheck(Cube.apply,(probe,),eps=1e-6,atol=1e-5,rtol=1e-3)
```

**Expected:** grad check True.

**Verify:** Compare the computed values or written argument with grad check True.

## Exercise 6: Inspect the incoming-gradient factor

The question is: Differentiate the sum of 2*Cube(x) atx2.

The local derivative3*x² must be multiplied by the incoming derivative2. Forgetting that factor can pass a simple standalone test but fail when the function is composed.

```python
value=torch.tensor([2.],dtype=torch.float64,requires_grad=True); (2*Cube.apply(value)).sum().backward()
assert value.grad.item()==24
```

**Expected:** gradient24.

**Verify:** Compare the computed values or written argument with gradient24.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
