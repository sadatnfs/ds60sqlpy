# torch-020: explanatory solutions

Open these answers only after attempting Pooling, local augmentation and label invariants yourself. They reuse the guide's literal inputs, starting from Example A, Compare local reductions, so a discrepancy points at one step. The executable companion runs the assertions; this page explains why each one tests Pooling, Augmentation, Label invariance. After a pass, choose a new input for exercise 6, Transform directional labels consistently, without looking.

After comparing, follow the [review steps](../STUDY-GUIDE.md#after-the-solutions).

## Mechanism review

Pooling reduces local spatial information. Max pooling retains the largest response; average pooling uses every entry. Both can make certain perturbations less visible while also discarding potentially useful details. Augmentation changes training inputs under a declared label policy. A horizontal flip may preserve a shape label but reverse a left/right direction label. A transform's availability in a library does not establish its validity for the task.

This lesson uses only torch operations on literal images, not torchvision or a data download. Training transforms and evaluation transforms are separate functions. Evaluation remains deterministic. Random augmentation, when introduced, should use the intended random state and be tested by invariants rather than a hard coded cross-platform mask.

**Pooling:** A local reduction discarding spatial detail.

**Augmentation:** A training transform with a declared target policy.

**Label invariance:** The condition that the target remains valid after a transform.

## Reading the implementation

F.max_pool2d and avg_pool2d operate on NCHW tensors. torch.flip(image, dims=(-1, )) reverses width, and flipping twice restores the original. A training flag or a separate transform object should decide whether augmentation applies. Inspect the label transformation beside the image: geometry alone cannot prove semantic invariance.

## Trace discarded information, gradients and target semantics

For the patch [[1, 3], [2, 4]], max pooling returns 4 and average pooling returns (1+3+2+4)/4=2.5. Now change only the first entry from 1 to 0. The maximum stays 4, while the average becomes 9/4=2.25. The two maps are therefore not interchangeable summaries even though both return one number. Many different patches share the same maximum, so no later layer can reconstruct all discarded values from that output alone.

Consider an upstream derivative \(g=1\) for this one pooled output. With a unique maximum, the max-pool backward route sends one to the selected 4 and zero to the other positions. Average pooling sends \(\frac{1}{4}\) to every entry. This explains the perturbation result locally: a small change to the nonmaximum 1 has zero first-order effect on the max but a quarter-sized effect on the average. Raising 3 past 4 changes the selected maximum, so the derivative route changes at that boundary. At a tie there is no unique ordinary derivative of the max function; do not assume gradients are split equally or use a tied point as a smooth finite-difference oracle.

The worked call uses kernel_size2 and the default stride equal to the kernel size. With overlapping windows, one input can receive contributions from several pooled outputs, so its final gradient sums those routes. Pooling itself has no learned kernel coefficients in these examples. Its effect on training is through the information and derivatives it passes to learned layers.

Padding conventions matter on negative inputs. PyTorch max pooling uses implicit negative infinity for its padding, so a padded location cannot defeat a valid negative maximum. Replacing that with ordinary zero padding would make a patch of negative responses appear to contain a larger zero. For average pooling, count_include_pad and any divisor override affect the denominator near boundaries. The paired TensorFlow worked example uses VALID padding, so none of those boundary differences is exercised there. Match explicit conventions before claiming a padded cross-framework equivalence. [PyTorch 2.9 MaxPool2d](https://docs.pytorch.org/docs/2.9/generated/torch.nn.MaxPool2d.html).

A local pool can be invariant to permutations inside one fixed window, but shifting an image can move values between windows. Max pooling is not a general guarantee that the complete model ignores translations. Stride and window boundaries can discard small features or alias a pattern. Whether that tradeoff helps depends on the task and the downstream representation, not only the smaller tensor shape.

The horizontal flip reverses the width axis, which is the final axis in this NCHW fixture. Applying it twice restores the original pixel arrangement. That proves an involution of indices. It does not prove that the intermediate image retains its label. If the target is a direction, the full transform is (image, label)→(flipped_image, opposite_direction), and applying that full transform twice restores both components. Keeping left while reversing the arrow would manufacture an inconsistent training example.

The same reasoning extends to structured targets. A segmentation mask must use the same geometric transform as its image. A box or keypoint needs its coordinates transformed under the declared origin and pixel convention. A crop can remove the evidence needed for a classification label. A library offering the operation says nothing about whether these task assumptions hold. When augmented siblings come from one original source, keep their family inside the intended training/evaluation split; otherwise a visually altered duplicate can leak source information across the split.

The evaluation exercise adds an ownership promise: return equal values in an independent tensor, so a caller's later mutation cannot alter the source. An identity-valued alias would pass a value comparison and fail that ownership contract. In PyTorch, clone is the relevant explicit storage operation here. TensorFlow's ordinary immutable tensor API has different mutation semantics, so do not infer the same storage promise merely from the paired chapter's identity-valued transformation.

Random training augmentation, when introduced, belongs to the experiment's RNG state. A seeded CPU demonstration is useful reproducibility evidence within its declared environment, not a universal promise of identical random transforms across platforms. Test semantic and geometric invariants and keep the actual sample/seed configuration with the run. Evaluation variation should be intentional and separately described, not accidental training-mode behavior.

## Exercise 1: Pool a new patch

The question is: Pool the patch [[5, -1], [2, 6]] with a 2-by-2 window.

Max keeps one response; average uses all four values, including the negative one.

```python
patch = torch.tensor([[[[5.0, -1.0], [2.0, 6.0]]]])
assert F.max_pool2d(patch, 2).item() == 6 and F.avg_pool2d(patch, 2).item() == 3
```

**Expected:** max 6; average 3.

**Verify:** In a fresh process, the exercise checks confirm `F.max_pool2d(patch, 2).item() == 6` and `F.avg_pool2d(patch, 2).item() == 3`.

## Exercise 2: Flip the height axis instead

The question is: Flip the same patch along the height axis and read its rows.

In NCHW layout dimension -2 is height, so the rows swap while each row keeps its order.

```python
vertical = torch.flip(patch, dims=(-2,))
assert vertical[0, 0].tolist() == [[2.0, 6.0], [5.0, -1.0]]
```

**Expected:** rows [2, 6] and [5, -1].

**Verify:** In a fresh process, the exercise checks confirm `vertical[0, 0].tolist() == [[2.0, 6.0], [5.0, -1.0]]`.

## Exercise 3: Pool a 4-by-4 map

The question is: Apply 2-by-2 max and average pooling to the 4-by-4 map with values 0..15.

Each output summarizes one nonoverlapping window; the bottom-right window is 10, 11, 14, 15.

```python
grid = torch.arange(16.0).reshape(1, 1, 4, 4)
assert F.max_pool2d(grid, 2).tolist() == [[[[5.0, 7.0], [13.0, 15.0]]]] and F.avg_pool2d(
    grid, 2
).tolist() == [[[[2.5, 4.5], [10.5, 12.5]]]]
```

**Expected:** max [[5, 7], [13, 15]]; average [[2.5, 4.5], [10.5, 12.5]].

**Verify:** In a fresh process, the exercise checks confirm `F.max_pool2d(grid, 2).tolist() == [[[[5.0, 7.0], [13.0, 15.0]]]]` and `F.avg_pool2d(grid, 2).tolist() == [[[[2.5, 4.5], [10.5, 12.5]]]]`.

## Exercise 4: Expose discarded information

The question is: Change only the non-maximum pixel 1 to 0 and compare both pools.

The perturbation is invisible to max pooling. That can be useful robustness or harmful information loss, depending on the task.

```python
changed = image.clone()
changed[0, 0, 0, 0] = 0
assert F.max_pool2d(changed, 2).item() == 4 and F.avg_pool2d(changed, 2).item() == 2.25
```

**Expected:** max still 4; average 2.25.

**Verify:** In a fresh process, the exercise checks confirm `F.max_pool2d(changed, 2).item() == 4` and `F.avg_pool2d(changed, 2).item() == 2.25`.

## Exercise 5: Keep evaluation transforms deterministic

The question is: Define a transform that flips only in training and returns an owned copy in evaluation.

A clear branch makes mode behavior reviewable. The owned copy also prevents downstream mutation from changing the original fixture.

```python
def transform(value, training):
    return torch.flip(value, (-1,)) if training else value.clone()


evaluated = transform(image, False)
assert torch.equal(evaluated, image)
evaluated[0, 0, 0, 0] = 99
assert image[0, 0, 0, 0].item() == 1
```

**Expected:** evaluation equals source and does not alias it.

**Verify:** In a fresh process, the exercise checks confirm `torch.equal(evaluated, image)` and `image[0, 0, 0, 0].item() == 1`.

## Exercise 6: Transform directional labels consistently

The question is: Map left to right under horizontal reflection and check the inverse.

A valid augmentation can transform the target rather than preserve it, but that mapping must be explicit. Keeping the left label after a flip would teach contradictory examples.

```python
labels = {"left": "right", "right": "left"}
assert labels["left"] == "right" and labels[labels["left"]] == "left"
```

**Expected:** left->right->left.

**Verify:** In a fresh process, the exercise checks confirm `labels['left'] == 'right'` and `labels[labels['left']] == 'left'`.

