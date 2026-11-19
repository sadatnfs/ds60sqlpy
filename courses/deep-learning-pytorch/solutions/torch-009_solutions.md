# torch-009: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

An epoch is a traversal of selected records; a batch is the set reduced before an update; an optimizer step changes parameters once. These counts differ. Six records with batch size 2 produce three updates per epoch, while batch size 1 produces six. Later batches see weights changed by earlier updates, so equal epochs do not imply equal trajectories. PyTorch also accumulates gradients unless they are cleared, which can accidentally turn a minibatch loop into an unplanned accumulation scheme.

Record IDs should travel with features and targets. A final short batch is retained unless drop_last is explicitly chosen. Its mean loss uses its own number of examples. To report an epoch mean from unequal batches, accumulate loss sums and counts rather than averaging batch means equally. This lesson makes the loop explicit before introducing DataLoader configuration.

**Epoch:** One traversal of the chosen observation set.

**Batch:** The observations contributing to one gradient reduction.

**Gradient reset:** Clearing stored derivatives before an independent update.

## Reading the implementation

Slice the leading observation axis into batches. For each independent update, call `zero_grad(set_to_none=True)`, compute the current mean loss, backward and step. Log parameter values after each step and counts separately from epochs. A shared index permutation preserves x/y pairing. Changing only one side creates a different learning task even when marginal distributions remain unchanged.

## Trace every update at the state where its gradient was computed

Six records with batch size two produce three batches per epoch: IDs [1, 2], [3, 4], [5, 6]. With one optimizer step per batch, one epoch means three updates. At batch size one, the same epoch means six updates. Neither count identifies the resulting parameter trajectory without the data order, loss reduction and learning rate.

For this scalar fixture, \(y=2x\) and each batch mean loss has derivative \(2\operatorname{mean}(x^2)(w-2)\). With learning rate \(\eta=0.01\), the exact correct trajectory is:

| Batch inputs | \(\operatorname{mean}({x}^{2})\) | Weight before | Fresh gradient | Weight after |
| --- | --- | --- | --- | --- |
| [1, 2] | 2.5 | 0 | -10 | 0.1 |
| [3, 4] | 12.5 | 0.1 | -47.5 | 0.575 |
| [5, 6] | 30.5 | 0.575 | -86.925 | 1.44425 |

Each gradient uses the latest weight. Clearing the buffer before each backward ensures that the applied gradient is precisely the one shown in its row. The same records in a different order can yield another trajectory because their local curvature and current parameter state differ.

Without clearing, the first step is still 0.1. The next backward adds -47.5 to the stored -10, giving -57.5, and the second weight becomes 0.675. The final fresh derivative is -80.825, but the accumulated buffer becomes -138.325 and the final weight 2.05825. These are derivatives evaluated at different historical weights. A single constant learning-rate adjustment does not turn this procedure into the intended minibatch algorithm.

Interestingly, the incorrect endpoint happens to lie closer to the known optimum two on this tiny sequence. That does not make the implementation correct. It violated the declared update rule, and another sequence can behave very differently. An acceptance test must inspect the mechanism and state trace rather than reward whichever accidental final training loss is smaller.

Intentional accumulation is different. Hold w fixed, compute each microbatch's contribution to one declared objective, accumulate the scaled gradients, and call step once. For the full six-record mean at \(w=0\), the gradient is 2 \(\operatorname{mean}({x}^{2})\)(-2)=-182/3. One rate 0.01 step gives \(\frac{91}{150}\), about 0.606667. This differs from the three-step minibatch result because it is one update from one fixed state. When microbatch sizes differ, weight each microbatch mean by its participating count divided by the total count.

Metric reporting needs the same denominator discipline. A mean loss two from two records contributes numerator four; mean loss eight from one record contributes numerator eight. The record-weighted mean is (4+8)/3=4, not the unweighted batch-mean average five. But there is another interpretation boundary: losses measured before successive updates belong to different model states. Their weighted average is an online training statistic, not necessarily the loss of the final model. A final-model metric requires a separate fixed-state evaluation pass.

Record identities protect the training population. A shared permutation of x and y preserves y=2x after shuffling. Independently permuting either side changes the prediction task while leaving each marginal array plausible. For five records at batch size two, the tail has one record; dropping it changes which observations participated in the epoch. The loop should retain that decision in its budget and denominator report.

## Exercise 1: Partition with batch size 4

The question is: Partition IDs 1..10 into batches of 4 without dropping the tail.

Ceil(10/4)=3 batches; only the last one is short.

```python
ten = list(range(1, 11))
quads = [ten[i : i + 4] for i in range(0, len(ten), 4)]
assert [len(batch) for batch in quads] == [4, 4, 2] and quads[-1] == [9, 10]
```

**Expected:** batch sizes 4, 4, 2; the last batch is [9, 10].

**Verify:** In a fresh process, the exercise checks confirm `[len(batch) for batch in quads] == [4, 4, 2]` and `quads[-1] == [9, 10]`.

## Exercise 2: Count updates with a dropped tail

The question is: With 10 records, batch size 4 and the short tail dropped, count optimizer steps per epoch and over 3 epochs.

Dropping the tail changes both the step count and which records are ever seen when the order is fixed.

```python
steps_per_epoch = len(ten) // 4
assert (
    steps_per_epoch == 2
    and 3 * steps_per_epoch == 6
    and [i for batch in quads[:steps_per_epoch] for i in batch] == list(range(1, 9))
)
```

**Expected:** 2 steps per epoch and 6 in total; records 9 and 10 never contribute in unshuffled order.

**Verify:** In a fresh process, the exercise checks confirm `steps_per_epoch == 2`; `3 * steps_per_epoch == 6` and `[i for batch in quads[:steps_per_epoch] for i in batch] == list(range(1, 9))`.

## Exercise 3: Trace two single-record updates

The question is: Train w from 0 on x = 1, 2 with y = 2x, batch size 1 and learning rate 0.1, clearing gradients before each step.

The first gradient is 2(0-2)=-4; the second, at \(w=0\).4, is 2(0.8-4)*2=-12.8.

```python
pair_x = torch.tensor([1.0, 2.0], dtype=torch.float64)
pair_y = 2 * pair_x
weight = nn.Parameter(torch.tensor(0.0, dtype=torch.float64))
opt = torch.optim.SGD([weight], lr=0.1)
trace = []
for index in range(2):
    opt.zero_grad(set_to_none=True)
    ((weight * pair_x[index] - pair_y[index]) ** 2).backward()
    opt.step()
    trace.append(weight.item())
np.testing.assert_allclose(trace, [0.4, 1.68], atol=1e-12, rtol=0)
```

**Expected:** weights 0.4 then 1.68.

**Verify:** In a fresh process, the exercise checks confirm `trace` matches `[0.4, 1.68]` within 1e-12.

## Exercise 4: Expose accidental accumulation

The question is: Repeat the loop without zero_grad and compare its final weight with the correct run.

The optimizer applies old derivative contributions again. This is not the same as intentional full-batch accumulation at a fixed parameter state.

```python
bad = nn.Parameter(torch.tensor(0.0, dtype=torch.float64))
bad_optimizer = torch.optim.SGD([bad], lr=0.01)
for start in range(0, 6, 2):
    ((bad * x[start : start + 2] - y[start : start + 2]) ** 2).mean().backward()
    bad_optimizer.step()
assert abs(bad.item() - history[-1]) > 1e-6
```

**Expected:** different endpoint.

**Verify:** In a fresh process, the exercise checks confirm `abs(bad.item() - history[-1]) > 1e-06`.

## Exercise 5: Shuffle paired records together

The question is: Use permutation 5, 0, 4, 1, 3, 2 for both x and y.

A shared identity permutation preserves pairs. Independent shuffles would train on unrelated targets while retaining plausible-looking individual arrays.

```python
order = torch.tensor([5, 0, 4, 1, 3, 2])
sx = x[order]
sy = y[order]
torch.testing.assert_close(sy, 2 * sx, atol=0, rtol=0)
```

**Expected:** every shuffled target equals twice its input.

**Verify:** In a fresh process, the exercise checks confirm `sy` matches `2 * sx` exactly.

## Exercise 6: Aggregate unequal batch means

The question is: Combine mean loss 2 over 2 examples and mean loss 8 over 1 example.

Reconstruct numerators before combining means. This denominator discipline applies to reported metrics as well as gradients.

```python
assert (2 * 2 + 8 * 1) / 3 == 4 and (2 + 8) / 2 == 5
```

**Expected:** epoch mean 4, not 5.

**Verify:** In a fresh process, the exercise checks confirm `(2 * 2 + 8 * 1) / 3 == 4` and `(2 + 8) / 2 == 5`.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
