# llm-032: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Low-rank adaptation freezes a base matrix and learns an additive product of two smaller matrices. Here row-vector inputs multiply W+A@B, with W shaped8x8,A8x2 and B shaped 2 by 8. The adapter has32 trainable scalars compared with64 in the base. InitializingB to zero makes the initial adapter contribution exactly zero, preserving base behavior. On the first update, the gradient ofA can be zero because it is multiplied byB, whileB receives a nonzero gradient throughA. This is expected under the stated initialization, not a disconnected graph. Low rank limits the update space; it is not a universal guarantee of equal quality to full fine-tuning.

**Low-rank update:** A matrix change represented as the product of two smaller matrices.

**Frozen base:** Parameters excluded from the adaptation optimizer.

**Zero-delta initialization:** An adapter starting with no change to the base function.

## Reading the implementation

Keep W as a tensor without requires_grad. Wrap A and B as Parameters and pass only those to SGD. The row-vector convention differs from frameworks that store Linear weights as(out,in), so record the orientation before transplanting equations. Compute delta=A@B and compare its shape withW. Snapshot the base bytes and assert exact preservation after the adapter update.

## Exercise 1: Count adapter parameters

The question is: Use W=I8,A=ones(8,2)/8,B=zeros(2,8).

The parameter reduction comes from the factorization rank2. Increasing rank increases trainable state and changes the set of possible updates.

```python
w = torch.eye(8)
a = nn.Parameter(torch.ones((8, 2)) / 8)
b = nn.Parameter(torch.zeros((2, 8)))
x = torch.ones((1, 8))
assert a.numel() + b.numel() == 32 and w.numel() == 64
```

**Expected:** adapter32 parameters versus base64.

**Verify:** Compare the computed values or written argument with adapter32 parameters versus base64.

## Exercise 2: Check zero initial delta

The question is: Compare x@(W+A@B) withx@W before training.

ZeroB eliminates the product while retaining a connected path forB throughA. The base prediction is preserved exactly at initialization.

```python
delta = a @ b
initial = x @ (w + delta)
assert torch.equal(delta, torch.zeros((8, 8)))
assert torch.equal(initial, x @ w)
```

**Expected:** both equal ones(1,8).

**Verify:** Compare the computed values or written argument with both equal ones(1,8).

## Exercise 3: Differentiate the first objective

The question is: Use mean squared error to a zero target and inspect both adapter gradients.

The derivative with respect toA includesB and is zero at this initialization. The derivative with respect toB includesA, which is nonzero, so learning can begin.

```python
saved = w.clone()
loss = initial.square().mean()
loss.backward()
assert torch.count_nonzero(a.grad).item() == 0 and torch.count_nonzero(b.grad).item() > 0
```

**Expected:** A gradient zero;B gradient nonzero.

**Verify:** Compare the computed values or written argument with A gradient zero;B gradient nonzero.

## Exercise 4: Update only the adapter

The question is: Take one SGD(.1) step overA,B.

An optimizer over all model parameters would violate the frozen-base contract. The snapshot directly tests the state that must remain untouched.

```python
before_b = b.detach().clone()
opt = torch.optim.SGD([a, b], lr=0.1)
opt.step()
assert not torch.equal(b, before_b) and torch.equal(w, saved)
```

**Expected:** B changes;W remains exactly equal.

**Verify:** Compare the computed values or written argument with B changes;W remains exactly equal.

## Exercise 5: Observe the changed function

The question is: Recompute the zero-target squared error after the adapter step.

The first update changes the function throughB. This local decrease demonstrates a working adapter path, not a general optimization guarantee.

```python
after = (x @ (w + a @ b)).square().mean()
assert after.item() < loss.item()
```

**Expected:** loss decreases for this fixture.

**Verify:** Compare the computed values or written argument with loss decreases for this fixture.

## Exercise 6: Bound the update rank

The question is: Compute the numerical matrix rank ofA@B after the step.

The factorization constrains the rank regardless of optimizer behavior. Multiple adapters or different placement choices can change the overall function class and require separate analysis.

```python
assert int(torch.linalg.matrix_rank((a @ b).detach())) <= 2
```

**Expected:** rank at most2.

**Verify:** Compare the computed values or written argument with rank at most2.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
