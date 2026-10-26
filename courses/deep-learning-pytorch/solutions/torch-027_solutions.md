# torch-027: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Transfer learning reuses a representation while adapting a task-specific head. Freezing requires both a gradient policy and a correct optimizer membership policy. Setting `requires_grad=False` prevents new derivatives for those parameters, but an optimizer can still contain stale gradient state if the transition is handled carelessly. Clear old gradients and deliberately select trainable parameters. Evaluation mode is a separate concern: a frozen BatchNorm base can still update running buffers if left in training mode.

The local fixture uses a fixed identity base and a new linear head, so a byte-level snapshot can verify that only the head changes. A later unfreeze phase creates a new optimizer with a declared rate and membership list. No pretrained weights are downloaded. The lesson teaches the state transition required for transfer rather than claiming that freezing always improves quality.

**Frozen base:** A reused model component excluded from parameter updates.

**Optimizer membership:** The exact parameters supplied to an optimizer.

**Mode-dependent buffer:** State that can change during forward even without parameter gradients.

**Unfreeze phase:** A deliberate transition to updating previously frozen state.

## Reading the implementation

Call requires_grad_(False) on base parameters, clear their grad fields, and construct the head optimizer from head.parameters only. Use base.eval when its mode-dependent state should remain fixed. Snapshot all base state_dict tensors with clone. After training the head, compare both parameters and buffers. Unfreezing changes the intended update set and requires an explicit optimizer policy.

## Trace what freezing preserves and what it does not

The base is a bias-free 2-to-2 Linear layer initialized to identity. Its stored weight has shape(2, 2), and base(x)=x for the three fixture rows. The head has shape(1, 2) and begins at zero. Disabling base parameter gradients and supplying only head.parameters() to SGD establishes two distinct boundaries: the base does not receive new parameter derivatives, and the optimizer is not asked to update it.

The head update has an independent analytic value. With targets[1, 2, 3], zero predictions and mean squared error, the residuals are[-1, -2, -3]. The head gradient is(2/3) times the feature-weighted residual sum, namely[-8/3, -10/3]. SGD at 0.1 produces head weights[4/15, \(\frac{1}{3}\)] and predictions[4/15, \(\frac{1}{3}\), 3/5]. This explains both the observed nonzero head update and why the base need not change for the head to learn.

When the base is later unfrozen, the derivative path through it becomes relevant. If its stored weight is B and the head row is h, features are \(XB^{\mathsf T}\) and logits are \(XB^{\mathsf T}h^{\mathsf T}\). The base gradient combines the output residuals with h and X. After the head has nonzero weights, that gradient can be nonzero. Enabling `requires_grad` does not add B to an optimizer that was constructed from head parameters only. The update set must be changed deliberately.

A parameter can remain in an optimizer after `requires_grad` becomes false. That flag prevents new gradient construction for the leaf, but it does not erase an old `.grad` tensor. An optimizer step using that stale tensor can still change the parameter. Clear stored gradients at the phase boundary and inspect the exact optimizer-held objects. For the supplied built-in update policy, `grad=None` skips the corresponding update; an allocated zero gradient and a missing gradient are not interchangeable in every state/decay situation.

Freezing parameters is also different from wrapping computation in no_grad. If a trainable upstream adapter needs gradients through a fixed base, its input derivative must remain connected even though base parameters are frozen. no_grad around the whole base would sever that upstream path. Conversely, when features are truly fixed and no earlier component is trained, avoiding unnecessary graph construction can be an intentional efficiency choice. State the intended gradient destination first.

Mode-dependent buffers form another axis. BatchNorm affine weights can be frozen while training-mode forward still updates running mean, running variance and batch counters. Dropout can remain stochastic without any trainable parameter of its own. base.eval() changes those module behaviors; it does not disable autograd or alter optimizer membership. A later parent_model.train() can recursively put the base back into training mode, so the intended fixed-mode policy must be restored or encoded deliberately in the training procedure.

A freeze receipt should compare the complete intended tensor state, not just the Linear weight. Clone the relevant state_dict tensors before the phase so the snapshot does not alias later mutations. Record mode flags separately because they are not ordinary learned tensors in state_dict. The tiny Linear base has no running statistics, while the separate BatchNorm exercise makes this hidden-state issue observable.

At unfreeze, there are two different optimizer-state policies. A new optimizer resets momentum/adaptive state for the head as well as introducing the base, which changes the trajectory. add_param_group can preserve existing head state while adding previously excluded parameters with explicit group options. It requires avoiding duplicate membership and deciding rates, decay and scheduler behavior for the new group. The API supports this use, but the resulting experiment still needs its own state receipt. [PyTorch 2.9 add_param_group](https://docs.pytorch.org/docs/2.9/generated/torch.optim.Optimizer.add_param_group.html).

The paired Keras guide uses trainable flags and a deliberate training argument for the base. Those mechanisms are not a one-to-one spelling substitution for PyTorch `requires_grad`, optimizer lists and train/eval. In either framework, verify before/after tensors, buffer behavior and actual updated identities. The local identity base is a controlled ownership fixture, not a downloaded pretrained model or evidence that transfer will improve an unseen task.

## Exercise 1: Freeze a known base

The question is: Create a bias-free 2-to-2 identity Linear base and disable its parameter gradients.

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

The question is: Attach a zero-initialized 2-to-1head and take one SGD.1step toward targets 1, 2, 3.

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

`requires_grad` controls parameter differentiation, not forward-time buffer updates. A frozen representation can still drift through training-mode normalization state.

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
