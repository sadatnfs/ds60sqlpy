# torch-020: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Pooling reduces local spatial information. Max pooling retains the largest response; average pooling uses every entry. Both can make certain perturbations less visible while also discarding potentially useful details. Augmentation changes training inputs under a declared label policy. A horizontal flip may preserve a shape label but reverse a left/right direction label. A transform's availability in a library does not establish its validity for the task.

This lesson uses only torch operations on literal images, not torch vision or a data download. Training transforms and evaluation transforms are separate functions. Evaluation remains deterministic. Random augmentation, when introduced, should use the intended random state and be tested by invariants rather than a hard coded cross-platform mask.

**Pooling:** A local reduction discarding spatial detail.

**Augmentation:** A training transform with a declared target policy.

**Label invariance:** The condition that the target remains valid after a transform.

## Reading the implementation

F.max_pool2d and avg_pool2d operate on NCHW tensors. torch.flip(image, dims=(-1, )) reverses width, and flipping twice restores the original. A training flag or a separate transform object should decide whether augmentation applies. Inspect the label transformation beside the image:geometry alone cannot prove semantic invariance.

## Exercise 1: Compare local reductions

The question is: Pool patch1, 3; 2, 4 with a2x2window.

The two operators retain different information despite identical output shape. The average uses all four values while the maximum ignores three smaller ones.

```python
image=torch.tensor([[[[1.,3.],[2.,4.]]]])
assert F.max_pool2d(image,2).item()==4 and F.avg_pool2d(image,2).item()==2.5
```

**Expected:** max4; average2.5.

**Verify:** Compare the computed values or written argument with max4; average2.5.

## Exercise 2: Inspect a horizontal flip

The question is: Flip the width axis and read the pixel s.

The last axis is the width under NCHW. Flipping the channel or height axis would be a different operation.

```python
flipped=torch.flip(image,dims=(-1,))
assert flipped[0,0].tolist()==[[3.,1.],[4.,2.]]
```

**Expected:** rows3, 1 and4, 2.

**Verify:** Compare the computed values or written argument with rows3, 1 and4, 2.

## Exercise 3: Check the round trip

The question is: Flip the image horizontal l y twice.

Reversibility is a useful indexing check, but does not prove the intermediate image has the original semantic label.

```python
assert torch.equal(torch.flip(flipped,dims=(-1,)),image)
```

**Expected:** exact original values.

**Verify:** Compare the computed values or written argument with exact original values.

## Exercise 4: Expose discarded information

The question is: Change only the non maximum pixel1to0 and compare pool s.

The perturbation is invisible to max pooling. That can be useful robustness or harmful information loss, depending on the task.

```python
changed=image.clone(); changed[0,0,0,0]=0
assert F.max_pool2d(changed,2).item()==4 and F.avg_pool2d(changed,2).item()==2.25
```

**Expected:** max still4; average2.25.

**Verify:** Compare the computed values or written argument with max still4; average2.25.

## Exercise 5: Keep evaluation transforms deterministic

The question is: Define a transform that flips only in training and returns an owned copy in evaluation.

A clear branch makes mode behavior reviewable. The owned copy also prevents downstream mutation from changing the original fixture.

```python
def transform(value,training): return torch.flip(value,(-1,)) if training else value.clone()
evaluated=transform(image,False); assert torch.equal(evaluated,image)
evaluated[0,0,0,0]=99; assert image[0,0,0,0].item()==1
```

**Expected:** evaluation equals source and does not alias it.

**Verify:** Compare the computed values or written argument with evaluation equals source and does not alias it.

## Exercise 6: Transform directional labels consistently

The question is: Map left to right under horizontal reflect i on and check the inverse.

A valid augmentation can transform the target rather than preserve it, but that mapping must be explicit. Keeping the left label after a flip would teach contradictory examples.

```python
labels={'left':'right','right':'left'}
assert labels['left']=='right' and labels[labels['left']]=='left'
```

**Expected:** left->right->left.

**Verify:** Compare the computed values or written argument with left->right->left.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
