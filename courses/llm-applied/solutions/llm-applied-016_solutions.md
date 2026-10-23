# llm-applied-016: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Low-rank adaptation freezes a base weight matrix and learns a smaller additive update. Under the row-vector convention used here, the effective matrix isW+(alpha/r)A@B, withW8x8, A8x2 andB2x8. Rankr2 gives32 trainable adapter entries compared with 64 base entries. The scaling factoralpha/r is part of the function and changes gradients. Some libraries store Linear weights transposed relative to this equation, so shapes must be translated explicitly.

InitializeA to small nonzero values andB to zero. The initial delta is zero, preserving the base function. On the first step, the gradient ofA is zero because it containsB, whileB receives a gradient throughA. This is a connected zero gradient, not a missing path. AfterB changes, later updates can changeA too. The chapter performs actual PyTorch SGD updates and checks frozen-base identity, parameter counts and merged inference parity. It demonstrates LoRA mechanics on a small matrix, not the quality of adapting a pretrained assistant.

**Adapter rank:** The inner dimension limiting the rank of the update matrix.

**LoRA scale:** The multiplieralpha/r applied to the low-rank product.

**Frozen base:** Weights excluded from gradient updates during adaptation.

**Merged inference:** An equivalent matrix with the adapter delta added for serving.

## Reading the implementation

CreateW as a nontrainable tensor andA/B asParameters. Pass onlyA andB to the optimizer. Compute output=x@(W+scale*A@B). SnapshotW before training and assert exact equality afterward. Merge into a new matrix for inference and compare with the unmerged computation. Do not mutate the original base when creating the merged artifact, because that would change other adapters sharing it.

## Exercise 1: Count and orient parameters

The question is: ConstructW=I8, A=ones(8, 2)/8, B=zeros(2, 8), rank 2, alpha 4.

The orientation is chosen for row-vector inputs. A framework Linear layer storing(out, in) weights would require a transposed formulation rather than copying these shapes blindly.

```python
w=torch.eye(8); a=nn.Parameter(torch.ones((8,2))/8); b=nn.Parameter(torch.zeros((2,8))); rank=2; alpha=4; scale=alpha/rank; x=torch.ones((1,8))
assert w.numel()==64 and a.numel()+b.numel()==32 and scale==2
```

**Expected:** base64 entries; adapter32; scale2.

**Verify:** Compare the computed values or written argument with base64 entries; adapter32; scale2.

## Exercise 2: Prove zero-delta initialization

The question is: Compare the effective output with the frozen base before updating.

The initial adapter does not perturb the base. This is useful for controlled comparisons and explains why one factor starts at zero.

```python
initial=x@(w+scale*(a@b)); saved=w.clone()
assert torch.equal(initial,x@w) and torch.equal(a@b,torch.zeros((8,8)))
```

**Expected:** outputs exactly equalones(1, 8).

**Verify:** Compare the computed values or written argument with outputs exactly equalones(1, 8).

## Exercise 3: Inspect the first gradients

The question is: Minimize mean squared output towardzero and backpropagate once.

The zero derivative ofA follows algebraically fromB=0. Treating it as a disconnected parameter would be a mistaken diagnosis.

```python
loss=initial.square().mean(); loss.backward()
assert torch.count_nonzero(a.grad).item()==0 and torch.count_nonzero(b.grad).item()>0 and w.grad is None
```

**Expected:** A gradientzero; B gradientnonzero; W has no gradient.

**Verify:** Compare the computed values or written argument with A gradientzero; B gradientnonzero; W has no gradient.

## Exercise 4: Take an adapter-only step

The question is: UseSGD.1 onA/B and recalculate the objective.

The optimizer receives only adapter parameters. The direct base comparison catches accidental updates outside that optimizer list.

```python
before_b=b.detach().clone(); opt=torch.optim.SGD([a,b],lr=.1); opt.step(); after=x@(w+scale*(a@b))
assert not torch.equal(before_b,b) and after.square().mean()<loss and torch.equal(w,saved)
```

**Expected:** B changes; loss decreases; W remains byte-identical.

**Verify:** Compare the computed values or written argument with B changes; loss decreases; W remains byte-identical.

## Exercise 5: Merge without changing the base

The question is: Create a detached merged matrix and compare predictions with the unmerged expression.

Merging is an inference representation change. Preserve adapter and base identities so the artifact can be reconstructed or replaced without contaminating shared state.

```python
merged=w.detach().clone()+scale*(a@b).detach()
torch.testing.assert_close(x@merged,after.detach(),atol=1e-6,rtol=0)
assert torch.equal(w,saved)
```

**Expected:** parity within1e-6; originalW unchanged.

**Verify:** Compare the computed values or written argument with parity within1e-6; originalW unchanged.

## Exercise 6: Inspect rank and scaling consequences

The question is: Check the numerical rank of the update and comparealpha4 withalpha2 using the same factors.

Rank limits the update space, while scaling changes its magnitude. They are different hyperparameters and should not be conflated when comparing adapters.

```python
delta=(a@b).detach(); assert int(torch.linalg.matrix_rank(delta))<=2
torch.testing.assert_close((4/rank)*delta,2*((2/rank)*delta),atol=1e-6,rtol=0)
```

**Expected:** rank at most2; delta atalpha4 is twice delta atalpha2.

**Verify:** Compare the computed values or written argument with rank at most2; delta atalpha4 is twice delta atalpha2.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
