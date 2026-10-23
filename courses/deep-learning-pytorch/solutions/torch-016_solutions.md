# torch-016: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Nonlinearity changes which functions a network can represent. Stacking linear layers without activations still produces one affine map. XOR assigns opposite labels to diagonal l y opposite corners of a square, so there is no linear threshold separating all four cases. Two rectified differences h1=max(x1-x2, 0), h2=max(x2-x1, 0) produce the exact binary pattern when added. This manual construction distinguishes representation al capacity from whether an optimizer happens to find it.

Initialization selects a starting point and can preserve or break symmetry between units. Equal hidden weights can produce identical features and gradients, making units redundant. Gradient diagnostics should inspect where activations and derivatives become zero or nonfinite instead of assuming the architecture is in capable. PyTorch provides explicit initialization functions and no_grad assignment for controlled fixtures.

**Nonlinearity:** A transformation that cannot be collapsed into one affine map.

**Initialization:** The policy choosing parameter values before training.

**Capacity:** The function family an architecture can represent.

**Symmetry:** Identical unit behavior preserved by identical state and updates.

## Reading the implementation

UseF.relu after a matrix product. Innn.Linear, the columns of a mathematical projection are the rows of the stored weight. torch.nn.init.zeros_ or constant_ set known initial state without constructing an optimization graph. Compare all four XOR inputs before training. A ReLU negative preactivation has zero local derivative; a zero gradient and a missing gradient path are not the same diagnosis.

## Exercise 1: Construct XOR by hand

The question is: Use inputs00, 01, 10, 11 and two rectified differences.

Each hidden unit detects one direction of difference. ReLU prevents positive and negative contributions from cancelling.

```python
x=torch.tensor([[0.,0.],[0.,1.],[1.,0.],[1.,1.]])
w=torch.tensor([[1.,-1.],[-1.,1.]])
h=F.relu(x@w); output=h.sum(1)
assert output.tolist()==[0.,1.,1.,0.]
```

**Expected:** outputs0, 1, 1, 0.

**Verify:** Compare the computed values or written argument with outputs0, 1, 1, 0.

## Exercise 2: Remove the nonlinearity

The question is: Sum the raw difference features without ReLU.

The two columns are opposite s, so a linear sum cancels. Adding more linear layers would not create the piecewise behavior needed for XOR.

```python
assert (x@w).sum(1).tolist()==[0.,0.,0.,0.]
```

**Expected:** all four outputs0.

**Verify:** Compare the computed values or written argument with all four outputs0.

## Exercise 3: Map the construction into Linear

The question is: Seta2-to-2 bias-free Linear weight to W.T and apply ReLU.

The explicit transpose checks PyTorch's stored layout. A correct mathematical matrix with the wrong assignment orientation can change a function silently when shapes are square.

```python
layer=nn.Linear(2,2,bias=False)
with torch.no_grad(): layer.weight.copy_(w.T)
torch.testing.assert_close(F.relu(layer(x)),h,atol=0,rtol=0)
```

**Expected:** module features equal manual features.

**Verify:** Compare the computed values or written argument with module features equal manual features.

## Exercise 4: Inspect activation gradients

The question is: Differentiate ReLU at-2 and2.

An inactive unit receives no derivative from these inputs. This is a connected zero, so adding retain_grad or detach would not repair the learning condition.

```python
z=torch.tensor([-2.,2.],requires_grad=True); F.relu(z).sum().backward()
assert z.grad.tolist()==[0.,1.]
```

**Expected:** gradients0 and1.

**Verify:** Compare the computed values or written argument with gradients0 and1.

## Exercise 5: Expose identical-unit symmetry

The question is: Initialize both stored Linear rows identically and compare their outputs.

Separate parameter objects do not guarantee different representations. Initialization and training data must break unhelpful symmetries when the task requires distinct features.

```python
symmetric=nn.Linear(2,2,bias=False)
with torch.no_grad(): symmetric.weight.copy_(torch.tensor([[1.,2.],[1.,2.]]))
features=symmetric(x); torch.testing.assert_close(features[:,0],features[:,1],atol=0,rtol=0)
```

**Expected:** two unit outputs match on every row.

**Verify:** Compare the computed values or written argument with two unit outputs match on every row.

## Exercise 6: Transfer to continuous inputs

The question is: Evaluate the fixed construction at(.2, .8) and(.8, .2).

The architecture computes a continuous function outside the binary fixture. Calling every output XOR would hide the input-domain assumption.

```python
points=torch.tensor([[.2,.8],[.8,.2]])
torch.testing.assert_close(F.relu(points@w).sum(1),torch.tensor([.6,.6]),atol=1e-6,rtol=0)
```

**Expected:** both.6; the function is absolute difference.

**Verify:** Compare the computed values or written argument with both.6; the function is absolute difference.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
