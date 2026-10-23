# torch-016: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Nonlinearity changes which functions a network can represent. Stacking linear layers without activations still produces one affine map. XOR assigns opposite labels to diagonally opposite corners of a square, so there is no linear threshold separating all four cases. Two rectified differences h1=max(x1-x2, 0), h2=max(x2-x1, 0) produce the exact binary pattern when added. This manual construction distinguishes representational capacity from whether an optimizer happens to find it.

Initialization selects a starting point and can preserve or break symmetry between units. Equal hidden weights can produce identical features and gradients, making units redundant. Gradient diagnostics should inspect where activations and derivatives become zero or nonfinite instead of assuming the architecture is incapable. PyTorch provides explicit initialization functions and no_grad assignment for controlled fixtures.

**Nonlinearity:** A transformation that cannot be collapsed into one affine map.

**Initialization:** The policy choosing parameter values before training.

**Capacity:** The function family an architecture can represent.

**Symmetry:** Identical unit behavior preserved by identical state and updates.

## Reading the implementation

Use F.relu after a matrix product. In nn.Linear, the columns of a mathematical projection are the rows of the stored weight. torch.nn.init.zeros_ or constant_ set known initial state without constructing an optimization graph. Compare all four XOR inputs before training. A ReLU negative preactivation has zero local derivative; a zero gradient and a missing gradient path are not the same diagnosis.

## Prove the capacity boundary and then inspect optimization

Suppose a classifier uses an affine score \(s=a\) x1+b x2+c and predicts class 1 when \(s>0\). XOR requires(1, 0) and(0, 1) positive, so \(a+c>0\) and \(b+c>0\). It requires(0, 0) and(1, 1) nonpositive, so c≤0 and a+b+c≤0. Summing the positive requirements gives a+b+2c>0; summing the negative requirements gives the same quantity≤0. The contradiction proves that no such affine separator exists, independent of a random seed or training budget.

Stacking affine layers does not remove that boundary. `(XW1+b1)W2+b2 = X(W1W2)+(b1W2+b2)` is still affine in the input. A bottleneck can even restrict the possible rank. Nonlinear parameterization of the weights may change optimization behavior, but it does not create a nonlinear input function. Adding an engineered interaction feature would change the input representation and therefore the problem being considered.

The manual construction uses \(d=x_{1}-x_{2}\), h1=max(d, 0), h2=max(-d, 0), and \(\mathrm{output}=h_{1}+h_{2}\):

| Input | Raw difference pair | ReLU features | Output |
| --- | --- | --- | --- |
| (0, 0) | (0, 0) | (0, 0) | 0 |
| (0, 1) | (-1, 1) | (0, 1) | 1 |
| (1, 0) | (1, -1) | (1, 0) | 1 |
| (1, 1) | (0, 0) | (0, 0) | 0 |

Without ReLU, the two raw differences cancel everywhere. With ReLU, the sum is|x1-x2|. On binary corners that equals XOR, but on continuous inputs(.2, .8) and(.8, .2) it equals 0.6. That value is a function output, not automatically a calibrated probability or a new definition of a binary logical operator.

The XOR projection matrix[[1, -1], [-1, 1]] is symmetric. Consequently, W.T equalsW, so the original fixture alone cannot detect a forgotten transpose when copying a mathematical matrix into nn.Linear's stored(out, in) layout. The strengthened example adds a separate nonsymmetric matrix[[1, 2], [3, 4]]. For input[0, 1], XW gives[3, 4], while XW.T gives[2, 4]. That probe makes the storage translation observable while retaining the original XOR construction unchanged.

Activation gradients distinguish a dead region from a broken graph. ReLU at a negative preactivation has a connected derivative zero; at a positive one its derivative is one. At the kink, the framework uses its chosen convention. Repeatedly negative preactivations can therefore block useful gradient flow even though every operation is differentiable on the active path. Inspect activation signs and intermediate gradients before declaring the architecture incapable.

Identical hidden rows produce identical features on the same input. Equal gradients additionally require symmetric downstream influence and other state; unequal output weights can break that symmetry. If a whole ReLU network is initialized in a zero/symmetric configuration, both hidden activations and upstream signals can vanish, leaving ordinary gradient descent unable to create useful differences. Separate Parameter objects are not by themselves evidence of diverse features.

Variance-aware initialization gives a useful approximation. For independent zero-mean inputs and weights, a preactivation's variance scales roughly with \(\mathrm{fan}_{\mathrm{in}}\cdot \operatorname{Var}(\mathrm{weight})\cdot \operatorname{Var}(\mathrm{input})\). ReLU discards about half the second moment under a symmetric distribution, motivating an initialization scale near \(\frac{2}{\mathrm{fan}_{\mathrm{in}}}\) for that simplified setting. Those assumptions need not hold exactly for correlated finite data. Choose the documented initializer and gain for the intended activation rather than assuming every layer's default initialization implements that exact rule. [PyTorch 2.9 initialization APIs](https://docs.pytorch.org/docs/2.9/nn.init.html).

## Exercise 1: Construct XOR by hand

The question is: Use inputs 00, 01, 10, 11 and two rectified differences.

Each hidden unit detects one direction of difference. ReLU prevents positive and negative contributions from cancelling.

```python
x=torch.tensor([[0.,0.],[0.,1.],[1.,0.],[1.,1.]])
w=torch.tensor([[1.,-1.],[-1.,1.]])
h=F.relu(x@w); output=h.sum(1)
assert output.tolist()==[0.,1.,1.,0.]
```

**Expected:** outputs 0, 1, 1, 0.

**Verify:** Compare the computed values or written argument with outputs 0, 1, 1, 0.

## Exercise 2: Remove the nonlinearity

The question is: Sum the raw difference features without ReLU.

The two columns are opposites, so a linear sum cancels. Adding more linear layers would not create the piecewise behavior needed for XOR.

```python
assert (x@w).sum(1).tolist()==[0.,0.,0.,0.]
```

**Expected:** all four outputs 0.

**Verify:** Compare the computed values or written argument with all four outputs 0.

## Exercise 3: Map the construction into Linear

The question is: Set a 2-to-2 bias-free Linear weight to W.T, then check a separate asymmetric matrix.

The XOR matrix is symmetric, so that fixture alone cannot detect a missing transpose. The separate asymmetric matrix makes the two orientations produce different outputs and checks the Linear storage convention independently.

```python
layer=nn.Linear(2,2,bias=False)
with torch.no_grad(): layer.weight.copy_(w.T)
torch.testing.assert_close(F.relu(layer(x)),h,atol=0,rtol=0)
asymmetric=torch.tensor([[1.,2.],[3.,4.]])
probe=nn.Linear(2,2,bias=False)
with torch.no_grad(): probe.weight.copy_(asymmetric.T)
torch.testing.assert_close(probe(x),x@asymmetric,atol=0,rtol=0)
assert not torch.equal(x@asymmetric,x@asymmetric.T)
```

**Expected:** module features equal manual features; the asymmetric probe distinguishes the two orientations.

**Verify:** Compare the computed values or written argument with module features equal manual features; the asymmetric probe distinguishes the two orientations.

## Exercise 4: Inspect activation gradients

The question is: Differentiate ReLU at-2 and 2.

An inactive unit receives no derivative from these inputs. This is a connected zero, so adding retain_grad or detach would not repair the learning condition.

```python
z=torch.tensor([-2.,2.],requires_grad=True); F.relu(z).sum().backward()
assert z.grad.tolist()==[0.,1.]
```

**Expected:** gradients 0 and 1.

**Verify:** Compare the computed values or written argument with gradients 0 and 1.

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
