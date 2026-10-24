# tf-014: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Multiclass and multilabel prediction answer different questions. In a multiclass task exactly one class is chosen, so a softmax distributes one unit of probability across mutually exclusive outcomes. In a multilabel task several labels may hold at once, so each label gets its own binary decision. A tensor with three outputs does not by itself tell you which task is intended. The target contract determines the activation, loss and denominator. Integer sparse targets name one class index; a vector such as [1,0,1] names two independently present labels. Converting one task into the other changes the meaning of the data.

**Multiclass:** One outcome among mutually exclusive categories.

**Multilabel:** Independent binary outcomes that may coexist.

**Sparse target:** An integer index of the observed class.

## Reading the implementation

Sparse categorical cross entropy takes class indices with shape(batch,), alongside logits shaped(batch,classes). Sigmoid cross entropy instead takes a binary matrix matching logits. Softmax reduces across the class axis. Explicitly check which axes a loss function reduces before comparing mean losses, particularly when multilabel losses are averaged across both labels and examples.

## Exercise 1: Uniform class uncertainty

The question is: Compute sparse cross entropy for target1 and three zero logits.

Three equal scores create a uniform distribution. The target probability is one third, so the negative log likelihood is log3, independent of which class index is chosen.

```python
logits=tf.zeros((1,3)); loss=tf.nn.sparse_softmax_cross_entropy_with_logits(labels=[1],logits=logits)
np.testing.assert_allclose(loss.numpy(),[np.log(3)],atol=1e-6,rtol=0)
```

**Expected:** loss \(\log(3)\).

**Verify:** Compare the computed values or written argument with loss \(\log(3)\).

## Exercise 2: Independent labels

The question is: Calculate sigmoid probabilities for three zero logits and labels[1,0,1].

Independent binary probabilities do not need to sum to one. Forcing a softmax here would make the two present labels compete for probability mass.

```python
probs=tf.math.sigmoid(logits).numpy()
np.testing.assert_array_equal(probs,[[.5,.5,.5]])
assert probs.sum()==1.5
```

**Expected:** three probabilities.5 with total1.5.

**Verify:** Compare the computed values or written argument with three probabilities.5 with total1.5.

## Exercise 3: Contrast target shapes

The question is: Build sparse targets[2,0] and multilabel targets[[1,0,1],[0,1,0]].

A class index is a category identity, not a magnitude. The multilabel row contains three observations of presence. Keeping these shapes explicit prevents unintended broadcasting.

```python
sparse=np.array([2,0],dtype=np.int32); multi=np.array([[1,0,1],[0,1,0]],dtype=np.float32)
assert sparse.shape==(2,) and multi.shape==(2,3)
```

**Expected:** shapes(2,) and(2,3).

**Verify:** Compare the computed values or written argument with shapes(2,) and(2,3).

## Exercise 4: Verify softmax mass

The question is: Apply softmax to[[2,0,-2]] and compare its sum with sigmoid output.

The normalizer in softmax couples categories. Sigmoids do not share a normalizer, which is why changing one logit has different consequences in the two tasks.

```python
z=tf.constant([[2.,0.,-2.]])
np.testing.assert_allclose(tf.nn.softmax(z).numpy().sum(),1,atol=1e-6,rtol=0)
np.testing.assert_allclose(tf.math.sigmoid(z).numpy().sum(),1.5,atol=1e-6,rtol=0)
```

**Expected:** softmax sum1; sigmoid sum1.5.

**Verify:** Compare the computed values or written argument with softmax sum1; sigmoid sum1.5.

## Exercise 5: Choose the denominator

The question is: Compute binary cross entropy for two three-label rows of zero logits; compare sum with entry mean.

There are six binary entries but only two records. A mean per record of summed labels differs from a mean per binary entry by three. State the intended objective instead of comparing unlabelled loss numbers.

```python
losses=tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.constant(multi),logits=tf.zeros((2,3))).numpy()
np.testing.assert_allclose([losses.sum(),losses.mean()],[6*np.log(2),np.log(2)],atol=1e-6,rtol=0)
```

**Expected:** sum6log2; meanlog2.

**Verify:** Compare the computed values or written argument with sum6log2; meanlog2.

## Exercise 6: Reject an impossible class

The question is: Validate a sparse class index before lookup in a three-class vocabulary.

A target index equal to the vocabulary size is out of range. Early validation keeps a category-definition failure distinct from an optimizer failure.

```python
def validate_class(value):
    if not isinstance(value,int) or isinstance(value,bool) or not 0<=value<3: raise ValueError('class index')
    return value
assert validate_class(2)==2
try: validate_class(3)
except ValueError: pass
else: raise AssertionError('accepted unknown class')
```

**Expected:** index3 is outside legal indices0,1,2.

**Verify:** Compare the computed values or written argument with index3 is outside legal indices0,1,2.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
