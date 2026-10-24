# torch-032: state_dict, torch.export and inference parity

## Level and prerequisites

Advanced; approximately 135 minutes. Direct prerequisites: `torch-031`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A state dictionary stores named parameters and buffers, not the complete Python architecture. The central investigation is concrete: Set a 2-to-1 bias-free Linear weight to[2, -1] and predict rows 1, 2 and 3, 4. The finish condition is outputs 0, 2. three-row parity passes; temporary directory absent. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

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

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-032/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-032.py`. For macOS/Linux, use the interpreter explicitly selected for a separately prepared native PyTorch environment, and invoke that interpreter on `courses/deep-learning-pytorch/lessons/torch-032.py` from the repository root. The repository's general `.venv` is not assumed to contain PyTorch; the prepared classroom profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

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

## Worked example / walkthrough

### Example A: Create a known inference model

Known coefficients make a layout or persistence error visible without depending on training randomness.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
import tempfile,json,subprocess,sys,textwrap
from pathlib import Path

model=nn.Linear(2,1,bias=False)
with torch.no_grad(): model.weight.copy_(torch.tensor([[2.,-1.]]))
model.eval(); x=torch.tensor([[1.,2.],[3.,4.]]); expected=model(x).detach()
assert expected.tolist()==[[0.],[2.]]
```

**Expected:** outputs 0, 2.

### Example B: Round-trip named state

The architecture is reconstructed explicitly. A compatible set of names and shapes is necessary, but the application should also retain semantic feature order and dtype metadata.

```python
temporary=tempfile.TemporaryDirectory(); folder=Path(temporary.name); state_path=folder/'weights.pt'; torch.save(model.state_dict(),state_path)
restored=nn.Linear(2,1,bias=False); restored.load_state_dict(torch.load(state_path,map_location='cpu',weights_only=True)); restored.eval()
torch.testing.assert_close(restored(x),expected,atol=1e-6,rtol=0)
```

**Expected:** restored predictions match within 1e-6.

### Example C: Save an exported program

The program includes shape constraints from the example. A readable archive alone would not prove that those constraints or operations execute correctly.

```python
program=torch.export.export(model,(x,),strict=True); export_path=folder/'model.pt2'; torch.export.save(program,export_path)
loaded_program=torch.export.load(export_path); exported_module=loaded_program.module()
torch.testing.assert_close(exported_module(x),expected,atol=1e-6,rtol=0)
```

**Expected:** exported predictions match within 1e-6.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: outputs 0, 2. three-row parity passes; temporary directory absent. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Create a known inference model.** Set a 2-to-1 bias-free Linear weight to[2, -1] and predict rows 1, 2 and 3, 4.
   **Expected:** outputs 0, 2.
   **Verify:** Save the assertion results for exercise 1, including outputs 0, 2.

2. **Round-trip named state.** Save state_dict to an owned temporary file, reconstruct the architecture and load weights_only.
   **Expected:** restored predictions match within 1e-6.
   **Verify:** Save the assertion results for exercise 2, including restored predictions match within 1e-6.

3. **Save an exported program.** Export the fixed batch program, save it, and load its module.
   **Expected:** exported predictions match within 1e-6.
   **Verify:** Save the assertion results for exercise 3, including exported predictions match within 1e-6.

4. **Check both artifacts in a fresh process.** Load the state and exported program in a new interpreter and compare outputs.
   **Expected:** both child predictions 0, 2.
   **Verify:** Save the assertion results for exercise 4, including both child predictions 0, 2.

5. **Expose static batch specialization.** Pass three rows to the statically exported module and compare with ordinary Linear.
   **Expected:** ordinary Linear accepts 3; static export rejects its batch constraint.
   **Verify:** Save the assertion results for exercise 5, including ordinary Linear accepts 3; static export rejects its batch constraint.

6. **Declare a bounded dynamic batch and clean up.** Export with batch Dim range 1..4, test three rows, and remove owned files.
   **Expected:** three-row parity passes; temporary directory absent.
   **Verify:** Save the assertion results for exercise 6, including three-row parity passes; temporary directory absent.

## Common pitfalls and diagnosis

If state loading fails, compare the intended constructor, keys and tensor shapes before using permissive loading. If loading succeeds but values differ, check feature order, normalization, dtype and evaluation mode. If only a new batch length fails, inspect static versus declared dynamic export constraints rather than changing the model's feature width.

If a fresh-process check fails, read the child's actual stderr and confirm it loaded the created artifact rather than another path. Do not infer boundary behavior at 1, 4 or 5 from the single three-row dynamic example. If inference matches but resumed training diverges, return to optimizer/RNG/data-state restoration; prediction parity is not the corresponding test.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain state_dict, Exported program, Dynamic dimension using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-031` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 export](https://docs.pytorch.org/docs/2.9/export.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

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
