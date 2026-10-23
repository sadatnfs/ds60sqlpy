# torch-027: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Transfer learning reuses a representation while adapting a task-specific head. Freezing requires both a gradient policy and a correct optimizer membership policy. Setting requires_grad=False prevents new derivatives for those parameters, but an optimizer can still contain stale gradient state if the transition is handled care lessly. Clear old gradients and deliberately select trainable parameters. Evaluation mode is a separate concern: a frozen BatchNorm base can still update running buffers if left in training mode.

The local fixture uses a fixed identity base and a new linear head, so a byte-level snapshot can verify that only the head changes. A later unfreeze phase creates a new optimizer with a declared rate and membership list. No pretrained weights are downloaded. The lesson teaches the state transition required for transfer rather than claiming that freezing always improves quality.

**Frozen base:** A reused model component excluded from parameter updates.

**Optimizer membership:** The exact parameters supplied to an optimizer.

**Mode-dependent buffer:** State that can change during forward even without parameter gradients.

**Unfreeze phase:** A deliberate transition to updating previously frozen state.

## Reading the implementation

Call requires_grad_(False) on base parameters, clear their grad fields, and construct the head optimizer from head.parameters only. Use base.eval when its mode-dependent state should remain fixed. Snapshot all base state_dict tensors with clone. After training the head, compare both parameters and buffers. Unfreezing changes the intended update set and requires an explicit optimizer policy.

## Exercise 1: Freeze a known base

The question is: Create a bias-free2-to-2 identity Linear base and disable its parameter gradients.

The identity fixture isolates ownership. A learned base would have different values but should obey the same freeze contract.

```python
base=nn.Linear(2,2,bias=False)
with torch.no_grad(): base.weight.copy_(torch.eye(2))
for parameter in base.parameters(): parameter.requires_grad_(False); parameter.grad=None
x=torch.tensor([[1.,0.],[0.,1.],[1.,1.]])
assert torch.equal(base(x),x) and not any(p.requires_grad for p in base.parameters())
```

**Expected:** base output equals input; all base parameters frozen.

**Verify:** Compare the computed values or written argument with base output equals input; all base parameters frozen.

## Exercise 2: Train a new head

The question is: Attach a zero-initialized2-to-1 head and take one SGD.1 step toward targets1, 2, 3.

The optimizer receives only head parameters. The direct snapshot check proves preservation rather than trusting a flag alone.

```python
head=nn.Linear(2,1,bias=False)
with torch.no_grad(): head.weight.zero_()
base_before=base.weight.detach().clone(); head_before=head.weight.detach().clone(); target=torch.tensor([[1.],[2.],[3.]])
optimizer=torch.optim.SGD(head.parameters(),lr=.1); optimizer.zero_grad(set_to_none=True); loss=(head(base(x))-target).square().mean(); loss.backward(); optimizer.step()
assert not torch.equal(head.weight,head_before) and torch.equal(base.weight,base_before)
```

**Expected:** head changes; base remains exact identity.

**Verify:** Compare the computed values or written argument with head changes; base remains exact identity.

## Exercise 3: Inspect absent base gradients

The question is: Check the frozen base after head backward.

The head can learn from fixed features without differentiating base parameters. This is a computation path with a deliberate gradient boundary.

```python
assert base.weight.grad is None and head.weight.grad is not None
```

**Expected:** base gradient None; head gradient present.

**Verify:** Compare the computed values or written argument with base gradient None; head gradient present.

## Exercise 4: Expose buffer updates despite freezing

The question is: Freeze BatchNorm affine parameters but call it in train mode on a nonzero batch.

requires_grad controls parameter differentiation, not forward-time buffer updates. A frozen representation can still drift through training-mode normalization state.

```python
normalizer=nn.BatchNorm1d(2,momentum=.5)
for parameter in normalizer.parameters(): parameter.requires_grad_(False)
before=normalizer.running_mean.clone(); normalizer.train(); normalizer(torch.tensor([[1.,3.],[3.,5.]]))
assert not torch.equal(before,normalizer.running_mean)
```

**Expected:** running mean changes.

**Verify:** Compare the computed values or written argument with running mean changes.

## Exercise 5: Freeze normalization behavior with eval

The question is: Switch that BatchNorm to eval and call a different batch.

The mode transition addresses a separate state mechanism. It should be part of the transfer design when the base is intended to remain fixed.

```python
normalizer.eval(); fixed=normalizer.running_mean.clone(); normalizer(torch.tensor([[100.,200.]]))
assert torch.equal(fixed,normalizer.running_mean)
```

**Expected:** running mean remains unchanged.

**Verify:** Compare the computed values or written argument with running mean remains unchanged.

## Exercise 6: Begin an explicit unfreeze phase

The question is: Enable base gradients, create a new optimizer over base+head, and take one smaller-rate step.

The new optimizer makes membership and state policy explicit. Reusing an old optimizer without adding the base would leave the unfreeze flag ineffective for updates.

```python
for parameter in base.parameters(): parameter.requires_grad_(True)
combined=torch.optim.SGD(list(base.parameters())+list(head.parameters()),lr=.01); combined.zero_grad(set_to_none=True)
(head(base(x))-target).square().mean().backward(); combined.step()
assert not torch.equal(base.weight,base_before)
```

**Expected:** base weight now changes.

**Verify:** Compare the computed values or written argument with base weight now changes.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
