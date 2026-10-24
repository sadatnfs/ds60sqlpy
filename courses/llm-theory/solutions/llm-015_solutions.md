# llm-015: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

PyTorch builds a dynamic computation graph when operations involve tensors requiring gradients. backward traverses that graph and accumulates derivatives into leaf gradients. A detached tensor keeps numeric data while removing its gradient connection, which can silently break training if used in the forward path. A zero derivative and an absent gradient are different observations. Embedding lookup is still the same indexed table seen in the NumPy lesson; a framework adds trainable state and gradient tracking rather than changing the mathematical meaning. CPU execution and tiny fixtures keep the first framework investigation inspectable.

**Autograd:** Automatic differentiation through recorded tensor operations.

**Leaf gradient:** Accumulated derivative stored on an input or parameter tensor.

**Detach:** Remove a tensor value from its existing gradient graph.

## Reading the implementation

torch.tensor(...,requires_grad=True) creates a leaf whose .grad is populated after backward. Clear gradients before a new independent step because backward accumulates by default. detach returns a value with requires_grad=False. nn.Embedding.from_pretrained(...,freeze=False) wraps a fixed literal table as trainable state. IDs use torch.long and select rows along the vocabulary axis.

## Exercise 1: Derive a scalar gradient

The question is: Differentiate(w-2)² atw0 in float64.

The analytic derivative2(w-2) supplies an independent oracle. A correct loss alone would not show that the gradient graph was connected.

```python
w=torch.tensor(0.,dtype=torch.float64,requires_grad=True); loss=(w-2)**2; loss.backward()
assert w.grad.item()==-4 and loss.item()==4
```

**Expected:** gradient-4 and loss4.

**Verify:** Compare the computed values or written argument with gradient-4 and loss4.

## Exercise 2: Compare finite differences

The question is: Use central differenceh=.001 for the same scalar function.

Finite differences perturb the function value rather than reading autograd internals. Agreement away from a nondifferentiable point supports the derivative calculation.

```python
h=.001; numeric=(((h-2)**2)-((-h-2)**2))/(2*h)
np.testing.assert_allclose(numeric,-4,atol=1e-10,rtol=0)
```

**Expected:** finite difference approximately-4 within1e-10.

**Verify:** Compare the computed values or written argument with finite difference approximately-4 within1e-10.

## Exercise 3: Observe accumulation

The question is: Call backward on a new loss without clearing the prior gradient.

PyTorch adds to existing gradients. A training loop that forgets zero_grad changes its effective update and can look unstable for reasons unrelated to model capacity.

```python
((w-2)**2).backward(); assert w.grad.item()==-8
```

**Expected:** stored gradient becomes-8.

**Verify:** Compare the computed values or written argument with stored gradient becomes-8.

## Exercise 4: Clear gradient state

The question is: Set the gradient to None, recompute and backpropagate once.

Resetting before the next independent batch restores the intended one-batch derivative. Intentional accumulation needs a separate denominator and step policy.

```python
w.grad=None; ((w-2)**2).backward(); assert w.grad.item()==-4
```

**Expected:** gradient returns to-4.

**Verify:** Compare the computed values or written argument with gradient returns to-4.

## Exercise 5: Inspect detachment

The question is: Detachw and compare its value and gradient-tracking status.

Detach preserves a numeric observation while cutting dependency. It is appropriate for logging or explicit stop-gradient designs, but not a repair for an unexplained backward error.

```python
detached=w.detach(); assert detached.item()==0 and detached.requires_grad is False
```

**Expected:** same value0; requires_gradFalse.

**Verify:** Compare the computed values or written argument with same value0; requires_gradFalse.

## Exercise 6: Check an embedding table

The question is: Lookup IDs2,0,2 in a fixed4x2 table and compare repeated rows.

The lookup does not average repeated IDs. Both positions refer to the same parameter row, so later gradient contributions to that row can accumulate.

```python
table=torch.tensor([[1.,0.],[0.,1.],[2.,2.],[-1.,1.]])
embedding=nn.Embedding.from_pretrained(table,freeze=False); out=embedding(torch.tensor([2,0,2]))
assert tuple(out.shape)==(3,2); np.testing.assert_array_equal(out.detach().numpy(),[[2,2],[1,0],[2,2]])
```

**Expected:** shape(3,2); rows0 and2 both[2,2].

**Verify:** Compare the computed values or written argument with shape(3,2); rows0 and2 both[2,2].

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
