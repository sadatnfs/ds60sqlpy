# torch-027: explanatory solutions

Open these answers only after attempting Transfer learning, frozen layers and optimizer membership yourself. They reuse the guide's literal inputs, starting from Example A, Freeze a known base, so a discrepancy points at one step. The executable companion runs the assertions; this page explains why each one tests Frozen base, Optimizer membership, Mode-dependent buffer. After a pass, choose a new input for exercise 6, Begin an explicit unfreeze phase, without looking.

After comparing, follow the [review steps](../STUDY-GUIDE.md#after-the-solutions).

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

The base is a bias-free 2-to-2 Linear layer initialized to identity. Its stored weight has shape (2, 2), and base(x)=x for the three fixture rows. The head has shape (1, 2) and begins at zero. Disabling base parameter gradients and supplying only head.parameters() to SGD establishes two distinct boundaries: the base does not receive new parameter derivatives, and the optimizer is not asked to update it.

The head update has an independent analytic value. With targets [1, 2, 3], zero predictions and mean squared error, the residuals are [-1, -2, -3]. The head gradient is (2/3) times the feature-weighted residual sum, namely [-8/3, -10/3]. SGD at 0.1 produces head weights [4/15, \(\frac{1}{3}\)] and predictions [4/15, \(\frac{1}{3}\), 3/5]. This explains both the observed nonzero head update and why the base need not change for the head to learn.

When the base is later unfrozen, the derivative path through it becomes relevant. If its stored weight is B and the head row is h, features are \(XB^{\mathsf T}\) and logits are \(XB^{\mathsf T}h^{\mathsf T}\). The base gradient combines the output residuals with h and X. After the head has nonzero weights, that gradient can be nonzero. Enabling `requires_grad` does not add B to an optimizer that was constructed from head parameters only. The update set must be changed deliberately.

A parameter can remain in an optimizer after `requires_grad` becomes false. That flag prevents new gradient construction for the leaf, but it does not erase an old `.grad` tensor. An optimizer step using that stale tensor can still change the parameter. Clear stored gradients at the phase boundary and inspect the exact optimizer-held objects. For the supplied built-in update policy, `grad=None` skips the corresponding update; an allocated zero gradient and a missing gradient are not interchangeable in every state/decay situation.

Freezing parameters is also different from wrapping computation in no_grad. If a trainable upstream adapter needs gradients through a fixed base, its input derivative must remain connected even though base parameters are frozen. no_grad around the whole base would sever that upstream path. Conversely, when features are truly fixed and no earlier component is trained, avoiding unnecessary graph construction can be an intentional efficiency choice. State the intended gradient destination first.

Mode-dependent buffers form another axis. BatchNorm affine weights can be frozen while training-mode forward still updates running mean, running variance and batch counters. Dropout can remain stochastic without any trainable parameter of its own. base.eval() changes those module behaviors; it does not disable autograd or alter optimizer membership. A later parent_model.train() can recursively put the base back into training mode, so the intended fixed-mode policy must be restored or encoded deliberately in the training procedure.

A freeze receipt should compare the complete intended tensor state, not just the Linear weight. Clone the relevant state_dict tensors before the phase so the snapshot does not alias later mutations. Record mode flags separately because they are not ordinary learned tensors in state_dict. The tiny Linear base has no running statistics, while the separate BatchNorm exercise makes this hidden-state issue observable.

At unfreeze, there are two different optimizer-state policies. A new optimizer resets momentum/adaptive state for the head as well as introducing the base, which changes the trajectory. add_param_group can preserve existing head state while adding previously excluded parameters with explicit group options. It requires avoiding duplicate membership and deciding rates, decay and scheduler behavior for the new group. The API supports this use, but the resulting experiment still needs its own state receipt. [PyTorch 2.9 add_param_group](https://docs.pytorch.org/docs/2.9/generated/torch.optim.Optimizer.add_param_group.html).

The paired Keras guide uses trainable flags and a deliberate training argument for the base. Those mechanisms are not a one-to-one spelling substitution for PyTorch `requires_grad`, optimizer lists and train/eval. In either framework, verify before/after tensors, buffer behavior and actual updated identities. The local identity base is a controlled ownership fixture, not a downloaded pretrained model or evidence that transfer will improve an unseen task.

## Exercise 1: Freeze a scaling base

The question is: Create a bias-free 2-to-2 base whose weight is 2 times the identity, freeze it and evaluate the row [1, 2].

Freezing changes trainability, not the function the base computes.

```python
doubling = nn.Linear(2, 2, bias=False)
with torch.no_grad():
    doubling.weight.copy_(2 * torch.eye(2))
doubling.requires_grad_(False)
probe_x = torch.tensor([[1.0, 2.0]])
assert doubling(probe_x).tolist() == [[2.0, 4.0]] and not doubling.weight.requires_grad
```

**Expected:** output [[2, 4]]; the base weight does not require gradients.

**Verify:** In a fresh process, the exercise checks confirm `doubling(probe_x).tolist() == [[2.0, 4.0]]` and `not doubling.weight.requires_grad`.

## Exercise 2: Predict the head update

The question is: Attach a zero-initialized bias-free 2-to-1 head, take one SGD step with learning rate 0.1 toward target 1 using mean squared error.

The head sees features [2, 4]; the gradient 2(0-1)[2, 4] times -0.1 gives [0.4, 0.8].

```python
new_head = nn.Linear(2, 1, bias=False)
with torch.no_grad():
    new_head.weight.zero_()
head_opt = torch.optim.SGD(new_head.parameters(), lr=0.1)
head_opt.zero_grad(set_to_none=True)
(new_head(doubling(probe_x)) - torch.tensor([[1.0]])).square().mean().backward()
head_opt.step()
torch.testing.assert_close(new_head.weight, torch.tensor([[0.4, 0.8]]), atol=1e-6, rtol=0)
assert doubling.weight.grad is None
```

**Expected:** head weight [0.4, 0.8]; the base receives no gradient.

**Verify:** In a fresh process, the exercise checks confirm `new_head.weight` matches `torch.tensor([[0.4, 0.8]])` within 1e-06 and `doubling.weight.grad is None`.

## Exercise 3: Count trainable parameters

The question is: Count the scalars that still require gradients across the frozen base and the new head.

Only the head's two weights are trainable; the four frozen base weights are excluded.

```python
trainable = sum(
    p.numel() for p in [*doubling.parameters(), *new_head.parameters()] if p.requires_grad
)
assert trainable == 2
```

**Expected:** 2 trainable scalars, all in the head.

**Verify:** In a fresh process, the exercise checks confirm `trainable == 2`.

## Exercise 4: Expose buffer updates despite freezing

The question is: Freeze BatchNorm affine parameters but call it in train mode on a nonzero batch.

`requires_grad` controls parameter differentiation, not forward-time buffer updates. A frozen representation can still drift through training-mode normalization state.

```python
normalizer = nn.BatchNorm1d(2, momentum=0.5)
for parameter in normalizer.parameters():
    parameter.requires_grad_(False)
before = normalizer.running_mean.clone()
normalizer.train()
normalizer(torch.tensor([[1.0, 3.0], [3.0, 5.0]]))
assert not torch.equal(before, normalizer.running_mean)
```

**Expected:** running mean changes.

**Verify:** In a fresh process, the exercise checks confirm `not torch.equal(before, normalizer.running_mean)`.

## Exercise 5: Freeze normalization behavior with eval

The question is: Switch that BatchNorm to eval and call a different batch.

The mode transition addresses a separate state mechanism. It should be part of the transfer design when the base is intended to remain fixed.

```python
normalizer.eval()
fixed = normalizer.running_mean.clone()
normalizer(torch.tensor([[100.0, 200.0]]))
assert torch.equal(fixed, normalizer.running_mean)
```

**Expected:** running mean remains unchanged.

**Verify:** In a fresh process, the exercise checks confirm `torch.equal(fixed, normalizer.running_mean)`.

## Exercise 6: Begin an explicit unfreeze phase

The question is: Enable base gradients, create a new optimizer over base+head, and take one smaller-rate step.

The new optimizer makes membership and state policy explicit. Reusing an old optimizer without adding the base would leave the unfreeze flag ineffective for updates.

```python
for parameter in base.parameters():
    parameter.requires_grad_(True)
combined = torch.optim.SGD(list(base.parameters()) + list(head.parameters()), lr=0.01)
combined.zero_grad(set_to_none=True)
(head(base(x)) - target).square().mean().backward()
combined.step()
assert not torch.equal(base.weight, base_before)
```

**Expected:** base weight now changes.

**Verify:** In a fresh process, the exercise checks confirm `not torch.equal(base.weight, base_before)`.

