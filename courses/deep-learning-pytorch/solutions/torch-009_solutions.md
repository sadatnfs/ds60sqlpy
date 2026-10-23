# torch-009: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

An epoch is a traversal of selected records; a batch is the set reduced before an update; an optimizer step changes parameters once. These counts differ. Six records with batch size 2 produce three updates per epoch, while batch size 1 produces six. Later batches see weights changed by earlier updates, so equal epochs do not imply equal trajectories. PyTorch also accumulates gradients unless they are clear e d, which can accidentally turn a minibatch loop into an unplanned accumulation scheme.

Record IDs should travel with features and targets. A final short batch is retained unless drop_last is explicitly chosen. Its mean loss uses its own number of examples. To report an epoch mean from unequal batches, accumulate loss sums and counts rather than averaging batch means equally. This lesson makes the loop explicit before introducing DataLoader configuration.

**Epoch:** One traversal of the chosen observation set.

**Batch:** The observations contributing to one gradient reduction.

**Gradient reset:** Clearing stored derivatives before an independent update.

## Reading the implementation

Slice the leading observation axis into batches. For each independent update, call zero_grad(set_to_none=True), compute the current mean loss, backward and step. Log parameter values after each step and counts separately from epochs. A shared index permutation preserves x/y pairing. Changing only one side creates a different learning task even when marginal distributions remain unchanged.

## Exercise 1: Count batches and updates

The question is: Partition IDs1..6 into batches of 2.

The update count is the number of batches when there is one step per batch. It is neither the number of examples nor the number of epochs.

```python
ids=list(range(1,7)); batches=[ids[i:i+2] for i in range(0,len(ids),2)]
assert batches==[[1,2],[3,4],[5,6]]
```

**Expected:** three batches[[1, 2], [3, 4], [5, 6]].

**Verify:** Compare the computed values or written argument with three batches[[1, 2], [3, 4], [5, 6]].

## Exercise 2: Retain a short tail

The question is: Partition five IDs with batch size 2.

Dropping the last singleton would change the effective training set. Record that choice explicitly when fixed batch shapes are required.

```python
short=[list(range(5))[i:i+2] for i in range(0,5,2)]
assert [len(batch) for batch in short]==[2,2,1]
```

**Expected:** batch sizes2, 2, 1.

**Verify:** Compare the computed values or written argument with batch sizes2, 2, 1.

## Exercise 3: Run three independent updates

The question is: Train x1..6, y2x, w0 with batch size 2, rate.01, clearing gradients each batch.

Each derivative is evaluated at the latest weight. Clearing the gradient prevents earlier batches from being counted again accidentally.

```python
x=torch.arange(1,7,dtype=torch.float64); y=2*x; w=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); optimizer=torch.optim.SGD([w],lr=.01); history=[]
for start in range(0,6,2):
    optimizer.zero_grad(set_to_none=True); loss=((w*x[start:start+2]-y[start:start+2])**2).mean(); loss.backward(); optimizer.step(); history.append(w.item())
assert len(history)==3 and np.isfinite(history).all() and len(set(history))==3
```

**Expected:** three finite distinct weights.

**Verify:** Compare the computed values or written argument with three finite distinct weights.

## Exercise 4: Expose accidental accumulation

The question is: Repeat the loop without zero_grad and compare its final weight with the correct run.

The optimizer applies old derivative contributions again. This is not the same as intentional full-batch accumulation at a fixed parameter state.

```python
bad=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); bad_optimizer=torch.optim.SGD([bad],lr=.01)
for start in range(0,6,2):
    ((bad*x[start:start+2]-y[start:start+2])**2).mean().backward(); bad_optimizer.step()
assert abs(bad.item()-history[-1])>1e-6
```

**Expected:** different endpoint.

**Verify:** Compare the computed values or written argument with different endpoint.

## Exercise 5: Shuffle paired records together

The question is: Use permutation5, 0, 4, 1, 3, 2 for both x andy.

A shared identity permutation preserves pairs. Independent shuffles would train on unrelated targets while retaining plausible-looking individual arrays.

```python
order=torch.tensor([5,0,4,1,3,2]); sx=x[order]; sy=y[order]
torch.testing.assert_close(sy,2*sx,atol=0,rtol=0)
```

**Expected:** every shuffled target equals twice its input.

**Verify:** Compare the computed values or written argument with every shuffled target equals twice its input.

## Exercise 6: Aggregate unequal batch means

The question is: Combine mean loss2 over2examples and mean loss8 over1example.

Reconstruct numerators before combining means. This denominator discipline applies to reported metrics as well as gradients.

```python
assert (2*2+8*1)/3==4 and (2+8)/2==5
```

**Expected:** epoch mean4, not5.

**Verify:** Compare the computed values or written argument with epoch mean4, not5.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
