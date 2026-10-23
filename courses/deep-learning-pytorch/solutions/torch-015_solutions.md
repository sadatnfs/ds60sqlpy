# torch-015: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Dataset defines how to retrieve an observation, while DataLoader defines batching, sampling and collation. The default collator stacks compatible tensors and groups compatible structures; variable-length records may need a custom collate_fn. A loader's batch count differs from the number of records, and drop_last can omit a tail. Shuffling needs a controlled generator if the ordering itself is part of a reproducible experiment.

This course uses num_workers=0 so all loading occurs in the same process and requires no extra worker startup or shared-memory assumptions. Multiple workers introduce additional random state, serialization, lifetime and platform considerations that need separate testing. A local generator separates sampler randomness from unrelated global random draws. Record IDs remain in each batch so ordering, duplication and pairing can be checked independently of loss.

**DataLoader:** An iterator coordinating sampling, batching and collation over a dataset.

**Collation:** Combining individual observations into a batch structure.

**Sampler generator:** An explicit random-state source controlling sample order.

**Worker count:** The number of separate data-loading processes.

## Reading the implementation

TensorDataset groups tensor components sharing the leading dimension. DataLoader(batch_size=2, shuffle=False, num_workers=0) yields three batches for five records. A seeded torch.Generator supplied to shuffling controls the sampler sequence in this runtime. A custom collator receives a list of items and must return the declared batch structure; it should not perform hidden network or file mutations.

## Exercise 1: Inspect retained batches

The question is: Load five paired ID/value records with batch size 2 and no shuffle.

The loader preserves the final singleton by default. The ID conservation check catches missing or duplicated records that value-only statistics may hide.

```python
dataset=torch.utils.data.TensorDataset(torch.arange(5),torch.arange(1,6,dtype=torch.float32))
loader=torch.utils.data.DataLoader(dataset,batch_size=2,shuffle=False,num_workers=0)
batches=list(loader)
assert [len(ids) for ids,values in batches]==[2,2,1]
assert torch.cat([ids for ids,values in batches]).tolist()==[0,1,2,3,4]
```

**Expected:** sizes2, 2, 1 and IDs0..4 exactly once.

**Verify:** Compare the computed values or written argument with sizes2, 2, 1 and IDs0..4 exactly once.

## Exercise 2: Make dropping explicit

The question is: Set drop_last True on the same fixture.

The policy changes the effective epoch population. It may be useful for fixed shapes, but it must not be described as an identical traversal.

```python
dropped=list(torch.utils.data.DataLoader(dataset,batch_size=2,drop_last=True,num_workers=0))
assert len(dropped)==2 and torch.cat([ids for ids,values in dropped]).tolist()==[0,1,2,3]
```

**Expected:** two batches; ID4 omitted.

**Verify:** Compare the computed values or written argument with two batches; ID4 omitted.

## Exercise 3: Reproduce shuffle with a local generator

The question is: Construct two loaders with fresh generators both seeded7.

A new generator recreates the starting state. Reusing one already-consumed generator would produce a later random sequence rather than a replay.

```python
def order(seed):
    generator=torch.Generator().manual_seed(seed)
    batches=torch.utils.data.DataLoader(dataset,batch_size=2,shuffle=True,generator=generator,num_workers=0)
    return torch.cat([ids for ids,values in batches]).tolist()
assert order(7)==order(7) and sorted(order(7))==list(range(5))
```

**Expected:** same permutation; all five IDs retained.

**Verify:** Compare the computed values or written argument with same permutation; all five IDs retained.

## Exercise 4: Col late variable-length sequences

The question is: Pad sequences[2, 3] and[4] with zero while keeping lengths.

Padding equalize s storage without inventing a valid token. Length metadata is needed for recurrent packing or loss masking later.

```python
padded,lengths=collate([[2,3],[4]])
assert padded.tolist()==[[2,3],[4,0]] and lengths.tolist()==[2,1]
```

**Expected:** batch[[2, 3], [4, 0]] and lengths 2, 1.

**Verify:** Compare the computed values or written argument with batch[[2, 3], [4, 0]] and lengths 2, 1.

## Exercise 5: Preserve pairing after shuffle

The question is: Load values=2*IDs with shuffling and check each batch.

Sampling one joint dataset keeps the components together. Two independently shuffled loaders would not preserve the pairing.

```python
paired=torch.utils.data.TensorDataset(torch.arange(6),2*torch.arange(6))
for ids,targets in torch.utils.data.DataLoader(paired,batch_size=2,shuffle=True,generator=torch.Generator().manual_seed(9),num_workers=0):
    assert torch.equal(targets,2*ids)
```

**Expected:** every target equals twice its ID.

**Verify:** Compare the computed values or written argument with every target equals twice its ID.

## Exercise 6: Reject an empty sequence in this collator

The question is: Pass[[], [1]] to a collator whose contract requires positive lengths.

Some applications can represent empty sequences, but this lesson's recurrent contract cannot. Rejecting the case early keeps an undefined loss denominator from appearing later.

```python
try: collate([[],[1]])
except ValueError: pass
else: raise AssertionError('empty sequence accepted')
```

**Expected:** ValueError before padding.

**Verify:** Compare the computed values or written argument with ValueError before padding.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
