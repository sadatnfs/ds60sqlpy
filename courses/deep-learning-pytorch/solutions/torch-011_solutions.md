# torch-011: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Annn.Module owns a model's registered parameters, buffers and child modules. Its forward method defines a computation, but the optimizer membership and training loop remain explicit. A plain tensor attribute is not automatically a Parameter. A buffer is tracked state that moves with the module and appears in state_dict without being optimized by default. This distinction is useful for fixed preprocessing statistics, running counts or nontrainable masks.

Calling model(x) routes through Module machinery and forward; it does not calculate a loss or apply an update. A complete loop selects parameters for an optimizer, clears gradients, computes an objective, backpropagates and steps. Replacing a Parameter after constructing an optimizer does not automatically update the optimizer object list. This lesson uses a scalar module to make ownership and membership observable before larger architectures hide them.

**Module:** An object organizing computation and tracked model state.

**Buffer:** Tracked non parameter tensor state.

**Optimizer membership:** The parameter objects explicitly owned by an optimizer.

## Reading the implementation

Define parameters in__init__ after super().__init__, using nn.Parameter or registered child layers. register_buffer names a nontrainable tensor. forward uses those attributes without creating a new parameter on every call. named_parameters and named_buffers expose different state sets. state_dict includes both. An SGD optimizer captures references to the parameter objects supplied at construction.

## Trace module-owned state and optimizer-owned references

The scalar model owns a Parameter named weight and a buffer named offset. Both are scalar float64 tensors, but only weight is selected by model.parameters(). Its forward expression is weight*x+offset. The offset influences predictions while remaining fixed under the demonstrated SGD step because it is not in that optimizer's parameter list.

| Item | Registered category | In parameters() | In default state_dict() | Changed by this SGD step |
| --- | --- | --- | --- | --- |
| weight | Parameter | Yes | Yes | Yes |
| offset | Persistent buffer | No | Yes | No |
| An arbitrary plain tensor attribute | Ordinary attribute | No | No | Only if separately managed |

These are registration defaults, not a law that buffers can never participate in autograd or that every registered Parameter must be trainable. requires_grad and optimizer membership remain separate choices. A buffer registered with persistent=False still follows module conversion but is omitted from state_dict. The supplied offset uses the default persistent behavior. [PyTorch 2.9 Module state APIs](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Module.html).

A call to model(x) routes through Module machinery and its forward method. At weight=offset=0, the three inputs 1, 2, 3 produce three zeros. No loss, backward call or optimizer step is implied by that invocation. The explicit loop then clears gradients, computes the paired mean squared objective, backpropagates and applies SGD. The one-step weight \(\frac{28}{15}\) is the same scalar oracle as the earlier chapter, while offset remains zero.

Converting the module to float32 moves both registered tensors through the module conversion mechanism. A plain auxiliary tensor could remain at its old dtype or device and later cause an operation mismatch. This example checks CPU dtype movement; it does not qualify a GPU placement path. In a larger model, also inspect optimizer state after a late conversion because momentum or other optimizer tensors have their own lifecycle.

Object identity makes the stale-optimizer failure concrete. At construction, the optimizer stores a reference to the original weight object. Replacing fresh.weight with a new Parameter changes what forward reads, but the old optimizer list still refers to the former object. A new backward can populate the replacement's grad while step examines the old object's gradient instead. Rebuilding or deliberately editing parameter groups is therefore part of the model-change operation, not an optional cleanup detail.

Creating Parameters inside forward causes a related failure. Repeated calls can create new objects after the optimizer captured its membership, so the current computation and the objects being updated diverge. A stable model should preserve its intended parameter identities across batch sizes unless it implements a deliberate, tested dynamic-state policy. The final exercise compares calls of length one and four for that reason.

State serialization also has a boundary. state_dict supplies a mapping of registered parameter and persistent-buffer state, but it is not automatically an immutable historical snapshot of independent storage. If a diagnostic must survive later in-place model mutation, clone the relevant values or serialize them at a defined point. Later checkpoint lessons distinguish a saved model state from optimizer, RNG and data-order state needed for a training restart.

For the paired Keras model, compare the represented function before comparing the training interface. A no-bias Dense kernel and the zero-offset scalar PyTorch model can represent the same map, but their storage layouts and construction APIs differ. Explicitly match dtype, denominator and update budget; a high-level training call can report a pre-update loss just as a retained PyTorch loss tensor can.

## Exercise 1: Inspect module state

The question is: Build Scalar Model with weight 0 and buffer offset 0.

The buffer is serialized and follows device/dtype conversions, but it is not an optimizer parameter. A plain attribute would not provide the same tracking contract.

```python
model=ScalarModel()
assert set(dict(model.named_parameters()))=={'weight'} and set(dict(model.named_buffers()))=={'offset'}
assert set(model.state_dict())=={'weight','offset'}
```

**Expected:** one parameter weight; one buffer offset; both in state_dict.

**Verify:** Compare the computed values or written argument with one parameter weight; one buffer offset; both in state_dict.

## Exercise 2: Check a forward call

The question is: Runx 1, 2, 3 through the zero-weight module.

A forward call only computes the current function. Neither parameter registration nor calling the module performs training.

```python
x=torch.tensor([1.,2.,3.],dtype=torch.float64); y=2*x
assert torch.equal(model(x),torch.zeros_like(x)) and model.weight.item()==0
```

**Expected:** three zero outputs; weight unchanged.

**Verify:** Compare the computed values or written argument with three zero outputs; weight unchanged.

## Exercise 3: Run one explicit loop step

The question is: Use SGD with rate 0.1 and mean squared error, clearing gradients before backward.

The optimizer consumes only the registered Parameter. The buffer influences forward but remains fixed under this update.

```python
optimizer=torch.optim.SGD(model.parameters(),lr=.1); optimizer.zero_grad(set_to_none=True)
loss=((model(x)-y)**2).mean(); loss.backward(); optimizer.step()
np.testing.assert_allclose(model.weight.item(),28/15,atol=1e-12,rtol=0); assert model.offset.item()==0
```

**Expected:** weight \(\frac{28}{15}\); buffer still 0.

**Verify:** Compare the computed values or written argument with weight \(\frac{28}{15}\); buffer still 0.

## Exercise 4: Move dtype through registered state

The question is: Convert the module to float32 and inspect parameter and buffer dtypes.

Tracking gives the module a consistent state-conversion mechanism. Ad hoc tensor attributes can remain on an incompatible dtype or device.

```python
model=model.to(dtype=torch.float32)
assert model.weight.dtype==torch.float32 and model.offset.dtype==torch.float32
```

**Expected:** both float32.

**Verify:** Compare the computed values or written argument with both float32.

## Exercise 5: Expose stale optimizer membership

The question is: Create an optimizer, replace the module Parameter, and inspect captured object identity.

An optimizer list is not a live query over the module. Replacing trainable state requires an explicit optimizer reconstruction or parameter-group policy.

```python
fresh=ScalarModel(); old=fresh.weight; stale=torch.optim.SGD(fresh.parameters(),lr=.1); fresh.weight=nn.Parameter(torch.tensor(5.,dtype=torch.float64))
assert stale.param_groups[0]['params'][0] is old and stale.param_groups[0]['params'][0] is not fresh.weight
```

**Expected:** optimizer still holds old Parameter, not replacement.

**Verify:** Compare the computed values or written argument with optimizer still holds old Parameter, not replacement.

## Exercise 6: Keep parameter count stable across calls

The question is: Call a fresh module on batches of length 1 and 4 and compare parameter identities.

Creating Parameters inside forward would make the model change with each batch. Persistent state belongs in a deliberate construction path.

```python
stable=ScalarModel(); identity=id(stable.weight); stable(torch.ones(1,dtype=torch.float64)); stable(torch.ones(4,dtype=torch.float64))
assert id(stable.weight)==identity and len(list(stable.parameters()))==1
```

**Expected:** same weight object and one parameter.

**Verify:** Compare the computed values or written argument with same weight object and one parameter.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
