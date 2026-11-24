# torch-032: state_dict, torch.export and inference parity

## Level and prerequisites

Advanced; approximately 135 minutes. Direct prerequisites: `torch-031`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Release a model as a state_dict and as an exported program, and verify inference parity and batch constraints in a fresh process.

Central investigation: Save a 2-to-1 Linear model with weight [2, -1] both ways, reload each in a new interpreter and test a three-row batch.

Finish condition: Both artifacts predict 0 and 2 for the two fixture rows, the static export rejects three rows while the module accepts them, the dynamic export with batch range 1..4 matches the module, and the temporary directory is removed.

The worked examples demonstrate the mechanism; exercises 1-3 transfer it to new inputs and exercises 4-6 extend it to failures and boundary cases. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A state dictionary stores named parameters and buffers, not the complete Python architecture. Reconstruct the intended module and validate its configuration before loading state. torch.export captures a constrained tensor program for inference and records input-shape assumptions. These artifacts solve different problems. A default export can specialize to the example batch size; dynamic dimensions must be declared and tested if variable batches are required.

This lesson saves a fixed two-feature linear model and an exported program, then loads both in a fresh interpreter and compares predictions. The files are owned temporary artifacts and contain no external model download. weights_only=True is used for the local state dictionary. Export load is also restricted to the artifact created by this lesson. Prediction parity does not establish optimizer restart parity, which was tested separately.

## Design decisions and when to use this method

Choose an artifact according to what the consumer must reconstruct. Use architecture plus state_dict when the consumer owns the compatible module definition. Use torch.export when a constrained tensor-program interface is the intended handoff. Neither format automatically carries the entire preprocessing, feature meaning or training-continuation contract.

Declare which dimensions may vary and verify representative and boundary inputs in the intended runtime. Keep artifact existence, deserialization, execution and numerical parity as separate observations. The current reference exercises a static two-row export and one three-row dynamic call; other declared bounds and deployment backends remain additional acceptance work.

## Paired TensorFlow comparison

Compare [tf-032](../../deep-learning-tensorflow/guides/tf-032.md) after deriving the shared numerical contract.

TensorFlow/Keras distinguishes.keras reconstruction from SavedModel inference export. PyTorch distinguishes explicit architecture+state_dict from torch.export programs and their constraints. Both need fresh-process prediction checks, and neither inference parity check proves optimizer continuation.

## Vocabulary and concepts

**state_dict:** Named tensor state requiring a compatible reconstructed architecture.

**Exported program:** A captured tensor program with declared input constraints.

**Dynamic dimension:** An input axis allowed to vary within specified bounds.

**Inference parity:** Agreement of restored and original predictions on checked inputs.

## How to run this lesson

Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **Deep Learning with PyTorch: tensors to reliable model releases** subject and select `torch-032`. Use its `llm-torch-cpu` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `courses/deep-learning-pytorch/lessons/torch-032.py` under `.learning/expansion/torch-032/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

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

## Worked example / walkthrough

### Example A: Create a known inference model

Known coefficients make a layout or persistence error visible without depending on training randomness.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
import tempfile, json, subprocess, sys, textwrap
from pathlib import Path

model = nn.Linear(2, 1, bias=False)
with torch.no_grad():
    model.weight.copy_(torch.tensor([[2.0, -1.0]]))
model.eval()
x = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
expected = model(x).detach()
assert expected.tolist() == [[0.0], [2.0]]
```

**Expected:** outputs 0, 2.

### Example B: Round-trip named state

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

### Example C: Save an exported program

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

## Prediction before your attempt

Derive Example A again with its **Expected** line covered: Create a known inference model. Predict exercise 6, Declare a bounded dynamic batch and clean up, from its prompt alone: Export with batch Dim range 1..4, test three rows, and remove owned files. Then explain why this finish condition holds: Both artifacts predict 0 and 2 for the two fixture rows, the static export rejects three rows while the module accepts them, the dynamic export with batch range 1..4 matches the module, and the temporary directory is removed. Keep each prediction beside the observed value.

## Exercises

1. **Predict a new inference output.** Set a bias-free 2-to-1 Linear weight to [1, 3] and predict the rows [1, 2] and [3, 4].
   **Expected:** outputs [[7], [15]].
   **Verify:** In a fresh process, the exercise checks confirm `other_model(rows).tolist() == [[7.0], [15.0]]`.

2. **Load state into matching and mismatched modules.** Load the model's state_dict into a fresh bias-free Linear(2, 1) and into a Linear(2, 1) that has a bias.
   **Expected:** the matching module reproduces the outputs; the module with a bias raises RuntimeError for the missing key.
   **Verify:** In a fresh process, the exercise checks confirm `copy_model(rows)` matches `other_model(rows)` exactly and `nn.Linear(2, 1).load_state_dict(other_model.state_dict())` raises `RuntimeError`.

3. **Export the new model in memory.** Export the new model for the two-row input and compare the exported module's predictions.
   **Expected:** exported predictions match [[7], [15]] within 1e-6.
   **Verify:** In a fresh process, the exercise checks confirm `exported_other(rows)` matches `other_model(rows)` within 1e-06.

4. **Check both artifacts in a fresh process.** Load the state and exported program in a new interpreter and compare outputs.
   **Expected:** both child predictions 0, 2.
   **Verify:** In a fresh process, the exercise checks confirm `not (result.returncode)`, `a` matches `expected.numpy()` within 1e-06 and `b` matches `expected.numpy()` within 1e-06.

5. **Expose static batch specialization.** Pass three rows to the statically exported module and compare with ordinary Linear.
   **Expected:** ordinary Linear accepts 3; static export rejects its batch constraint.
   **Verify:** In a fresh process, the exercise checks confirm `tuple(restored(three).shape) == (3, 1)`; `exported_module(three)` raises `AssertionError` and the raised error satisfies `'Guard failed: input.size()[0] == 2' in str(error)`.

6. **Declare a bounded dynamic batch and clean up.** Export with batch Dim range 1..4, test three rows, and remove owned files.
   **Expected:** three-row parity passes; temporary directory absent.
   **Verify:** In a fresh process, the exercise checks confirm `dynamic(three)` matches `restored(three)` within 1e-06 and `not folder.exists()`.

## Common pitfalls and diagnosis

If state loading fails, compare the intended constructor, keys and tensor shapes before using permissive loading. If loading succeeds but values differ, check feature order, normalization, dtype and evaluation mode. If only a new batch length fails, inspect static versus declared dynamic export constraints rather than changing the model's feature width.

If a fresh-process check fails, read the child's actual stderr and confirm it loaded the created artifact rather than another path. Do not infer boundary behavior at 1, 4 or 5 from the single three-row dynamic example. If inference matches but resumed training diverges, return to optimizer/RNG/data-state restoration; prediction parity is not the corresponding test.

## Progressive hints

Hint 1: Example B (Round-trip named state) alters one assumption of Example A (Create a known inference model). Hint 2: exercise 4, Check both artifacts in a fresh process, should end at both child predictions 0, 2. Work backward from it. Hint 3: exercise 5, Expose static batch specialization, changes one input; predict which value moves first.

## Self-check and retrieval

Close the worked examples and rebuild Example C, Save an exported program, from its inputs alone. Predict whether exercise 3, Export the new model in memory, survives one changed input. Then explain state_dict, Exported program, Dynamic dimension in terms of that fixture; say which claims the code guarantees and which need new observations.

## Next step

If Example A (Create a known inference model) cannot be rebuilt without help, revisit `torch-031` first. Otherwise keep your exercise 2 attempt, Load state into matching and mismatched modules, as a regression case alongside a fresh transfer input, then continue along the course plan.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 export](https://docs.pytorch.org/docs/2.9/export.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

## Interview reasoning with worked answers

**Does state_dict include the architecture?**

No. It stores named state. The caller must reconstruct a compatible architecture and preserve the semantic schema used by that state.

**Why can an exported model reject a batch size that Linear accepts?**

The export may specialize to the example input. Declare and validate dynamic dimensions when that flexibility is required.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-032, state_dict, torch.export and inference parity.
Read courses/deep-learning-pytorch/guides/torch-032.md and courses/deep-learning-pytorch/lessons/torch-032.py. Direct prerequisites: `torch-031`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
