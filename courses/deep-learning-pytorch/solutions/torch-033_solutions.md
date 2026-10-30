# torch-033: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Inference is a bounded function with an input and output contract. A model may accept many tensors that are syntactically legal but semantically wrong: missing batch axes, wrong feature order, unexpected dtype, nonfinite values or an oversized request. Validate these conditions before forward computation. Batching should preserve each record's prediction for a stateless model in the declared evaluation mode.

PyTorch inference_mode disables more autograd bookkeeping than no_grad and creates tensors with restrictions relevant to later gradient use. It is appropriate for a pure inference boundary, but should not be substituted blindly into training or gradient-based analysis. model.eval remains necessary for mode-dependent layers. This lesson uses a fixed linear model and no server, deployment or GPU so the contract can be tested locally.

**Inference mode:** A PyTorch context disabling gradient recording and additional bookkeeping.

**Input contract:** The accepted shape, dtype, device, range and budget for prediction.

**Batch independence:** Agreement of a record predicted alone or with other records.

**Owned output:** Returned storage that cannot mutate caller or model state.

## Reading the implementation

The predict helper requires a CPU float32 tensor shaped(batch, 2), with batch size 1..4 and finite entries. It calls model.eval and uses inference_mode, then returns an owned clone suitable for caller inspection. The coefficient vector[2, -1] supplies an independent output oracle. Treat shape, dtype, device and value validation as different diagnostics rather than silently coercing every input.

## Trace validation, mode, storage and batching as separate boundaries

The function accepts a CPU float32 tensor shaped(B, 2), with \(1\le B\le 4\) and finite entries. Those checks occur before the model call. They are not interchangeable: an integer matrix has the wrong representation policy, a one-dimensional vector lacks the required batch axis, a three-feature matrix has the wrong schema, and a five-row matrix exceeds the declared work bound. A predictable validation order helps callers diagnose the first rejected condition.

The model computes 2 x_0-x_1. For[1, 2] and[3, 4], the results are zero and two. Linear returns(B, 1), and squeeze(-1) removes only the known singleton output-feature axis to produce(B). A blanket squeeze() would also remove the batch axis when \(B=1\), creating a scalar result and breaking a stable one-result-per-record interface. This is why axis-specific shape operations belong in the API contract.

model.eval() changes mode-dependent behavior such as ordinary Dropout and BatchNorm. It does not disable autograd. no_grad disables ordinary reverse-mode recording for operations in its scope. inference_mode removes additional bookkeeping, including some view/version tracking, and also has restrictions relevant to later differentiation. The choice should follow the consumer's intended use, not a rule that one context is always faster or universally better. [PyTorch 2.9 inference_mode](https://docs.pytorch.org/docs/2.9/generated/torch.autograd.grad_mode.inference_mode.html).

The worked function leaves inference_mode before cloning the result. That clone gives the caller independent normal tensor storage with requires_grad false under this path. It does not reconnect a gradient to the original model computation. The output can be inspected and mutated without changing caller input or model state. Cloning inside the inference context would still create an inference tensor, so the location of the operation matters if later ordinary tensor behavior is part of the interface.

For this stateless affine model, each row's output depends only on that row and fixed weights. Predicting one row alone or alongside the other must therefore agree. A training-mode BatchNorm layer could depend on neighboring records, and some models intentionally contain cross-record operations. A model configured without running BatchNorm statistics can also retain batch-dependent behavior in evaluation. Batch independence is a tested property of this predictor, not a universal theorem about eval().

Record identity remains necessary even when numeric parity holds. Concatenating singleton predictions in a different order can create a correctly shaped but misaligned result. A future batching service must preserve request-to-row mapping, not merely return the correct multiset of values. The local helper starts no server and proves no authentication, queueing, cancellation or concurrent-serving behavior.

The model object is dedicated to this teaching inference path. Calling eval on a model simultaneously shared with a training loop would mutate shared mode state. An output clone cannot repair that ownership problem. A real integration should define separate model instances or a deliberate synchronization/immutability policy, then test state preservation. The fixture does not claim thread-safe serving from a global mutable model.

Finite-value validation is also narrower than an output guarantee. A very large finite float32 input multiplied by two can overflow even though isfinite(input) passed. The literal rows here are small and produce exact finite outputs. If a service promises finite predictions for all accepted requests, it must bound feature magnitudes appropriately or validate output finiteness and define a failure policy. Silently clipping inputs would change the represented model unless that preprocessing rule was declared and tested.

Likewise, shape validation cannot identify swapped features or changed units. The[2, -1] coefficient vector assumes one fixed ordering. A valid two-column float32 array carrying different semantics can pass every tensor check and still be the wrong request. Save names, units and preprocessing metadata with the predictor, and use known input/output cases through that complete path.

The paired TensorFlow helper accepts a float32 NumPy array and returns a copied NumPy output. Its immutable tensor operations and explicit copy have different mechanics from PyTorch inference tensors, but the application-level goals are comparable: strict input policy, one output per record, batch parity and no caller-data mutation. Compare those observed contracts rather than treating training=False and inference_mode as identical APIs.

## Exercise 1: Predict a valid batch

The question is: Use float32 CPU rows 1, 2 and 3, 4.

The output has one scalar per record. The absence of gradient tracking is part of this inference-only contract.

```python
x = torch.tensor([[1.0, 2.0], [3.0, 4.0]], dtype=torch.float32)
result = predict(x)
assert result.tolist() == [0.0, 2.0] and tuple(result.shape) == (2,) and not result.requires_grad
```

**Expected:** outputs 0, 2 with shape(2, ).

**Verify:** Compare the computed values or written argument with outputs 0, 2 with shape(2, ).

## Exercise 2: Check per-record batching parity

The question is: Predict each row alone and concatenate.

A training-mode BatchNorm layer could violate this property. The test therefore checks more than output shape.

```python
single = torch.cat([predict(x[i : i + 1]) for i in range(len(x))])
torch.testing.assert_close(single, result, atol=0, rtol=0)
```

**Expected:** same values as batch prediction.

**Verify:** Compare the computed values or written argument with same values as batch prediction.

## Exercise 3: Reject empty and oversized batches

The question is: Pass shapes 0 x2 and 5 x2.

A resource bound must be checked before computation. An empty batch also has no observations to score.

```python
for bad in [torch.empty((0, 2)), torch.zeros((5, 2))]:
    try:
        predict(bad)
    except ValueError as error:
        assert "batch" in str(error)
    else:
        raise AssertionError("invalid batch accepted")
```

**Expected:** ValueError naming batch limit.

**Verify:** Compare the computed values or written argument with ValueError naming batch limit.

## Exercise 4: Reject shape and dtype ambiguity

The question is: Pass a vector, a3-feature matrix and an int64 matrix.

Automatic reshaping or casting can hide which semantic interpretation the caller intended. A different API can permit conversion, but must document and test it.

```python
for bad, kind in [
    (torch.tensor([1.0, 2.0]), ValueError),
    (torch.zeros((2, 3)), ValueError),
    (torch.ones((1, 2), dtype=torch.int64), TypeError),
]:
    try:
        predict(bad)
    except kind:
        pass
    else:
        raise AssertionError("input contract bypassed")
```

**Expected:** shape ValueErrors and dtype TypeError.

**Verify:** Compare the computed values or written argument with shape ValueErrors and dtype TypeError.

## Exercise 5: Reject nonfinite values

The question is: Pass aN aN feature and inspect the failure.

A finite weight matrix cannot repair invalid input data. Rejecting the case preserves a clear failure category.

```python
try:
    predict(torch.tensor([[float("nan"), 1.0]]))
except ValueError as error:
    assert "finite" in str(error)
else:
    raise AssertionError("NaN accepted")
```

**Expected:** ValueError for finite-value contract.

**Verify:** Compare the computed values or written argument with ValueError for finite-value contract.

## Exercise 6: Preserve caller data

The question is: Mutate the returned output and compare the original input.

Ownership checks protect against shared views that let downstreamed its alter upstream data. They are independent of model accuracy.

```python
saved = x.clone()
output = predict(x)
output[0] = 999
assert torch.equal(x, saved)
```

**Expected:** input unchanged.

**Verify:** Compare the computed values or written argument with input unchanged.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
