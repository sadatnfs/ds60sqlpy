# torch-007: explanatory solutions

Open these answers only after attempting Leaf tensors, detach, no_grad and gradient accumulation yourself. They reuse the guide's literal inputs, starting from Example A, Inspect leaf and nonleaf state, so a discrepancy points at one step. The executable companion runs the assertions; this page explains why each one tests Leaf tensor, Detach, Gradient accumulation. After a pass, choose a new input for exercise 6, Show eval is separate, without looking.

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

For tensors requiring gradients, a leaf is not the result of a tracked differentiable operation. An intermediate such as `2 * w` has an operation history even when assigned to a named variable. Tensors not requiring gradients are treated as leaves by convention. A conversion or copy operation can therefore change the graph role of a tracked tensor; inspect the actual metadata instead of assuming every user-named tensor is a leaf. [PyTorch 2.9 is_leaf](https://docs.pytorch.org/docs/2.9/generated/torch.Tensor.is_leaf.html).

The first fixture has \(w=0\) and intermediate=2w. Backpropagating that scalar gives incoming sensitivity one at the intermediate and sensitivity two at w. The intermediate's gradient is visible only because retain_grad was requested. Its absence by default would be a storage-policy observation, not evidence that the chain rule failed.

Now reset `w.grad` to None and compute (w-2)². The new contribution is -4. Building the same expression again creates a fresh graph, but backward adds another -4 into the existing gradient buffer, leaving -8. A fresh graph does not clear a previous buffer. Resetting to None before the third computation gives -4 again without changing w itself.

None and numeric zero have different meanings. None may indicate that no gradient has been stored, that a reset occurred, that the tensor was unused, or that an intermediate was not retained. A numeric zero can be the correct derivative of a connected path. Optimizers can also treat them differently: parameters with None gradients are commonly skipped, whereas zero gradients may still interact with momentum or weight decay. This distinction is documented for zero_grad rather than being merely a display detail. [PyTorch 2.9 zero_grad](https://docs.pytorch.org/docs/2.9/generated/torch.optim.Optimizer.zero_grad.html).

The detach example changes shared storage. After detached=source.detach(), writing `detached[0] = 9` changes `source[0]` as well. The earlier source.detach().clone() snapshot remains one because it owns a copy. The snapshot is suitable for comparing later mutation, but detaching a value that the objective actually needs can break learning. Ownership and differentiation must both match the intended interface.

Finally, model.eval() does not stop derivatives through a Linear layer. It changes a module's training flag and the behavior of layers that consult it. no_grad affects ordinary operation recording while leaving the original tensor's `requires_grad` flag unchanged; factory operations with an explicit `requires_grad` argument are a documented exception to treating the scope as a blanket flag rewrite. Keep mode, recording and gradient-buffer decisions separate in the surrounding training or inference function.

## Exercise 1: Predict a nonleaf gradient

The question is: Create leaf v=1.0 and intermediate u=3v, retain u's gradient and backpropagate u*u.

d(u*u)/du=2u=6, and the extra factor du/dv=3 gives 18 at the leaf.

```python
v = torch.tensor(1.0, requires_grad=True)
u = 3 * v
u.retain_grad()
(u * u).backward()
assert v.grad.item() == 18 and u.grad.item() == 6 and not u.is_leaf
```

**Expected:** u.grad is 6 and v.grad is 18; u is not a leaf.

**Verify:** In a fresh process, the exercise checks confirm `v.grad.item() == 18`, `u.grad.item() == 6` and `not u.is_leaf`.

## Exercise 2: Accumulate three backward calls

The question is: At w=1, backpropagate \({\left(w-2\right)}^{2}\) three times without clearing the gradient.

Backward adds into .grad; three fresh graphs each add \(2(w-2)\)=-2.

```python
p = torch.tensor(1.0, requires_grad=True)
for _ in range(3):
    ((p - 2) ** 2).backward()
assert p.grad.item() == -6
```

**Expected:** each call contributes -2, so the stored gradient is -6.

**Verify:** In a fresh process, the exercise checks confirm `p.grad.item() == -6`.

## Exercise 3: Clear with zero_ and with None

The question is: Clear the accumulated gradient with p.grad.zero_() and backpropagate once, then set it to None and backpropagate once more.

zero_ keeps an allocated zero tensor; None removes it, which lets a later check distinguish no gradient from a zero gradient.

```python
p.grad.zero_()
((p - 2) ** 2).backward()
assert p.grad.item() == -2
p.grad = None
assert p.grad is None
((p - 2) ** 2).backward()
assert p.grad.item() == -2
```

**Expected:** both routes end at -2; after the None assignment the gradient is absent until the next backward.

**Verify:** In a fresh process, the exercise checks confirm `p.grad.item() == -2`, `p.grad is None` and `p.grad.item() == -2`.

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

**Verify:** In a fresh process, the exercise checks confirm `source[0].item() == 9`, `owned[0].item() == 1` and `not detached.requires_grad`.

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

**Verify:** In a fresh process, the exercise checks confirm `tracked.requires_grad` and `not observed.requires_grad`.

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

**Verify:** In a fresh process, the exercise checks confirm `result.requires_grad` and `model.training is False`.

## Review after comparison

Repeat exercise 4, Separate detach from ownership, with one changed fixture value and predict the difference before running it. Keep your failing attempt at exercise 5, Use no_grad for an observation, beside the repaired result. A missing framework is not a failing assertion. These solutions use only local fixtures.
