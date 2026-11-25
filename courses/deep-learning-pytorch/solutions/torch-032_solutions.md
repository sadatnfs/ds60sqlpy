# torch-032: explanatory solutions

Open these answers only after attempting state_dict, torch.export and inference parity yourself. They reuse the guide's literal inputs, starting from Example A, Create a known inference model, so a discrepancy points at one step. The executable companion runs the assertions; this page explains why each one tests state_dict, Exported program, Dynamic dimension. After a pass, choose a new input for exercise 6, Declare a bounded dynamic batch and clean up, without looking.

After comparing, follow the [review steps](../STUDY-GUIDE.md#after-the-solutions).

## Mechanism review

A state dictionary stores named parameters and buffers, not the complete Python architecture. Reconstruct the intended module and validate its configuration before loading state. torch.export captures a constrained tensor program for inference and records input-shape assumptions. These artifacts solve different problems. A default export can specialize to the example batch size; dynamic dimensions must be declared and tested if variable batches are required.

This lesson saves a fixed two-feature linear model and an exported program, then loads both in a fresh interpreter and compares predictions. The files are owned temporary artifacts and contain no external model download. weights_only=True is used for the local state dictionary. Export load is also restricted to the artifact created by this lesson. Prediction parity does not establish optimizer restart parity, which was tested separately.

**state_dict:** Named tensor state requiring a compatible reconstructed architecture.

**Exported program:** A captured tensor program with declared input constraints.

**Dynamic dimension:** An input axis allowed to vary within specified bounds.

**Inference parity:** Agreement of restored and original predictions on checked inputs.

## Reading the implementation

Save model.state_dict with torch.save and load into an nn.Linear(2, 1, bias=False). torch.export.export(model, (example, ), strict=True) captures a static program; torch.export.save/load persists it. Call loaded_program.module() to obtain the checked inference module. For variable batch length, declare Dim('batch', \(\mathrm{min}=1\), \(\mathrm{max}=4\)) through dynamic_shapes and test within and outside the bound. Keep loaded owners in named variables while using their derived objects.

## Compare tensor state with a constrained program

The fixed Linear layer has two input features, one output and no bias. Its stored weight is [2, -1], so row [1, 2] maps to zero and row [3, 4] maps to two. The output shape is (B, 1). This explicit affine rule is the independent persistence oracle: the restored result should match the known function, not merely another object that happens to share the original weights.

state_dict records named parameters and persistent buffers. Loading it into a new nn.Linear(2, 1, bias=False) checks compatibility with that reconstructed architecture. It does not serialize the Python class definition, feature names, normalization policy or arbitrary nonregistered state. Strict loading can detect missing/unexpected keys and incompatible tensor shapes, but equal shapes do not establish semantic equivalence. Reversing the two feature meanings changes [1, 2]'s prediction from zero to three while preserving every dimension.

torch.export captures a tensor program with assumptions derived from the example and declared dynamic shapes. In the static example, the batch dimension is specialized to two. The ordinary reconstructed Linear can evaluate a three-row batch, because its parameters constrain feature width rather than batch size. The static exported module rejects that same batch under its captured guard. That rejection is expected interface enforcement, not evidence that the affine calculation itself requires exactly two observations. [PyTorch 2.9 export](https://docs.pytorch.org/docs/2.9/export.html).

The dynamic export names a batch dimension with declared range 1..4 while keeping feature width two. A three-row call is compared with the ordinary module in the reference. That establishes one in-range dynamic case. The current executable does not separately test batch sizes one, four or an out-of-range five against the dynamic artifact, so those should not be claimed as observed results merely because the range appears in source. Export constraints are useful, but acceptance still needs the actual intended boundary cases when that interface is relied on.

A dynamic dimension does not mean arbitrary rank, dtype, feature width or arbitrary Python control. Shape constraints describe a family of tensor programs that the export process could justify. If later code needs a new branch or input structure, it may require a new export and qualification. A successful strict export is also not a promise that every target runtime or lowering backend can execute the resulting operators.

The fresh interpreter is an important independence boundary. It creates a new Linear, loads the saved tensors, and separately loads the exported program from the file path. It cannot accidentally satisfy the test by reusing the parent's in-memory model. Keeping loaded artifact owners and their derived modules in named variables makes the lifecycle inspectable. The child has a bounded timeout and exposes stderr on failure, so a failed load or guard is not converted into a success transcript.

The two saved forms have different reconstruction semantics from Keras .keras and SavedModel inference export. The paired TensorFlow example also uses a different one-feature affine fixture. Compare the artifact responsibilities and each independent local oracle rather than expecting identical filenames, load APIs or literal predictions across frameworks.

Prediction parity and training continuation remain separate. Matching [0, 2] says nothing about Adam moments, RNG position, data iteration or scheduler state. Conversely, a training checkpoint may contain state irrelevant to a minimal inference consumer. The previous checkpoint chapter tests the next update; this chapter tests a fixed prediction interface. Preserve that distinction in filenames, metadata and review claims.

Only the locally created trusted artifacts are loaded. weights_only=True constrains the state-dictionary load path but does not authenticate a publisher or prove that an arbitrary file has acceptable resource demands. The exported program has its own versioned loader/runtime contract. An archive suffix or a successful save call is not proof of compatibility with another framework, architecture or deployment format.

The handoff should retain artifact identity, constructor/program version, feature order and units, dtype/device, mode, shape constraints, preprocessing and output interpretation. Test the full predictor with known inputs in the consumer environment. A graph that reproduces one matrix multiplication can still sit behind a mismatched normalizer or class-label mapping, and those application errors will not be repaired by re-exporting the same weights.

## Exercise 1: Predict a new inference output

The question is: Set a bias-free 2-to-1 Linear weight to [1, 3] and predict the rows [1, 2] and [3, 4].

Each prediction is 1*first+3*second.

```python
other_model = nn.Linear(2, 1, bias=False)
with torch.no_grad():
    other_model.weight.copy_(torch.tensor([[1.0, 3.0]]))
other_model.eval()
rows = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
assert other_model(rows).tolist() == [[7.0], [15.0]]
```

**Expected:** outputs [[7], [15]].

**Verify:** In a fresh process, the exercise checks confirm `other_model(rows).tolist() == [[7.0], [15.0]]`.

## Exercise 2: Load state into matching and mismatched modules

The question is: Load the model's state_dict into a fresh bias-free Linear(2, 1) and into a Linear(2, 1) that has a bias.

A state_dict holds named tensors, not the architecture; strict loading checks that the names match.

```python
copy_model = nn.Linear(2, 1, bias=False)
copy_model.load_state_dict(other_model.state_dict())
torch.testing.assert_close(copy_model(rows), other_model(rows), atol=0, rtol=0)
try:
    nn.Linear(2, 1).load_state_dict(other_model.state_dict())
except RuntimeError:
    pass
else:
    raise AssertionError("missing bias accepted")
```

**Expected:** the matching module reproduces the outputs; the module with a bias raises RuntimeError for the missing key.

**Verify:** In a fresh process, the exercise checks confirm `copy_model(rows)` matches `other_model(rows)` exactly and `nn.Linear(2, 1).load_state_dict(other_model.state_dict())` raises `RuntimeError`.

## Exercise 3: Export the new model in memory

The question is: Export the new model for the two-row input and compare the exported module's predictions.

The exported program records the computation for the example shape; this check runs without writing files.

```python
exported_other = torch.export.export(other_model, (rows,), strict=True).module()
torch.testing.assert_close(exported_other(rows), other_model(rows), atol=1e-6, rtol=0)
```

**Expected:** exported predictions match [[7], [15]] within 1e-6.

**Verify:** In a fresh process, the exercise checks confirm `exported_other(rows)` matches `other_model(rows)` within 1e-06.

## Exercise 4: Check both artifacts in a fresh process

The question is: Load the state and exported program in a new interpreter and compare outputs.

The child cannot reuse parent objects. It must reconstruct each artifact'sstate and execution interface from disk.

```python
child = textwrap.dedent("""
import json,sys,torch
from torch import nn
x=torch.tensor([[1.,2.],[3.,4.]])
model=nn.Linear(2,1,bias=False); model.load_state_dict(torch.load(sys.argv[1],map_location='cpu',weights_only=True)); model.eval()
owner=torch.export.load(sys.argv[2]); exported=owner.module()
with torch.no_grad(): result=[model(x).tolist(),exported(x).tolist()]
print(json.dumps(result))
""")
compile(child, "torch-export-child", "exec")
result = subprocess.run(
    [sys.executable, "-c", child, str(state_path), str(export_path)],
    capture_output=True,
    text=True,
    timeout=60,
    check=False,
)
if result.returncode:
    raise RuntimeError("export child failed: " + result.stderr)
a, b = json.loads(result.stdout.strip().splitlines()[-1])
np.testing.assert_allclose(a, expected.numpy(), atol=1e-6, rtol=0)
np.testing.assert_allclose(b, expected.numpy(), atol=1e-6, rtol=0)
```

**Expected:** both child predictions 0, 2.

**Verify:** In a fresh process, the exercise checks confirm `not (result.returncode)`, `a` matches `expected.numpy()` within 1e-06 and `b` matches `expected.numpy()` within 1e-06.

## Exercise 5: Expose static batch specialization

The question is: Pass three rows to the statically exported module and compare with ordinary Linear.

Mathematical batch flexibility does not automatically make an export contract dynamic. The pinned PyTorch 2.15.0 CPU profile raises AssertionError with the exact guard input.size()[0] == 2 for this invalid batch. The handler recognizes that shape guard and re-raises unrelated assertions. Exception types can differ across framework versions, so the diagnostic is tied to the prepared profile.

```python
three = torch.tensor([[0.0, 0.0], [1.0, 2.0], [3.0, 4.0]])
assert tuple(restored(three).shape) == (3, 1)
try:
    exported_module(three)
except AssertionError as error:
    if "Guard failed: input.size()[0] == 2" not in str(error):
        raise
else:
    raise AssertionError("static export constraint not enforced")
```

**Expected:** ordinary Linear accepts 3; static export rejects its batch constraint.

**Verify:** In a fresh process, the exercise checks confirm `tuple(restored(three).shape) == (3, 1)`; `exported_module(three)` raises `AssertionError` and the raised error satisfies `'Guard failed: input.size()[0] == 2' in str(error)`.

## Exercise 6: Declare a bounded dynamic batch and clean up

The question is: Export with batch Dim range 1..4, test three rows, and remove owned files.

Dynamic dimensions describe allowed variation, not arbitrary inputs. Feature width, dtype and finite-value policy still need their own contracts.

```python
batch = torch.export.Dim("batch", min=1, max=4)
dynamic = torch.export.export(model, (x,), dynamic_shapes=({0: batch},), strict=True).module()
torch.testing.assert_close(dynamic(three), restored(three), atol=1e-6, rtol=0)
temporary.cleanup()
assert not folder.exists()
```

**Expected:** three-row parity passes; temporary directory absent.

**Verify:** In a fresh process, the exercise checks confirm `dynamic(three)` matches `restored(three)` within 1e-06 and `not folder.exists()`.

