# torch-032: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A state dictionary stores named parameters and buffers, not the complete Python architecture. Reconstruct the intended module and validate its configuration before loading state. torch.export captures a constrained tensor program for inference and records input-shape assumptions. These artifacts solve different problems. A default export can specialize to the example batch size; dynamic dimensions must be declared and tested if variable batches are required.

This lesson saves a fixed two-feature linear model and an exported program, then loads both in a fresh interpreter and compares predictions. The files are owned temporary artifacts and contain no external model download. weights_only=True is used for the local state dictionary. Export load is also restricted to the artifact created by this lesson. Prediction parity does not establish optimizer restart parity, which was tested separately.

**state_dict:** Named tensor state requiring a compatible reconstructed architecture.

**Exported program:** A captured tensor program with declared input constraints.

**Dynamic dimension:** An input axis allowed to vary within specified bounds.

**Inference parity:** Agreement of restored and original predictions on checked inputs.

## Reading the implementation

Save model.state_dict with torch.save and load into an nn.Linear(2, 1, bias=False). torch.export.export(model, (example, ), strict=True) captures a static program; torch.export.save/load persists it. Call loaded_program.module() to obtain the checked inference module. For variable batch length, declareDim('batch', \(\mathrm{min}=1\), \(\mathrm{max}=4\)) through dynamic_shapes and test within and outside the bound. Keep loaded owners in named variables while using their derived objects.

## Compare tensor state with a constrained program

The fixed Linear layer has two input features, one output and no bias. Its stored weight is[2, -1], so row[1, 2] maps to zero and row[3, 4] maps to two. The output shape is(B, 1). This explicit affine rule is the independent persistence oracle: the restored result should match the known function, not merely another object that happens to share the original weights.

state_dict records named parameters and persistent buffers. Loading it into a new nn.Linear(2, 1, bias=False) checks compatibility with that reconstructed architecture. It does not serialize the Python class definition, feature names, normalization policy or arbitrary nonregistered state. Strict loading can detect missing/unexpected keys and incompatible tensor shapes, but equal shapes do not establish semantic equivalence. Reversing the two feature meanings changes[1, 2]'s prediction from zero to three while preserving every dimension.

torch.export captures a tensor program with assumptions derived from the example and declared dynamic shapes. In the static example, the batch dimension is specialized to two. The ordinary reconstructed Linear can evaluate a three-row batch, because its parameters constrain feature width rather than batch size. The static exported module rejects that same batch under its captured guard. That rejection is expected interface enforcement, not evidence that the affine calculation itself requires exactly two observations. [PyTorch 2.9 export](https://docs.pytorch.org/docs/2.9/export.html).

The dynamic export names a batch dimension with declared range 1..4 while keeping feature width two. A three-row call is compared with the ordinary module in the reference. That establishes one in-range dynamic case. The current executable does not separately test batch sizes one, four or an out-of-range five against the dynamic artifact, so those should not be claimed as observed results merely because the range appears in source. Export constraints are useful, but acceptance still needs the actual intended boundary cases when that interface is relied on.

A dynamic dimension does not mean arbitrary rank, dtype, feature width or arbitrary Python control. Shape constraints describe a family of tensor programs that the export process could justify. If later code needs a new branch or input structure, it may require a new export and qualification. A successful strict export is also not a promise that every target runtime or lowering backend can execute the resulting operators.

The fresh interpreter is an important independence boundary. It creates a new Linear, loads the saved tensors, and separately loads the exported program from the file path. It cannot accidentally satisfy the test by reusing the parent's in-memory model. Keeping loaded artifact owners and their derived modules in named variables makes the lifecycle inspectable. The child has a bounded timeout and exposes stderr on failure, so a failed load or guard is not converted into a success transcript.

The two saved forms have different reconstruction semantics from Keras .keras and SavedModel inference export. The paired TensorFlow example also uses a different one-feature affine fixture. Compare the artifact responsibilities and each independent local oracle rather than expecting identical filenames, load APIs or literal predictions across frameworks.

Prediction parity and training continuation remain separate. Matching[0, 2] says nothing about Adam moments, RNG position, data iteration or scheduler state. Conversely, a training checkpoint may contain state irrelevant to a minimal inference consumer. The previous checkpoint chapter tests the next update; this chapter tests a fixed prediction interface. Preserve that distinction in filenames, metadata and review claims.

Only the locally created trusted artifacts are loaded. weights_only=True constrains the state-dictionary load path but does not authenticate a publisher or prove that an arbitrary file has acceptable resource demands. The exported program has its own versioned loader/runtime contract. An archive suffix or a successful save call is not proof of compatibility with another framework, architecture or deployment format.

The handoff should retain artifact identity, constructor/program version, feature order and units, dtype/device, mode, shape constraints, preprocessing and output interpretation. Test the full predictor with known inputs in the consumer environment. A graph that reproduces one matrix multiplication can still sit behind a mismatched normalizer or class-label mapping, and those application errors will not be repaired by re-exporting the same weights.

## Exercise 1: Create a known inference model

The question is: Set a 2-to-1 bias-free Linear weight to[2, -1] and predict rows 1, 2 and 3, 4.

Known coefficients make a layout or persistence error visible without depending on training randomness.

```python
model = nn.Linear(2, 1, bias=False)
with torch.no_grad():
    model.weight.copy_(torch.tensor([[2.0, -1.0]]))
model.eval()
x = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
expected = model(x).detach()
assert expected.tolist() == [[0.0], [2.0]]
```

**Expected:** outputs 0, 2.

**Verify:** Compare the computed values or written argument with outputs 0, 2.

## Exercise 2: Round-trip named state

The question is: Save state_dict to an owned temporary file, reconstruct the architecture and load weights_only.

The architecture is reconstructed explicitly. A compatible set of names and shapes is necessary, but the application should also retain semantic feature order and dtype metadata.

```python
temporary = tempfile.TemporaryDirectory()
folder = Path(temporary.name)
state_path = folder / "weights.pt"
torch.save(model.state_dict(), state_path)
restored = nn.Linear(2, 1, bias=False)
restored.load_state_dict(torch.load(state_path, map_location="cpu", weights_only=True))
restored.eval()
torch.testing.assert_close(restored(x), expected, atol=1e-6, rtol=0)
```

**Expected:** restored predictions match within 1e-6.

**Verify:** Compare the computed values or written argument with restored predictions match within 1e-6.

## Exercise 3: Save an exported program

The question is: Export the fixed batch program, save it, and load its module.

The program includes shape constraints from the example. A readable archive alone would not prove that those constraints or operations execute correctly.

```python
program = torch.export.export(model, (x,), strict=True)
export_path = folder / "model.pt2"
torch.export.save(program, export_path)
loaded_program = torch.export.load(export_path)
exported_module = loaded_program.module()
torch.testing.assert_close(exported_module(x), expected, atol=1e-6, rtol=0)
```

**Expected:** exported predictions match within 1e-6.

**Verify:** Compare the computed values or written argument with exported predictions match within 1e-6.

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

**Verify:** Compare the computed values or written argument with both child predictions 0, 2.

## Exercise 5: Expose static batch specialization

The question is: Pass three rows to the statically exported module and compare with ordinary Linear.

Mathematical batch flexibility does not automatically make an export contract dynamic. The pinned PyTorch 2.9.1 profile raises AssertionError with the exact guard input.size()[0] == 2 for this invalid batch. The handler recognizes that shape guard and re-raises unrelated assertions. Exception types can differ across framework versions, so the diagnostic is tied to the prepared profile.

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

**Verify:** Compare the computed values or written argument with ordinary Linear accepts 3; static export rejects its batch constraint.

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

**Verify:** Compare the computed values or written argument with three-row parity passes; temporary directory absent.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
