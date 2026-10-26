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

Assign nn.Parameter in __init__, register a scale buffer, and implement forward without allocating new trainable state. Use named_parameters and named_buffers to inspect ownership. A torch.autograd.Function defines static forward and backward methods; save_for_backward stores inputs needed later. grad check perturbs double-precision inputs and should avoid kinks. The cube derivative is \(3\cdot {x}^{2}\) times the incoming gradient.

## Derive residual gradients and stable module identity

For X shaped(B, D), a square kernel K shaped(D, D) and scalar scale s, the module computes \(Y=X+sXK\). Both terms have shape(B, D). A different branch width requires an explicit projection or a different architecture. Broadcasting an unrelated tensor into the residual sum may be legal arithmetic but would not satisfy this feature contract.

At \(K=0\) and \(s=1\), the forward map is exactly Y=X. That does not make the branch untrainable. For upstream \(G=\frac{\partial L}{\partial Y}\), the matrix derivatives are \(\frac{\partial L}{\partial X}=G+sGK^{\mathsf T}\) and \(\frac{\partial L}{\partial K}=sX^{\mathsf T}G\). With the fixture X=[[1, 2], [3, 4]] and L equal to the sum of output entries, G is all ones, so dL/dK=[[4, 4], [6, 6]] even at \(K=0\). The input derivative is G because the zero branch adds no additional input sensitivity. The skip path preserves a direct derivative route while the branch can begin learning.

Example C changes K to identity and s to 0.5. Its forward result is 1.5X. Under the same hypothetical summed loss, dL/dX=1.5G and dL/dK=[[2, 2], [3, 3]]. The paired TensorFlow residual has no scale buffer and therefore gives 2 X when its kernel is identity. That difference is an intentional mathematical configuration difference, not a framework disagreement. Match the scale before comparing corresponding derivatives.

The module owns one Parameter object with four scalar entries and one scalar buffer. Counting objects and counting scalars answer different questions. Parameters participate in named_parameters and are candidates for optimizer membership. The registered scale buffer participates in module state and device/dtype movement but is not automatically passed to an optimizer. Its current construction does not request gradients. An ordinary tensor attribute would not automatically receive all of those registration behaviors.

state_dict is not the complete program. It contains the registered kernel and persistent buffer, but reconstruction still needs the module class and width argument. Python configuration such as width is not made into serialized tensor state merely because it is an attribute. A release must preserve that construction contract alongside the tensors. Also, a state_dict mapping is not by itself an independent snapshot of every underlying tensor; clone the values when comparing against later in-place mutations.

Stable object identity matters as much as a stable parameter count. Replacing a four-element Parameter with a fresh four-element Parameter inside forward keeps the scalar count unchanged while leaving an existing optimizer holding the old object. Gradients can then appear on the new parameter without an update from that optimizer. The unchanged exercise checks both identity and count to expose this failure. Keras build/add_weight and PyTorch __init__/Parameter use different construction idioms, but both need a persistent tracked object across calls.

## Treat a custom backward as a local vector-Jacobian product

For \(f(x)=x^3\), the local derivative is 3 \({x}^{2}\). backward receives the derivative from later computation, so it must return \(\mathrm{grad\_output}\times3x^2\). At \(x=2\), the derivative of 2 f(x) is \(2\cdot 12=24\). Returning only 3 \({x}^{2}\) would pass a unit-upstream test but fail this composition. For a vector of independently cubed elements, the returned gradient has the same shape and multiplies each incoming component by its own local derivative.

save_for_backward preserves the tensor values required by the rule and lets autograd enforce relevant lifetime/version checks. Do not mutate saved input storage between forward and backward or detach a value that must support a higher-order derivative. A function with several inputs returns a corresponding derivative entry for each differentiable input, and None where that input has no requested derivative under the declared contract. [Extending PyTorch 2.9 autograd](https://docs.pytorch.org/docs/2.9/notes/extending.html).

gradcheck perturbs real-valued inputs and compares numerical sensitivities with the backward rule. The supplied float64 points 0.2 and-0.7 avoid a nondifferentiable branch, and the analytic derivatives are 0.12 and 1.47. Finite precision, probe size and conditioning still matter. A forward implementation that changes branches at the probe point may not have the derivative the numerical test assumes. Overlapping storage can also invalidate an interpretation that perturbations affect one independent coordinate.

A first-derivative check does not establish double backward, forward-mode support, arbitrary broadcasting or performance. Add the relevant contract tests when those features are actually required. The fixture's cube is small enough to inspect symbolically, and the upstream-factor test catches a distinct error from the basic numerical comparison. None of these checks requires a compiled extension or an external package.

## Exercise 1: Build an identity residual

The question is: Create a width 2 residual with zero kernel and scale buffer 1.

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

**Expected:** output \(1.5\cdot x\).

**Verify:** Compare the computed values or written argument with output \(1.5\cdot x\).

## Exercise 4: Reject incompatible feature width

The question is: Pass a width 3 row to the width 2 module.

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

The question is: Differentiate the sum of 2*Cube(x) atx 2.

The local derivative \(3\cdot {x}^{2}\) must be multiplied by the incoming derivative 2. Forgetting that factor can pass a simple standalone test but fail when the function is composed.

```python
value=torch.tensor([2.],dtype=torch.float64,requires_grad=True); (2*Cube.apply(value)).sum().backward()
assert value.grad.item()==24
```

**Expected:** gradient 24.

**Verify:** Compare the computed values or written argument with gradient 24.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
