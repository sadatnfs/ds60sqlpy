# llm-032: explanatory solutions

Read these low-rank adaptation without a package download answers after attempting *Count adapter parameters* through *Bound the update rank*, or after asking for a reveal. They reuse the guide's literals, so a mismatch in *Differentiate the first objective* points to one step. `llm-032_solution.py` holds the assertions; this page explains how they test low-rank update. Then try *Bound the update rank* on a fresh input you chose before looking.

## Mechanism review

Low-rank adaptation freezes a base matrix and learns an additive product of two smaller matrices. Here row-vector inputs multiply W+A@B, with W shaped 8x8, A 8x2 and B shaped 2 by 8. The adapter has 32 trainable scalars compared with 64 in the base. Initializing B to zero makes the initial adapter contribution exactly zero, preserving base behavior. On the first update, the gradient of A can be zero because it is multiplied by B, while B receives a nonzero gradient through A. This is expected under the stated initialization, not a disconnected graph. Low rank limits the update space; it is not a universal guarantee of equal quality to full fine-tuning.

**Low-rank update:** A matrix change represented as the product of two smaller matrices.

**Frozen base:** Parameters excluded from the adaptation optimizer.

**Zero-delta initialization:** An adapter starting with no change to the base function.

## Reading the implementation

Keep W as a tensor without requires_grad. Wrap A and B as Parameters and pass only those to SGD. The row-vector convention differs from frameworks that store Linear weights as (out, in), so record the orientation before transplanting equations. Compute delta=A@B and compare its shape with W. Snapshot the base bytes and assert exact preservation after the adapter update.

## Exercise 1: Count adapter parameters

The question is: Use W=I8, A=ones(8, 2)/8, B=zeros(2, 8).

The parameter reduction comes from the factorization rank 2. Increasing rank increases trainable state and changes the set of possible updates.

```python
w = torch.eye(8)
a = nn.Parameter(torch.ones((8, 2)) / 8)
b = nn.Parameter(torch.zeros((2, 8)))
x = torch.ones((1, 8))
assert a.numel() + b.numel() == 32 and w.numel() == 64
```

**Expected:** adapter 32 parameters versus base64.

**Verify:** For *Count adapter parameters*, a fresh-process check confirms `a.numel() + b.numel() == 32` and `w.numel() == 64`.

## Exercise 2: Check zero initial delta

The question is: Compare x@(W+A@B) with x@W before training.

A zero B eliminates the product while retaining a connected path for B through A. The base prediction is preserved exactly at initialization.

```python
delta = a @ b
initial = x @ (w + delta)
assert torch.equal(delta, torch.zeros((8, 8)))
assert torch.equal(initial, x @ w)
```

**Expected:** both equal ones(1, 8).

**Verify:** For *Check zero initial delta*, a fresh-process check confirms `torch.equal(delta, torch.zeros((8, 8)))` and `torch.equal(initial, x @ w)`.

## Exercise 3: Differentiate the first objective

The question is: Use mean squared error to a zero target and inspect both adapter gradients.

The derivative with respect to A includes B and is zero at this initialization. The derivative with respect to B includes A, which is nonzero, so learning can begin.

```python
saved = w.clone()
loss = initial.square().mean()
loss.backward()
assert torch.count_nonzero(a.grad).item() == 0 and torch.count_nonzero(b.grad).item() > 0
```

**Expected:** A gradient zero; B gradient nonzero.

**Verify:** For *Differentiate the first objective*, a fresh-process check confirms `torch.count_nonzero(a.grad).item() == 0` and `torch.count_nonzero(b.grad).item() > 0`.

## Exercise 4: Update only the adapter

The question is: Take one SGD(0.1) step over A, B.

An optimizer over all model parameters would violate the frozen-base contract. The snapshot directly tests the state that must remain untouched.

```python
before_b = b.detach().clone()
opt = torch.optim.SGD([a, b], lr=0.1)
opt.step()
assert not torch.equal(b, before_b) and torch.equal(w, saved)
```

**Expected:** B changes; W remains exactly equal.

**Verify:** For *Update only the adapter*, a fresh-process check confirms `not torch.equal(b, before_b)` and `torch.equal(w, saved)`.

## Exercise 5: Observe the changed function

The question is: Recompute the zero-target squared error after the adapter step.

The first update changes the function through B. This local decrease demonstrates a working adapter path, not a general optimization guarantee.

```python
after = (x @ (w + a @ b)).square().mean()
assert after.item() < loss.item()
```

**Expected:** loss decreases for this fixture.

**Verify:** For *Observe the changed function*, a fresh-process check confirms `after.item() < loss.item()`.

## Exercise 6: Bound the update rank

The question is: Compute the numerical matrix rank of A@B after the step.

The factorization constrains the rank regardless of optimizer behavior. Multiple adapters or different placement choices can change the overall function class and require separate analysis.

```python
assert int(torch.linalg.matrix_rank((a @ b).detach())) <= 2
```

**Expected:** rank at most 2.

**Verify:** For *Bound the update rank*, a fresh-process check confirms `int(torch.linalg.matrix_rank((a @ b).detach())) <= 2`.

## Review after comparison

Change one input to *Update only the adapter* and predict the result first; keep *Observe the changed function* failing beside the repair. Log a missing PyTorch separately from a wrong low-rank update value in `llm-032`.
