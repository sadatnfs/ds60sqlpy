# torch-002: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A PyTorch tensor has values plus metadata:shape, dtype, device, strides and gradient-tracking state. Shape tells you the number of elements along each axis; strides describe how an index moves through storage. A view can share storage with another tensor, so mutation through one reference may change the other. clone creates independent storage. Transpose changes the interpretation of axes and often produces a noncontiguous view. reshape may return a view or a copy, so code should not infer ownership solely from its name.

Device and dtype are part of a computation contract. This course uses CPU explicitly, with float64 for hand-derived numerical checks and float32 for small neural modules unless stated otherwise. Broadcasting aligns trailing dimensions and can silently create pairwise results. A vector of shape(3, ) subtracted from a column(3, 1) produces(3, 3), not three paired residuals.

**Stride:** Storage offset in elements for advancing one position along an axis.

**View:** A tensor sharing underlying storage with another tensor.

**Device:** The execution and storage location such as CPU.

**Broadcasting:** Expansion of compatible trailing dimensions during an operation.

## Reading the implementation

torch.arange creates a one-dimensional tensor; reshape supplies the desired axes. stride returns element offsets rather than byte offsets. Transpose .T swaps matrix axes. view requires a compatible storage layout, while contiguous can materialize a suitable layout. clone is the explicit ownership operation. Use shape equality before paired subtraction and keep device placement visible with device='cpu'.

## Exercise 1: Inspect shape and stride

The question is: Create a2x3 float64CPU tensor from values0..5.

The last axis advances by one stored element and the first by three. These metadata explain the matrix layout without relying on a printed table alone.

```python
x=torch.arange(6,dtype=torch.float64,device='cpu').reshape(2,3)
assert tuple(x.shape)==(2,3) and x.stride()==(3,1) and x.device.type=='cpu' and x.dtype==torch.float64
```

**Expected:** shape(2, 3), stride(3, 1), CPU, float64.

**Verify:** Compare the computed values or written argument with shape(2, 3), stride(3, 1), CPU, float64.

## Exercise 2: Expose shared storage

The question is: Slice the first row, change its first value, and inspect the original tensor.

Basic slicing returns a view here. A function receiving that view can mutate caller-owned data unless it copies or documents the ownership contract.

```python
row=x[0]; row[0]=99
assert x[0,0].item()==99
```

**Expected:** original x[0, 0] becomes99.

**Verify:** Compare the computed values or written argument with original x[0, 0] becomes99.

## Exercise 3: Create an independent copy

The question is: Clone the tensor, change the clone and compare the original.

clone copies storage and preserves a differentiable relationship when gradients are enabled. Detach in g and copying are separate operations discussed later.

```python
owned=x.clone(); owned[0,0]=-1
assert owned[0,0].item()==-1 and x[0,0].item()==99
```

**Expected:** clone starts-1; original remains99.

**Verify:** Compare the computed values or written argument with clone starts-1; original remains99.

## Exercise 4: Trace a transposed layout

The question is: Transpose x and inspect shape, strides and contiguity.

The values can be read correctly without rearranging storage. Contiguity is a layout property, not a correctness or ownership guarantee by itself.

```python
transposed=x.T
assert tuple(transposed.shape)==(3,2) and transposed.stride()==(1,3) and not transposed.is_contiguous()
assert transposed.contiguous().is_contiguous()
```

**Expected:** shape(3, 2), stride(1, 3), noncontiguous.

**Verify:** Compare the computed values or written argument with shape(3, 2), stride(1, 3), noncontiguous.

## Exercise 5: Detect a pairing broadcast

The question is: Subtract vector[1, 2, 3] from its column representation and inspect the result.

Both shapes are legal arithmetic, but they represent different questions. Paired-record losses should validate equal target and prediction shapes.

```python
v=torch.tensor([1.,2.,3.]); column=v[:,None]
assert tuple((v-column).shape)==(3,3) and tuple((v-v).shape)==(3,)
```

**Expected:** shape(3, 3), while equal-vector subtraction has shape(3, ).

**Verify:** Compare the computed values or written argument with shape(3, 3), while equal-vector subtraction has shape(3, ).

## Exercise 6: Reject incompatible arithmetic

The question is: Add tensors shaped(2, 3) and(4, ) and capture the shape failure.

Broadcasting is constrained by dimension equality or size one. A failure here is preferable to a legal but unintended expansion that silently changes the task.

```python
try: torch.zeros((2,3))+torch.zeros(4)
except RuntimeError: pass
else: raise AssertionError('incompatible shapes accepted')
```

**Expected:** RuntimeError for incompatible trailing dimensions.

**Verify:** Compare the computed values or written argument with RuntimeError for incompatible trailing dimensions.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
