# torch-007: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

PyTorch distinguishes graph tracking from gradient storage. A leaf tensor is a graph input created by the user or a registered parameter, while intermediate tensors have operation history. backward accumulates gradients into `leaf.grad` by default. Calling backward twice on newly computed losses without clearing gradients adds the contributions. A nonleaf can retain its gradient when retain_grad is requested, but that is a diagnostic choice rather than the default storage policy.

Detach removes a value from its current graph while sharing storage; clone copies storage while preserving a differentiable relationship. no_grad prevents recording operations in its scope. model.eval changes behavior of modules such as Dropout and BatchNorm, but does not disable autograd. These controls solve different problems and should not be used interchangeably.

**Leaf tensor:** An input or parameter whose gradient is accumulated by backward.

**Detach:** Removing a value from an existing autograd graph without necessarily copying storage.

**Gradient accumulation:** Adding new backward contributions into an existing grad field.

**Gradient mode:** Whether new operations are recorded for differentiation.

## Reading the implementation

Set `requires_grad` on floating-point inputs that need derivatives. Use backward for accumulated leaf gradients and `zero_grad(set_to_none=True)` between independent optimizer steps. detached=value.detach() does not allocate independent storage; use value.detach().clone() for an owned logging snapshot. Check is_leaf and grad_fn to understand the graph role rather than guessing from a variable name.

## Separate four kinds of state

A tensor's value, storage aliases, graph role and stored gradient are related but different facts. Module mode adds another independent control:

| Control or observation | What it changes or reports | What it does not establish |
| --- | --- | --- |
| `requires_grad` | Whether relevant operations can be tracked for derivatives | Independent storage or optimizer membership |
| is_leaf and grad_fn | Role in the recorded graph | Whether the Python variable name sounds like a parameter |
| backward | Adds derivative contributions to eligible stored gradients | A parameter update |
| detach | Removes the current differentiation connection | A copy of storage |
| clone | Copies storage | A detached gradient history |
| no_grad | Suppresses recording for ordinary operations in its scope | Evaluation behavior of Dropout or BatchNorm |
| eval | Selects evaluation behavior of affected modules | Disabled autograd or cleared gradients |

For tensors requiring gradients, a leaf is not the result of a tracked differentiable operation. An intermediate such as 2 w has an operation history even when assigned to a named variable. Tensors not requiring gradients are treated as leaves by convention. A conversion or copy operation can therefore change the graph role of a tracked tensor; inspect the actual metadata instead of assuming every user-named tensor is a leaf. [PyTorch 2.9 is_leaf](https://docs.pytorch.org/docs/2.9/generated/torch.Tensor.is_leaf.html).

The first fixture has \(w=0\) and intermediate=2w. Backpropagating that scalar gives incoming sensitivity one at the intermediate and sensitivity two at w. The intermediate's gradient is visible only because retain_grad was requested. Its absence by default would be a storage-policy observation, not evidence that the chain rule failed.

Now reset `w.grad` to None and compute(w-2)². The new contribution is -4. Building the same expression again creates a fresh graph, but backward adds another -4 into the existing gradient buffer, leaving -8. A fresh graph does not clear a previous buffer. Resetting to None before the third computation gives -4 again without changing w itself.

None and numeric zero have different meanings. None may indicate that no gradient has been stored, that a reset occurred, that the tensor was unused, or that an intermediate was not retained. A numeric zero can be the correct derivative of a connected path. Optimizers can also treat them differently: parameters with None gradients are commonly skipped, whereas zero gradients may still interact with momentum or weight decay. This distinction is documented for zero_grad rather than being merely a display detail. [PyTorch 2.9 zero_grad](https://docs.pytorch.org/docs/2.9/generated/torch.optim.Optimizer.zero_grad.html).

The detach example changes shared storage. After detached=source.detach(), writing detached[0]=9 changes source[0] as well. The earlier source.detach().clone() snapshot remains one because it owns a copy. The snapshot is suitable for comparing later mutation, but detaching a value that the objective actually needs can break learning. Ownership and differentiation must both match the intended interface.

Finally, model.eval() does not stop derivatives through a Linear layer. It changes a module's training flag and the behavior of layers that consult it. no_grad affects ordinary operation recording while leaving the original tensor's `requires_grad` flag unchanged; factory operations with an explicit `requires_grad` argument are a documented exception to treating the scope as a blanket flag rewrite. Keep mode, recording and gradient-buffer decisions separate in the surrounding training or inference function.

## Exercise 1: Inspect leaf and nonleaf state

The question is: Create a leaf tensor \(w=0\) and intermediate tensor \(u=2w\), retain the intermediate gradient and backpropagate its sum.

Leaf status follows graph construction, not whether a tensor is assigned to a Python variable. retain_grad explicitly requests storage for the intermediate diagnostic.

```python
w = torch.tensor(0.0, requires_grad=True)
intermediate = 2 * w
intermediate.retain_grad()
intermediate.backward()
assert (
    w.is_leaf and not intermediate.is_leaf and w.grad.item() == 2 and intermediate.grad.item() == 1
)
```

**Expected:** `w.is_leaf` is `True`; `u.is_leaf` is `False`; the gradients with respect to \(w\) and \(u\) are 2 and 1.

**Verify:** Compare the computed values or written argument with `w.is_leaf` is `True`; `u.is_leaf` is `False`; the gradients with respect to \(w\) and \(u\) are 2 and 1.

## Exercise 2: Observe accumulation across fresh graphs

The question is: Compute \({\left(w-2\right)}^{2}\) twice at \(w=0\) without clearing grad.

The second forward creates a new graph, but backward still adds into the existing leaf gradient buffer. Graph freshness does not imply gradient-buffer freshness.

```python
w.grad = None
((w - 2) ** 2).backward()
assert w.grad.item() == -4
((w - 2) ** 2).backward()
assert w.grad.item() == -8
```

**Expected:** after resetting first, grad -4 then -8.

**Verify:** Compare the computed values or written argument with after resetting first, grad -4 then -8.

## Exercise 3: Clear before an independent step

The question is: Set grad None and backpropagate once more.

This is the intended reset for independent batches. Intentional microbatch accumulation needs a separate scaling and update policy.

```python
w.grad = None
((w - 2) ** 2).backward()
assert w.grad.item() == -4
```

**Expected:** grad returns to-4.

**Verify:** Compare the computed values or written argument with grad returns to-4.

## Exercise 4: Separate detach from ownership

The question is: Detach a tensor, mutate the detached view, and compare with a detached clone.

Detach cuts gradient history but does not promise a copy. A logging snapshot that must survive later mutation should clone its storage.

```python
source = torch.tensor([1.0, 2.0], requires_grad=True)
detached = source.detach()
owned = source.detach().clone()
detached[0] = 9
assert source[0].item() == 9 and owned[0].item() == 1 and not detached.requires_grad
```

**Expected:** shared original changes; owned clone stays unchanged.

**Verify:** Compare the computed values or written argument with shared original changes; owned clone stays unchanged.

## Exercise 5: Use no_grad for an observation

The question is: Multiply a `requires_grad` tensor inside and outside no_grad.

The scope affects new operation recording. It does not change the original tensor `requires_grad` flag.

```python
value = torch.tensor(2.0, requires_grad=True)
tracked = value * 3
with torch.no_grad():
    observed = value * 3
assert tracked.requires_grad and not observed.requires_grad
```

**Expected:** tracked result `requires_grad` True; observed result False.

**Verify:** Compare the computed values or written argument with tracked result `requires_grad` True; observed result False.

## Exercise 6: Show eval is separate

The question is: Put a Linear module in eval mode, run a differentiable input, and inspect output tracking.

Evaluation mode changes module behavior, not the global autograd mode. Use no_grad or inference_mode separately for inference when appropriate.

```python
model = nn.Linear(1, 1)
model.eval()
result = model(torch.tensor([[1.0]], requires_grad=True))
assert result.requires_grad and model.training is False
```

**Expected:** the output still has `requires_grad=True`.

**Verify:** Compare the computed values or written argument with the output still has `requires_grad=True`.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
