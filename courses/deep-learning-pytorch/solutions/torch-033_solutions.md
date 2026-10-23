# torch-033: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Inference is a bounded function with an input and output contract. A model may accept many tensors that are syntactically legal but semantically wrong:missing batch axes, wrong feature order, unexpected dtype, nonfinite values oran oversized request. Validate these conditions before forward computation. Batching should preserve each record'sp re dict i on for a stateless model in the declared evaluation mode.

PyTorch inference_mode disables more autograd bookkeeping than no_grad and creates tensors with restrictions relevant to later gradient use. It is appropriate for a pure inference boundary, but should not be substituted blindly into training or gradient-based analysis. model.eval remains necessary for mode-dependent layers. This lesson uses a fixed linear model and no server, deployment or GPU so the contract can be tested locally.

**Inference mode:** A PyTorch context disabling gradient recording and additional bookkeeping.

**Input contract:** The accepted shape, dtype, device, range and budget for prediction.

**Batch independence:** Agreement of a record predicted alone or with other records.

**Owned output:** Returned storage that cannot mutate caller or model state.

## Reading the implementation

The predict helper requires a CPU float32 tensor shaped(batch, 2), with batch size 1..4 and finite entries. It calls model.eval and uses inference_mode, then returns an owned clone suitable for caller inspection. The coefficient vector[2, -1] supplies an independent output oracle. Treat shape, dtype, device and value validation as different diagnostics rather than silently coercing every input.

## Exercise 1: Predict a valid batch

The question is: Use float32 CPU rows1, 2 and3, 4.

The output has one scalar per record. The absence of gradient tracking is part of this inference-only contract.

```python
x=torch.tensor([[1.,2.],[3.,4.]],dtype=torch.float32); result=predict(x)
assert result.tolist()==[0.,2.] and tuple(result.shape)==(2,) and not result.requires_grad
```

**Expected:** outputs0, 2 with shape(2, ).

**Verify:** Compare the computed values or written argument with outputs0, 2 with shape(2, ).

## Exercise 2: Check per-record batching parity

The question is: Predict each row alone and concatenate.

A training-mode BatchNorm layer could violate this property. The test therefore checks more than output shape.

```python
single=torch.cat([predict(x[i:i+1]) for i in range(len(x))])
torch.testing.assert_close(single,result,atol=0,rtol=0)
```

**Expected:** same values as batch prediction.

**Verify:** Compare the computed values or written argument with same values as batch prediction.

## Exercise 3: Reject empty and oversized batches

The question is: Pass shapes0 x2 and5 x2.

Are source bound must be checked before computation. An empty batch also has no observations to score.

```python
for bad in [torch.empty((0,2)),torch.zeros((5,2))]:
    try: predict(bad)
    except ValueError as error: assert 'batch' in str(error)
    else: raise AssertionError('invalid batch accepted')
```

**Expected:** ValueError naming batch limit.

**Verify:** Compare the computed values or written argument with ValueError naming batch limit.

## Exercise 4: Reject shape and dtype ambiguity

The question is: Pass a vector, a3-feature matrix and an int64 matrix.

Automatic reshaping or casting can hide which semantic interpretation the caller intended. A different API can permit conversion, but must document and test it.

```python
for bad,kind in [(torch.tensor([1.,2.]),ValueError),(torch.zeros((2,3)),ValueError),(torch.ones((1,2),dtype=torch.int64),TypeError)]:
    try: predict(bad)
    except kind: pass
    else: raise AssertionError('input contract bypassed')
```

**Expected:** shape ValueErrors and dtype TypeError.

**Verify:** Compare the computed values or written argument with shape ValueErrors and dtype TypeError.

## Exercise 5: Reject nonfinite values

The question is: Pass aN aN feature and inspect the failure.

A finite weight matrix cannot repair invalid input data. Rejecting the case preserves a clear failure category.

```python
try: predict(torch.tensor([[float('nan'),1.]]))
except ValueError as error: assert 'finite' in str(error)
else: raise AssertionError('NaN accepted')
```

**Expected:** ValueError for finite-value contract.

**Verify:** Compare the computed values or written argument with ValueError for finite-value contract.

## Exercise 6: Preserve caller data

The question is: Mutate the returned output and compare the original input.

Ownership checks protect against shared views that let downstreamed its alter upstream data. They are independent of model accuracy.

```python
saved=x.clone(); output=predict(x); output[0]=999
assert torch.equal(x,saved)
```

**Expected:** input unchanged.

**Verify:** Compare the computed values or written argument with input unchanged.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
