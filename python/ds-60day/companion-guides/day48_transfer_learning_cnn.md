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

## Learner exercises and progressive hints

1. Load a small image folder with `ImageFolder` and `DataLoader`.
2. Train only the classifier head for a few epochs.
3. Unfreeze the final ResNet block and fine-tune it with a lower learning rate.

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
5. **Frozen-state edge case:** Freeze a pretrained backbone containing BatchNorm. Explain the difference between `requires_grad=False` and putting frozen modules in evaluation mode.
   **Progressive hint:** requires_grad controls parameter gradients; train/eval controls BatchNorm running statistics and Dropout behavior.
6. **Offline fallback design:** Make the lesson runnable when pretrained weights are not cached. Detect cache availability, offer an explicit connected preload step, and provide a tiny randomly initialized CNN smoke path.
   **Progressive hint:** Never trigger an undocumented download. Report whether results use pretrained or random weights because their learning goals differ.

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
