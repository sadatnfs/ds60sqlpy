# torch-002: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A PyTorch tensor has values plus metadata: shape, dtype, device, strides and gradient-tracking state. Shape tells you the number of elements along each axis; strides describe how an index moves through storage. A view can share storage with another tensor, so mutation through one reference may change the other. clone creates independent storage. Transpose changes the interpretation of axes and often produces a noncontiguous view. reshape may return a view or a copy, so code should not infer ownership solely from its name.

Device and dtype are part of a computation contract. This course uses CPU explicitly, with float64 for hand-derived numerical checks and float32 for small neural modules unless stated otherwise. Broadcasting aligns trailing dimensions and can silently create pairwise results. A vector of shape (3, ) subtracted from a column (3, 1) produces (3, 3), not three paired residuals.

**Stride:** Storage offset in elements for advancing one position along an axis.

**View:** A tensor sharing underlying storage with another tensor.

**Device:** The execution and storage location such as CPU.

**Broadcasting:** Expansion of compatible trailing dimensions during an operation.

## Reading the implementation

torch.arange creates a one-dimensional tensor; reshape supplies the desired axes. stride returns element offsets rather than byte offsets. Transpose .T swaps matrix axes. view requires a compatible storage layout, while contiguous can materialize a suitable layout. clone is the explicit ownership operation. Use shape equality before paired subtraction and keep device placement visible with device='cpu'.

## Trace axes, storage and pairing separately

For a contiguous 2-by-3 tensor containing 0 through 5, the stride tuple (3, 1) means one step along the first axis moves three stored elements and one step along the second moves one. Ignoring a nonzero base storage offset, element(i, j) is located at element offset 3 i+j. In float64 each element uses eight bytes, so offset 5 corresponds to 40 bytes from that base. Strides describe storage movement in elements, not a count of rows or bytes.

Transposing gives shape (3, 2) and strides (1, 3). The value at transposed[2, 1] is the original[1, 2], still five. No rearrangement of the underlying values is required for that interpretation. A contiguous materialization may allocate a new ordering for a later operation, but the fact that a tensor is contiguous does not establish that nobody else shares its storage. The official view documentation makes that aliasing boundary explicit. [PyTorch 2.9 tensor views](https://docs.pytorch.org/docs/2.9/tensor_view.html).

The worked sequence deliberately mutates state. Example A creates x, Example B takes its first-row view and changes x[0, 0] to 99, and Example C clones the now-mutated tensor. Its correct comparison is therefore clone=-1 versus original=99. Re-running Example C alone with an unrelated x would be a different fixture. Keep the stated sequential scratch-file contract visible when reproducing the examples.

Copying storage and changing the gradient graph are different operations. clone provides independent storage but can remain connected to the source through autograd. Detach changes the differentiation boundary but can still share storage. A later inference snapshot that needs both properties may require both operations. Do not infer either property from a convenient display or from reshape, which can choose a view or a copy according to layout.

Broadcasting provides a second independent counterexample. With v=[1, 2, 3] and column=v[:, None], the right-aligned shapes are (1, 3) and (3, 1). Their difference is:

| Column value | Difference against vector 1, 2, 3 |
| --- | --- |
| 1 | [0, 1, 2] |
| 2 | [-1, 0, 1] |
| 3 | [-2, -1, 0] |

The intended paired differences are only the diagonal zeros. The broadcast operation instead creates nine comparisons whose squared mean is \(\frac{12}{9}=\frac{4}{3}\). Reducing that grid to one scalar cannot restore the lost pairing. A model can therefore optimize a nonzero objective even though every intended prediction equals its target.

A practical tensor boundary should name every axis, required dtype, device and ownership rule. A shape check catches a column/vector mismatch, but it cannot detect that two equally shaped batches have different record orders or units. Keep those semantic checks beside the tensor metadata. The framework enforces legal arithmetic; the application defines which arithmetic corresponds to the task.

## Exercise 1: Predict a 3-by-2 layout

The question is: Create a float32 CPU tensor from values 0..5 reshaped to (3, 2) and predict its stride before printing it.

A row-major (3, 2) layout moves two stored elements per row step and one per column step, so the stride is (2, 1) rather than the (3, 1) of the worked tensor.

```python
grid = torch.arange(6, dtype=torch.float32).reshape(3, 2)
assert (
    tuple(grid.shape) == (3, 2)
    and grid.stride() == (2, 1)
    and grid.dtype == torch.float32
    and grid.device.type == "cpu"
)
```

**Expected:** shape (3, 2), stride (2, 1), float32 on CPU.

**Verify:** In a fresh process, the exercise checks confirm `tuple(grid.shape) == (3, 2)`; `grid.stride() == (2, 1)`; `grid.dtype == torch.float32` and `grid.device.type == 'cpu'`.

## Exercise 2: Write through a column view

The question is: Take column 1 of the (3, 2) tensor as a view, set its last entry to -7 and inspect the original tensor and the view's stride.

Basic slicing returns a view, so the write lands in the shared storage. The view steps two elements per entry because it skips the other column.

```python
column = grid[:, 1]
column[2] = -7
assert grid[2, 1].item() == -7 and column.stride() == (2,)
```

**Expected:** grid[2, 1] becomes -7; the column view has stride (2,).

**Verify:** In a fresh process, the exercise checks confirm `grid[2, 1].item() == -7` and `column.stride() == (2,)`.

## Exercise 3: Separate contiguous from clone

The question is: Call contiguous() and clone() on the already contiguous grid, then write 100 into the [0, 0] entry of the first result and -100 into the second.

contiguous() only guarantees a layout; for an already contiguous tensor it returns the tensor itself. clone() is the operation that promises independent storage.

```python
same = grid.contiguous()
owned = grid.clone()
same[0, 0] = 100
owned[0, 0] = -100
assert (
    same.data_ptr() == grid.data_ptr() and grid[0, 0].item() == 100 and owned[0, 0].item() == -100
)
```

**Expected:** contiguous() returns the same storage, so grid[0, 0] becomes 100; the clone write leaves grid unchanged.

**Verify:** In a fresh process, the exercise checks confirm `same.data_ptr() == grid.data_ptr()`; `grid[0, 0].item() == 100` and `owned[0, 0].item() == -100`.

## Exercise 4: Trace a transposed layout

The question is: Transpose x and inspect shape, strides and contiguity.

The values can be read correctly without rearranging storage. Contiguity is a layout property, not a correctness or ownership guarantee by itself.

```python
transposed = x.T
assert (
    tuple(transposed.shape) == (3, 2)
    and transposed.stride() == (1, 3)
    and not transposed.is_contiguous()
)
assert transposed.contiguous().is_contiguous()
```

**Expected:** shape (3, 2), stride (1, 3), noncontiguous.

**Verify:** In a fresh process, the exercise checks confirm `tuple(transposed.shape) == (3, 2)`; `transposed.stride() == (1, 3)`; `not transposed.is_contiguous()` and `transposed.contiguous().is_contiguous()`.

## Exercise 5: Detect a pairing broadcast

The question is: Subtract vector [1, 2, 3] from its column representation and inspect the result.

Both shapes are legal arithmetic, but they represent different questions. Paired-record losses should validate equal target and prediction shapes.

```python
v = torch.tensor([1.0, 2.0, 3.0])
column = v[:, None]
assert tuple((v - column).shape) == (3, 3) and tuple((v - v).shape) == (3,)
```

**Expected:** shape (3, 3), while equal-vector subtraction has shape (3, ).

**Verify:** In a fresh process, the exercise checks confirm `tuple((v - column).shape) == (3, 3)` and `tuple((v - v).shape) == (3,)`.

## Exercise 6: Reject incompatible arithmetic

The question is: Add tensors shaped (2, 3) and (4, ) and capture the shape failure.

Broadcasting is constrained by dimension equality or size one. A failure here is preferable to a legal but unintended expansion that silently changes the task.

```python
try:
    torch.zeros((2, 3)) + torch.zeros(4)
except RuntimeError:
    pass
else:
    raise AssertionError("incompatible shapes accepted")
```

**Expected:** RuntimeError for incompatible trailing dimensions.

**Verify:** In a fresh process, the exercise checks confirm `torch.zeros((2, 3)) + torch.zeros(4)` raises `RuntimeError`.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
