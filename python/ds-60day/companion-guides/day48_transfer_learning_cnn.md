# Day 48 — Transfer Learning with CNNs

**Lesson ID:** `python-48` · **Level:** advanced · **Dependencies:** `deep-learning` · **Network:** optional model download

Transfer learning reuses features from a model trained on another dataset. This
lesson practices a two-stage workflow: train a new classifier head, then
optionally fine-tune part of the backbone with a lower learning rate.

## Learning objectives

By the end of the lesson, you can:

- prepare an `ImageFolder` directory and matching data transforms;
- load ResNet-18 with cached pretrained weights or an explicit offline fallback;
- freeze and verify backbone parameters;
- replace and train the classification head; and
- unfreeze the final block cautiously for fine-tuning.

## Prerequisites

- Complete `python-47` (PyTorch training loops).
- Understand class logits, DataLoaders, train/evaluation mode, and checkpoints.
- Have a small local image dataset organized by class.

## Network and resource contract

`models.ResNet18_Weights.DEFAULT` downloads pretrained weights on first use
unless they are already in the PyTorch cache. During a connected bootstrap, run
the model-loading cell once and keep the cache. Later runs are offline.

If weights are not cached and the machine is offline, use
`models.resnet18(weights=None)` to practice the mechanics. That fallback is
training from scratch, not transfer learning, so label results accordingly.
CPU and a small image subset are the default; a GPU is optional.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Convolutional neural network | Network using learned spatial filters |
| Backbone | Feature-extracting layers before the task-specific head |
| Pretrained weights | Parameters learned from an earlier dataset |
| Freeze | Set `requires_grad=False` so optimizer updates do not change parameters |
| Fine-tune | Continue training some pretrained layers on the new task |
| Data augmentation | Label-preserving random input transformations |
| Catastrophic forgetting | Useful pretrained features damaged by overly aggressive updates |

## Worked example: replace the head and verify trainable state

```python
import torch
from torchvision import models

# DEFAULT requires a one-time download unless already cached.
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
for parameter in model.parameters():
    parameter.requires_grad = False

model.fc = torch.nn.Linear(model.fc.in_features, 2)
trainable = [name for name, p in model.named_parameters() if p.requires_grad]
print(trainable)
```

Only the new `fc.weight` and `fc.bias` should be trainable initially. Build the
optimizer from trainable parameters so the intended phase is explicit.

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 48 learner notebook from this guide's **Next
   step** section in VS Code or JupyterLab.
2. Select the `Python (ds60sqlpy)` kernel. Start at the top and use
   **Run All** only after making the written predictions; every added
   worked example is bounded and offline after bootstrap.
3. Keep experiments in new scratch cells. Do not edit the official
   solution while attempting the numbered practice.
4. Restart the kernel and run from the first cell before calling the
   lesson complete. A clean run catches hidden state and stale
   variables.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab
```

macOS/Linux:

```bash
.venv/bin/python -m jupyter lab
```

If the Windows environment uses the documented conda-prefix fallback,
use `.\.venv\python.exe` in place of
`.\.venv\Scripts\python.exe`.

## Concept deep dive — offline-safe transfer learning, frozen parameters, and cautious fine-tuning

### The mental model

Transfer learning reuses a **backbone** that learned general image
features and replaces its task-specific head. Freezing sets
`requires_grad=False`; it does not automatically switch batch
normalization or dropout into evaluation behavior. The optimizer should
receive only parameters intended to change.

Pretrained weights are an external artifact with provenance, license,
preprocessing, and cache requirements. The default lesson must make a
connected first-use download explicit and provide a `weights=None`
architecture-only fallback so offline execution never surprises the
learner.

### Worked examples and syntax anatomy

- **`models.resnet18(weights=...)`:** constructs the architecture and optionally loads a specific versioned weight bundle.
- **`parameter.requires_grad = False`:** excludes a parameter from autograd updates but does not change module mode.
- **`model.fc = nn.Linear(model.fc.in_features, classes)`:** replaces the classifier head while preserving the backbone feature width.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — build and verify a no-download frozen backbone

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
import torch
from torchvision import models

model = models.resnet18(weights=None)  # explicit offline architecture
for parameter in model.parameters():
    parameter.requires_grad = False
model.fc = torch.nn.Linear(model.fc.in_features, 3)

trainable = [name for name, p in model.named_parameters() if p.requires_grad]
print(trainable)
assert trainable == ["fc.weight", "fc.bias"]
```

**Expected observation:** Only the newly assigned head parameters are trainable; no pretrained asset was downloaded.

**Assumption to name:** Random backbone features are a mechanics fallback, not equivalent to pretrained transfer performance.

### Focused example B — apply the matching tensor normalization contract

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
import torch
from torchvision.transforms import Normalize

image = torch.full((3, 4, 4), 0.5)
normalize = Normalize(
    mean=[0.485, 0.456, 0.406],
    std=[0.229, 0.224, 0.225],
)
transformed = normalize(image)
print({"shape": tuple(transformed.shape),
       "channel_means": transformed.mean(dim=(1, 2)).tolist()})
assert transformed.shape == image.shape
```

**Expected observation:** Normalization preserves channel/height/width shape while applying a different affine transform to each channel.

**Assumption to name:** Those mean/std values are paired with the selected pretrained-weight recipe; arbitrary weights may require another contract.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define offline-safe transfer learning, frozen parameters, and cautious fine-tuning in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Downloading default weights silently, freezing parameters but optimizing all of them, or using training augmentation during validation.

**Debug it deliberately:** Print weight enum/cache path, trainable parameter names/counts, module modes, transform pipeline, class mapping, and one batch shape.

**Stop condition:** Do not fine-tune until the frozen-head baseline, validation transform, and offline/provenance behavior are reproducible.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Load a small image folder with `ImageFolder` and `DataLoader`.

**Verify:** For task `Load a small image folder with ImageFolder and DataLoader`, show the relevant row/group/time identities and assert the training and evaluation information boundaries are disjoint.






2. Train only the classifier head for a few epochs.

**Verify:** For task `Train only the classifier head for a few epochs`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels.






3. Unfreeze the final ResNet block and fine-tune it with a lower learning rate.

**Verify:** For task `Unfreeze the final ResNet block and fine-tune it with a lower learning rate`, demonstrate the concrete requirement “3. Unfreeze the final ResNet block and fine-tune it with a lower learning rate” with explicit inputs, observable output, and one counterexample.







### Progressive hints

1. Use `data/train/<class>/...` and `data/valid/<class>/...`. Resize/crop to the
   expected input size and normalize with the selected weights' documented
   transform. Start with `num_workers=0` for portable notebooks.
2. Pass only `model.fc.parameters()` to the optimizer and record validation loss
   as well as accuracy.
3. Set `requires_grad=True` for `model.layer4`, then use parameter groups: a
   smaller rate for the backbone than for the new head.

The separate solution also demonstrates augmentation and `OneCycleLR`. Add
those only after the head-only and fine-tuning baselines are reproducible.

### Additional mastery practice

Make pretrained weights, image transforms, frozen state, and offline fallback part of one explicit transfer-learning contract.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

4. **Transform mismatch diagnosis:** Compare predictions when validation images use the training transform with random crop/flip versus a deterministic validation transform. Explain the metric instability.
   **Progressive hint:** Augmentation belongs to training. Validation should apply deterministic resize/crop and the normalization expected by the selected weights.

**Verify:** For task `Transform mismatch diagnosis: Compare predictions when validation images use the training tra...`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







5. **Frozen-state edge case:** Freeze a pretrained backbone containing BatchNorm. Explain the difference between `requires_grad=False` and putting frozen modules in evaluation mode.
   **Progressive hint:** requires_grad controls parameter gradients; train/eval controls BatchNorm running statistics and Dropout behavior.

**Verify:** For task `Frozen-state edge case: Freeze a pretrained backbone containing BatchNorm. Explain the differ...`, state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation; then report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels.







6. **Offline fallback design:** Make the lesson runnable when pretrained weights are not cached. Detect cache availability, offer an explicit connected preload step, and provide a tiny randomly initialized CNN smoke path.
   **Progressive hint:** Never trigger an undocumented download. Report whether results use pretrained or random weights because their learning goals differ.

**Verify:** For task `Offline fallback design: Make the lesson runnable when pretrained weights are not cached. Det...`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it; then report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels.






Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.



## Self-check

- Why must preprocessing match the pretrained weights?
- How can you prove that the backbone did not update in phase one?
- Why should fine-tuned layers usually receive a lower learning rate?
- What is the difference between a cached-weight run and `weights=None`?

Expected behavior: the head is the only trainable module in phase one. Unfreezing
`layer4` increases the trainable parameter count substantially.

## Pitfalls, diagnostics, and tradeoffs

| Symptom | Likely cause | Response |
|---|---|---|
| Weight download fails offline | Cache was not prepared | Use cached assets or the labeled `weights=None` fallback |
| Validation accuracy is nonsensical | Class-index mapping differs | Record `ImageFolder.class_to_idx` for both splits |
| CPU run is extremely slow | Dataset/images/model too large | Use a small subset, fewer epochs, and bounded image size |
| Fine-tuning destroys validation performance | Learning rate too high or too many layers unfrozen | Restore checkpoint; unfreeze gradually |
| Windows DataLoader hangs | Multiprocessing from notebook/script | Use `num_workers=0`; add main guard in scripts |

Augmentation can improve robustness but must preserve the label. Horizontal
flips, for example, are inappropriate when left/right orientation defines the
class.

## Next step

- Work in the [Day 48 learner notebook](../notebooks/day48_transfer_learning_cnn.ipynb).
- Then review the
  [Day 48 solution](../solutions/day48_transfer_learning_cnn/day48_solutions.md).
- Continue to [Day 49 — NLP](day49_nlp_basics_hf_spacy.md).

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-48` — Day 48 — Transfer Learning with CNNs.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize offline-safe transfer learning, frozen parameters, and cautious fine-tuning. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day48_transfer_learning_cnn.md`
- learner artifact: `python/ds-60day/notebooks/day48_transfer_learning_cnn.ipynb`

Assume only the prerequisites declared in the guide. Do not open or
quote anything under `solutions/` unless I explicitly ask after an
honest attempt. First explain one concept in plain language and show a
tiny example. Then ask me to predict what happens before I run code.
Give me one bounded task at a time and wait for my code, output, error,
or written reasoning. If I am stuck, reveal only one rung of a
progressive hint ladder at a time.

Run or inspect my learner artifact when safe, distinguish observed
evidence from inference, and help me diagnose tracebacks instead of
replacing my work. Finish with two or three retrieval questions and
one transfer task.

Done when I can explain the core mechanism without notes, complete one
fresh attempt without copied solution code, produce the guide's stated
verification evidence from a clean run, answer the retrieval questions,
and explain how the transfer task changes the assumptions. A cell that
merely ran is not evidence of mastery.
```
