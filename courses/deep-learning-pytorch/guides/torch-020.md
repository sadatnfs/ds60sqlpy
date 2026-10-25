# torch-020: Pooling, local augmentation and label invariants

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-019`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Pooling reduces local spatial information. The central investigation is concrete: Pool patch 1, 3; 2, 4 with a 2-by-2 window. The finish condition is max 4; average 2.5. left->right->left. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Pooling reduces local spatial information. Max pooling retains the largest response; average pooling uses every entry. Both can make certain perturbations less visible while also discarding potentially useful details. Augmentation changes training inputs under a declared label policy. A horizontal flip may preserve a shape label but reverse a left/right direction label. A transform's availability in a library does not establish its validity for the task.

This lesson uses only torch operations on literal images, not torchvision or a data download. Training transforms and evaluation transforms are separate functions. Evaluation remains deterministic. Random augmentation, when introduced, should use the intended random state and be tested by invariants rather than a hard coded cross-platform mask.

## Design decisions and when to use this method

Choose a pooling rule according to which information the next stage should retain. Maximum and average pooling can have the same output shape while preserving different evidence and sending gradients through different input positions. Decide window, stride and padding explicitly when comparing frameworks.

Choose an augmentation only after specifying how every target changes. Classification may justify an invariant label, while direction, coordinates, segmentation masks or bounding boxes often require a corresponding target transform. Keep evaluation deterministic under its declared policy and preserve the exercise's owned-output contract separately from value equality.

## Paired TensorFlow comparison

Compare [tf-020](../../deep-learning-tensorflow/guides/tf-020.md) after deriving the shared numerical contract.

TensorFlow image operations commonly use channels-last layout, while these PyTorch examples use NCHW. The pooling and augmentation semantics are the same only after axis translation. This course does not assume torchvision; all fixtures are literal arrays.

## Vocabulary and concepts

**Pooling:** A local reduction discarding spatial detail.

**Augmentation:** A training transform with a declared target policy.

**Label invariance:** The condition that the target remains valid after a transform.

## How to run this lesson

Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **Deep Learning with PyTorch: tensors to reliable model releases** subject and select `torch-020`. Use its `llm-torch-cpu` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `courses/deep-learning-pytorch/lessons/torch-020.py` under `.learning/expansion/torch-020/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

F.max_pool2d and avg_pool2d operate on NCHW tensors. torch.flip(image, dims=(-1, )) reverses width, and flipping twice restores the original. A training flag or a separate transform object should decide whether augmentation applies. Inspect the label transformation beside the image: geometry alone cannot prove semantic invariance.

## Trace discarded information, gradients and target semantics

For the patch[[1, 3], [2, 4]], max pooling returns 4 and average pooling returns(1+3+2+4)/4=2.5. Now change only the first entry from 1 to 0. The maximum stays 4, while the average becomes 9/4=2.25. The two maps are therefore not interchangeable summaries even though both return one number. Many different patches share the same maximum, so no later layer can reconstruct all discarded values from that output alone.

Consider an upstream derivative \(g=1\) for this one pooled output. With a unique maximum, the max-pool backward route sends one to the selected 4 and zero to the other positions. Average pooling sends \(\frac{1}{4}\) to every entry. This explains the perturbation result locally: a small change to the nonmaximum 1 has zero first-order effect on the max but a quarter-sized effect on the average. Raising 3 past 4 changes the selected maximum, so the derivative route changes at that boundary. At a tie there is no unique ordinary derivative of the max function; do not assume gradients are split equally or use a tied point as a smooth finite-difference oracle.

The worked call uses kernel_size2 and the default stride equal to the kernel size. With overlapping windows, one input can receive contributions from several pooled outputs, so its final gradient sums those routes. Pooling itself has no learned kernel coefficients in these examples. Its effect on training is through the information and derivatives it passes to learned layers.

Padding conventions matter on negative inputs. PyTorch max pooling uses implicit negative infinity for its padding, so a padded location cannot defeat a valid negative maximum. Replacing that with ordinary zero padding would make a patch of negative responses appear to contain a larger zero. For average pooling, count_include_pad and any divisor override affect the denominator near boundaries. The paired TensorFlow worked example uses VALID padding, so none of those boundary differences is exercised there. Match explicit conventions before claiming a padded cross-framework equivalence. [PyTorch 2.9 MaxPool2d](https://docs.pytorch.org/docs/2.9/generated/torch.nn.MaxPool2d.html).

A local pool can be invariant to permutations inside one fixed window, but shifting an image can move values between windows. Max pooling is not a general guarantee that the complete model ignores translations. Stride and window boundaries can discard small features or alias a pattern. Whether that tradeoff helps depends on the task and the downstream representation, not only the smaller tensor shape.

The horizontal flip reverses the width axis, which is the final axis in this NCHW fixture. Applying it twice restores the original pixel arrangement. That proves an involution of indices. It does not prove that the intermediate image retains its label. If the target is a direction, the full transform is(image, label)→(flipped_image, opposite_direction), and applying that full transform twice restores both components. Keeping left while reversing the arrow would manufacture an inconsistent training example.

The same reasoning extends to structured targets. A segmentation mask must use the same geometric transform as its image. A box or keypoint needs its coordinates transformed under the declared origin and pixel convention. A crop can remove the evidence needed for a classification label. A library offering the operation says nothing about whether these task assumptions hold. When augmented siblings come from one original source, keep their family inside the intended training/evaluation split; otherwise a visually altered duplicate can leak source information across the split.

The evaluation exercise adds an ownership promise: return equal values in an independent tensor, so a caller's later mutation cannot alter the source. An identity-valued alias would pass a value comparison and fail that ownership contract. In PyTorch, clone is the relevant explicit storage operation here. TensorFlow's ordinary immutable tensor API has different mutation semantics, so do not infer the same storage promise merely from the paired chapter's identity-valued transformation.

Random training augmentation, when introduced, belongs to the experiment's RNG state. A seeded CPU demonstration is useful reproducibility evidence within its declared environment, not a universal promise of identical random transforms across platforms. Test semantic and geometric invariants and keep the actual sample/seed configuration with the run. Evaluation variation should be intentional and separately described, not accidental training-mode behavior.

## Worked example / walkthrough

### Example A: Compare local reductions

The two operators retain different information despite identical output shape. The average uses all four values while the maximum ignores three smaller ones.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

image=torch.tensor([[[[1.,3.],[2.,4.]]]])
assert F.max_pool2d(image,2).item()==4 and F.avg_pool2d(image,2).item()==2.5
```

**Expected:** max 4; average 2.5.

### Example B: Inspect a horizontal flip

The last axis is the width under NCHW. Flipping the channel or height axis would be a different operation.

```python
flipped=torch.flip(image,dims=(-1,))
assert flipped[0,0].tolist()==[[3.,1.],[4.,2.]]
```

**Expected:** rows 3, 1 and 4, 2.

### Example C: Check the round trip

Reversibility is a useful indexing check, but does not prove the intermediate image has the original semantic label.

```python
assert torch.equal(torch.flip(flipped,dims=(-1,)),image)
```

**Expected:** exact original values.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: max 4; average 2.5. left->right->left. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Compare local reductions.** Pool patch 1, 3; 2, 4 with a 2-by-2 window.
   **Expected:** max 4; average 2.5.
   **Verify:** Save the assertion results for exercise 1, including max 4; average 2.5.

2. **Inspect a horizontal flip.** Flip the width axis and read the pixel s.
   **Expected:** rows 3, 1 and 4, 2.
   **Verify:** Save the assertion results for exercise 2, including rows 3, 1 and 4, 2.

3. **Check the round trip.** Flip the image horizontal l y twice.
   **Expected:** exact original values.
   **Verify:** Save the assertion results for exercise 3, including exact original values.

4. **Expose discarded information.** Change only the non maximum pixel 1 to0 and compare pool s.
   **Expected:** max still 4; average 2.25.
   **Verify:** Save the assertion results for exercise 4, including max still 4; average 2.25.

5. **Keep evaluation transforms deterministic.** Define a transform that flips only in training and returns an owned copy in evaluation.
   **Expected:** evaluation equals source and does not alias it.
   **Verify:** Save the assertion results for exercise 5, including evaluation equals source and does not alias it.

6. **Transform directional labels consistently.** Map left to right under horizontal reflect i on and check the inverse.
   **Expected:** left->right->left.
   **Verify:** Save the assertion results for exercise 6, including left->right->left.

## Common pitfalls and diagnosis

When a pooling result is unexpected, inspect the window coordinates, stride and denominator before changing a model. On negative border values, check whether padding introduced zero where max pooling expected negative infinity. When a gradient differs only at a tied maximum, move to a unique-maximum fixture or explain the nonsmooth convention.

When augmentation improves a score suspiciously, inspect source-family leakage and whether labels were transformed consistently. A flip round trip only verifies indexing. For an evaluation-output ownership test, mutate the returned tensor and verify the source remains unchanged; equality before mutation cannot establish that. Keep geometry, target semantics, randomness and storage ownership as four separate checks.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Pooling, Augmentation, Label invariance using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-019` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

## Interview reasoning with worked answers

**Does a flip round trip prove augmentation validity?**

No. It proves the index operation is reversible. The task label can still change under the intermediate transform.

**Why separate training and evaluation transforms?**

Stochastic training changes are part of the fitting policy. Evaluation needs a declared repeatable policy so score changes are interpretable.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-020, Pooling, local augmentation and label invariants.
Read courses/deep-learning-pytorch/guides/torch-020.md and courses/deep-learning-pytorch/lessons/torch-020.py. Direct prerequisites: `torch-019`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
